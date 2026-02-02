"""Core error classes for parallel_download."""

from .extraction_errors import (
    FilenameExtractionError,
    NoPathInURLError,
    DirectoryPathError,
)
from .download_errors import (
    DownloadError,
    HTTPError,
    DownloadTimeoutError,
    NetworkError,
    FileWriteError,
)
from .validation_errors import (
    BulkValidationError,
)

__all__ = [
    "FilenameExtractionError",
    "NoPathInURLError",
    "DirectoryPathError",
    "DownloadError",
    "HTTPError",
    "DownloadTimeoutError",
    "NetworkError",
    "FileWriteError",
    "ValidationErrorDetail",
    "BulkValidationError",
]
