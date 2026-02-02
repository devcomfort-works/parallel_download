"""Core error classes for parallel_download."""

from .download_errors import (
    DownloadError,
    DownloadTimeoutError,
    FileWriteError,
    HTTPError,
    NetworkError,
)
from .extraction_errors import (
    DirectoryPathError,
    FilenameExtractionError,
    NoPathInURLError,
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
