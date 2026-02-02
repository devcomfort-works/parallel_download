from .request import DownloadInput, DownloadRequest
from .result import (
    DownloadFailure,
    DownloadResult,
    DownloadResultType,
    DownloadSuccess,
)

__all__ = [
    "DownloadRequest",
    "DownloadInput",
    "DownloadSuccess",
    "DownloadFailure",
    "DownloadResultType",
    "DownloadResult",
]
