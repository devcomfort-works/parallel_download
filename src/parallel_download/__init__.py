"""Parallel Download - Concurrent file downloader using asyncio and aiohttp."""

from .downloader import Downloader
from .download_request import DownloadRequest
from .download_result import DownloadSuccess, DownloadFailure, DownloadResultType, PreviewResult
from .config import TimeoutRecipe, DownloadConfig, DOWNLOAD_RECIPES
from .errors import (
    FilenameExtractionError,
    NoPathInURLError,
    DirectoryPathError,
    DownloadError,
    HTTPError,
    DownloadTimeoutError,
    NetworkError,
    FileWriteError,
)

__all__ = [
    # Core classes
    "Downloader",
    "DownloadRequest",
    "DownloadSuccess",
    "DownloadFailure",
    "DownloadResultType",
    "PreviewResult",
    # Configuration
    "TimeoutRecipe",
    "DownloadConfig",
    "DOWNLOAD_RECIPES",
    # Errors
    "FilenameExtractionError",
    "NoPathInURLError",
    "DirectoryPathError",
    "DownloadError",
    "HTTPError",
    "DownloadTimeoutError",
    "NetworkError",
    "FileWriteError",
]
