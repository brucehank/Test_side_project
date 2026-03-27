from dataclasses import dataclass


@dataclass(frozen=True)
class ContentData:
    modality: str
    content_id: str
    contentType: str
    auto_adjust: bool | None = None


PROGRAM_CONTENT_CASE: list[ContentData] = [
    ContentData(
        modality="TREADMILL",
        content_id="3c25de4e-4856-11ea-b77f-2e728ce88125",
        contentType="CONSOLE_MANUAL_TREAD",
        auto_adjust=False,
    ),
    ContentData(
        modality="TREADMILL",
        content_id="aff31268-695f-11ea-bc55-0242ac130003",
        contentType="CONSOLE_CANNED_TREAD",
        auto_adjust=True,
    ),
    ContentData(
        modality="MAX_TRAINER",
        content_id="939449ae-b71f-43e0-8be8-6035c564663d",
        contentType="CONSOLE_MANUAL_MAX",
        auto_adjust=False,
    ),
    ContentData(
        modality="MAX_TRAINER",
        content_id="003ac964-b414-466c-b689-d49b3728dbbc",
        contentType="CONSOLE_CANNED_MAX",
        auto_adjust=False,
    ),
    ContentData(
        modality="ELLIPTICAL",
        content_id="d28c878e-0237-4634-86e4-8838724d3640",
        contentType="CONSOLE_MANUAL_ELLIPTICAL",
        auto_adjust=False,
    ),
    ContentData(
        modality="ELLIPTICAL",
        content_id="bb280254-7398-4a1d-9460-e2d45954dde4",
        contentType="CONSOLE_CANNED_ELLIPTICAL",
        auto_adjust=True,
    ),
    ContentData(
        modality="BIKE",
        content_id="074166b2-47ac-11ea-b77f-2e728ce88125",
        contentType="CONSOLE_MANUAL_BIKE",
        auto_adjust=False,
    ),
    ContentData(
        modality="UPRIGHT_BIKE",
        content_id="074166b2-47ac-11ea-b77f-2e728ce88125",
        contentType="CONSOLE_MANUAL_BIKE",
        auto_adjust=False,
    ),
    ContentData(
        modality="UPRIGHT_BIKE",
        content_id="9d5810cc-d525-44ce-b471-b057a3198e91",
        contentType="CONSOLE_CANNED_BIKE_NON_FLYWHEEL",
        auto_adjust=True,
    ),
    ContentData(
        modality="RECUMBENT_BIKE",
        content_id="074166b2-47ac-11ea-b77f-2e728ce88125",
        contentType="CONSOLE_MANUAL_BIKE",
        auto_adjust=False,
    ),
    ContentData(
        modality="RECUMBENT_BIKE",
        content_id="f325aa03-5661-43a7-861b-3311b499e3c3",
        contentType="CONSOLE_CANNED_BIKE_NON_FLYWHEEL",
        auto_adjust=True,
    ),
]
