"""Custom exception classes for parallel_download package."""


class FilenameExtractionError(Exception):
    """
    Base exception for filename extraction errors.

    Raised when a filename cannot be extracted from a URL.
    """

    pass


class NoPathInURLError(FilenameExtractionError):
    """
    Raised when URL has no path information.

    This occurs when the URL lacks a path component,
    making it impossible to extract a filename.
    """

    pass


class DirectoryPathError(FilenameExtractionError):
    """
    Raised when URL path points to a directory.

    This occurs when the URL path ends with a slash (/),
    indicating a directory rather than a file.
    """

    pass


class DownloadError(Exception):
    """
    Base exception for download-related errors.

    Raised when a download fails for any reason.
    """

    pass


class HTTPError(DownloadError):
    """
    Raised when HTTP request returns a non-2xx status code.

    Attributes
    ----------
    url : str
        The URL that failed to download.
    status_code : int
        The HTTP status code returned by the server.
    """

    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        super().__init__(f"HTTP {status_code} error while downloading from {url}")


class DownloadTimeoutError(DownloadError):
    """
    Raised when a download request times out.

    Attributes
    ----------
    url : str
        The URL that timed out.
    timeout : int
        The timeout duration in seconds.
    """

    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        super().__init__(f"Download from {url} timed out after {timeout} seconds")


class NetworkError(DownloadError):
    """
    Raised when a network error occurs during download.

    Attributes
    ----------
    url : str
        The URL that encountered network error.
    original_error : Exception
        The original exception from aiohttp.
    """

    def __init__(self, url: str, original_error: Exception):
        self.url = url
        self.original_error = original_error
        super().__init__(f"Network error downloading from {url}: {str(original_error)}")


class FileWriteError(DownloadError):
    """
    Raised when a file write error occurs.

    Attributes
    ----------
    filename : str
        The filename that failed to write.
    original_error : Exception
        The original exception from the file system.
    """

    def __init__(self, filename: str, original_error: Exception):
        self.filename = filename
        self.original_error = original_error
        super().__init__(f"Failed to write file {filename}: {str(original_error)}")
