import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import sleep

from utils.config_toml import (
    Config,
    LaneGroups,
    TestLaneConfig,
    TestLanesConfig,
    get_config,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ALLURE_RESULTS_DIR = Path("allure-results")


def _reset_directory(path: Path) -> None:
    """Ensure directory exists and remove all existing entries inside it."""
    if path.exists() and not path.is_dir():
        path.unlink()
    path.mkdir(parents=True, exist_ok=True)
    for entry in path.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def pytest_addoption(parser):
    parser.addoption(
        "--user",
        action="store",
        default=None,
        help="Test client name like client01, client02, ...",
    )


@dataclass
class _LaneState:
    lane_id: str
    user: str
    jobs: list[str]
    next_job_index: int = 0
    current_job_index: int | None = None
    current_module: str | None = None
    current_proc: subprocess.Popen | None = None
    waiting_on_user_lock: bool = False


@dataclass
class _JobResult:
    platform: str
    lane_id: str
    user: str
    job_index: int
    module_path: str
    return_code: int


class TestRunner(object):
    """Encapsulates running tests in parallel with pytest."""

    def __init__(
        self,
        *,
        env: str,
        test_lanes: TestLanesConfig | None,
        enable_api: bool,
        enable_web: bool,
        enable_android: bool,
        enable_ios: bool,
        test_case_name: str | None = None,
        enable_reruns: bool = True
    ):
        self.env = env
        self.test_lanes = test_lanes
        self.enable_api = enable_api
        self.enable_web = enable_web
        self.enable_android = enable_android
        self.enable_ios = enable_ios
        self.test_case_name = test_case_name
        self.enable_reruns = enable_reruns

    def run_tests(self) -> list[_JobResult]:
        """
        Run enabled platforms' lanes.
        並行策略：lane 與 lane 並行；每個 lane 內部 jobs 依序執行。
        """
        all_results: list[_JobResult] = []
        plan = [
            (self.enable_api, "api"),
            (self.enable_web, "web"),
            (self.enable_android, "android"),
            (self.enable_ios, "ios"),
        ]
        for enabled, platform in plan:
            if not enabled:
                continue
            # Android/iOS 等待 2 秒（冷啟容錯）
            if platform in ("android", "ios"):
                # _reset_directory(SCREENSHOT_DIR)
                sleep(2)
            lanes = self._get_platform_lanes(platform)
            all_results.extend(self._run_parallel_lanes(lanes=lanes, platform=platform))

        self._log_run_summary(all_results)
        return all_results

    def _get_platform_lanes(self, platform: str) -> list[TestLaneConfig]:
        """Resolve lane config of current env for the given platform."""
        if self.test_lanes is None:
            raise RuntimeError(
                "缺少 test_lanes 設定，無法啟用帳號 lane 調度。"
            )

        all_env_names = ("dev", "prod")
        groups: LaneGroups | None = getattr(self.test_lanes, platform)
        if groups is None:
            return []

        lanes = getattr(groups, self.env, None)
        if lanes is not None:
            return lanes

        available = [
            name for name in all_env_names if getattr(groups, name, None) is not None
        ]
        raise RuntimeError(
            f"無對應 lane 設定：platform={platform} env={self.env} "
            f"(available={available or 'none'})"
        )

    def _run_parallel_lanes(self, lanes: list[TestLaneConfig], platform: str) -> list[_JobResult]:
        """Run lanes in parallel and execute jobs serially within each lane."""
        if not lanes:
            log.info("No lanes configured for platform=%s env=%s", platform, self.env)
            return []

        lane_states = [
            _LaneState(
                lane_id=lane.name or f"{platform}_lane{lane_index + 1:02d}",
                user=lane.user,
                jobs=self._expand_lane_jobs(lane.jobs),
            )
            for lane_index, lane in enumerate(lanes)
        ]
        completed_results: list[_JobResult] = []

        while any(
            state.current_proc is not None or state.next_job_index < len(state.jobs)
            for state in lane_states
        ):
            for state in lane_states:
                if state.current_proc is None and state.next_job_index < len(state.jobs):
                    if self._is_user_busy(state=state, all_states=lane_states):
                        if not state.waiting_on_user_lock:
                            log.info(
                                "Lane wait lane=%s user=%s reason=account_lock",
                                state.lane_id,
                                state.user,
                            )
                            state.waiting_on_user_lock = True
                        continue
                    self._start_next_lane_job(state=state)
                    state.waiting_on_user_lock = False

                proc = state.current_proc
                if proc is None:
                    continue

                return_code = proc.poll()
                if return_code is None:
                    continue

                log.info(
                    "Lane finished lane=%s user=%s job=%s module=%s code=%s",
                    state.lane_id,
                    state.user,
                    state.current_job_index,
                    state.current_module,
                    return_code,
                )
                if (
                    state.current_job_index is not None
                    and state.current_module is not None
                ):
                    completed_results.append(
                        _JobResult(
                            platform=platform,
                            lane_id=state.lane_id,
                            user=state.user,
                            job_index=state.current_job_index,
                            module_path=state.current_module,
                            return_code=return_code,
                        )
                    )
                state.current_proc = None
                state.current_job_index = None
                state.current_module = None
                state.next_job_index += 1

            sleep(0.2)
        return completed_results

    @staticmethod
    def _is_user_busy(state: "_LaneState", all_states: list["_LaneState"]) -> bool:
        """Prevent concurrent jobs for the same user across lanes."""
        return any(
            other is not state and other.user == state.user and other.current_proc is not None
            for other in all_states
        )

    @staticmethod
    def _expand_lane_jobs(job_groups: list[list[str]]) -> list[str]:
        """Flatten lane jobs so each module is executed as an independent pytest command."""
        modules: list[str] = []
        for group in job_groups:
            modules.extend(group)
        return modules

    def _start_next_lane_job(self, state: "_LaneState") -> None:
        """Start next pending job for a lane."""
        if state.next_job_index >= len(state.jobs):
            return

        job_index = state.next_job_index
        module_path = state.jobs[job_index]
        cmd = self._build_pytest_cmd(
            module_path=module_path,
            user=state.user,
        )

        state.current_job_index = job_index + 1
        state.current_module = module_path
        state.current_proc = subprocess.Popen(cmd)
        log.info(
            "Lane start lane=%s user=%s job=%s module=%s",
            state.lane_id,
            state.user,
            state.current_job_index,
            module_path,
        )

    def _build_pytest_cmd(self, module_path: str, user: str) -> list[str]:
        """Build pytest command line for one module process."""
        pytest_args = [
            "-p", "run",
            "-v", "-s", "--tb=short", "--disable-warnings",
            "-m", self.env,
            "--user", user,
            module_path,
            '--alluredir=./allure-results',
        ]
        # Conditionally enable reruns based on config (base.enable_reruns)
        if self.enable_reruns:
            pytest_args.extend(['--reruns=1', '--reruns-delay=2'])
        if self.test_case_name:
            pytest_args.extend(["-k", self.test_case_name])
        return [sys.executable, "-m", "pytest", *pytest_args]

    @staticmethod
    def _log_run_summary(results: list[_JobResult]) -> None:
        total = len(results)
        failed = [item for item in results if item.return_code != 0]
        passed = total - len(failed)
        log.info("Main tests summary total=%s passed=%s failed=%s", total, passed, len(failed))
        for item in failed:
            log.error(
                "Failed job platform=%s lane=%s user=%s module=%s code=%s",
                item.platform,
                item.lane_id,
                item.user,
                item.module_path,
                item.return_code,
            )

    @staticmethod
    def _overall_exit_code(results: list[_JobResult]) -> int:
        """Return 0 only when all jobs passed; otherwise return non-zero."""
        if not results:
            return 0
        non_zero_codes = [item.return_code for item in results if item.return_code != 0]
        if not non_zero_codes:
            return 0
        return max(non_zero_codes)


def main():
    # 獲取配置資料
    common_cfg = get_config(Config)  # 讀 <repo_root>/config/common.toml

    # 清理舊有報告資料
    _reset_directory(ALLURE_RESULTS_DIR)

    # 執行測試
    test_runner = TestRunner(
        env=common_cfg.base.env,
        test_lanes=common_cfg.test_lanes,
        enable_api=common_cfg.base.enable_api,
        enable_web=bool(common_cfg.base.enable_web),
        enable_android=bool(common_cfg.base.enable_android),
        enable_ios=bool(common_cfg.base.enable_ios),
        test_case_name=getattr(
            getattr(common_cfg, 'debug_test_case', None), 'test_case_name', None),
        enable_reruns=common_cfg.debug_test_case.enable_reruns,
    )
    run_results = test_runner.run_tests()
    overall_code = test_runner._overall_exit_code(run_results)
    if overall_code != 0:
        log.error("Main tests finished with failures. overall_exit_code=%s", overall_code)
    else:
        log.info("Main tests finished successfully. overall_exit_code=0")
    raise SystemExit(overall_code)


if __name__ == '__main__':
    main()
