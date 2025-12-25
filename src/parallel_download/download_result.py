from dataclasses import dataclass
from typing import Union, Literal


@dataclass
class DownloadResult:
    """
    Base class for download operation results.

    Attributes
    ----------
    url : str
        The URL that was downloaded.
    filename : str
        The target filename for the download.
    status : Literal["success", "failed"]
        The status of the download operation.
    """

    url: str
    filename: str
    status: Literal["success", "failed"]


@dataclass
class DownloadSuccess(DownloadResult):
    """
    Represents a successful download operation.

    Attributes
    ----------
    url : str
        The URL that was downloaded.
    filename : str
        The target filename for the download.
    status : Literal["success"]
        Always "success" for successful downloads.
    file_path : str
        The full path where the file was saved.
    """

    status: Literal["success"] = "success"
    file_path: str = ""

    def __post_init__(self):
        """Ensure file_path is provided after initialization."""
        if not self.file_path:
            raise ValueError("file_path must be provided for DownloadSuccess")


@dataclass
class DownloadFailure(DownloadResult):
    """
    Represents a failed download operation.

    Attributes
    ----------
    url : str
        The URL that failed to download.
    filename : str
        The intended filename for the download.
    status : Literal["failed"]
        Always "failed" for failed downloads.
    error : str
        Error message describing why the download failed.
    """

    status: Literal["failed"] = "failed"
    error: str = ""

    def __post_init__(self):
        """Ensure error is provided after initialization."""
        if not self.error:
            raise ValueError("error must be provided for DownloadFailure")


@dataclass
class PreviewResult:
    """
    Preview result for download request validation.

    Represents the validation status of a download request without
    performing actual download operations.

    Attributes
    ----------
    url : str
        The URL to be downloaded.
    filename : str
        The target filename for the download.
    status : Literal["valid", "invalid"]
        The validation status of the request.
    reason : str, optional
        Error message if status is "invalid". None if valid.
    """

    url: str
    filename: str
    status: Literal["valid", "invalid"]
    reason: str | None = None


# Type alias for download result
DownloadResultType = Union[DownloadSuccess, DownloadFailure]
