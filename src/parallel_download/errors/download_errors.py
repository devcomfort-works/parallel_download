"""Download operation related errors."""


class DownloadError(Exception):
    """
    Base exception for all download-related failures in the library.
    라이브러리 내 모든 다운로드 관련 실패에 대한 기본 예외 클래스입니다.
    """

    pass


class HTTPError(DownloadError):
    """
    Raised when the server returns a non-success HTTP status code (4xx or 5xx).
    서버가 비정상적인 HTTP 상태 코드(4xx 또는 5xx)를 반환할 때 발생합니다.

    Attributes
    ----------
    url : str
        The target URL that failed.
    status_code : int
        The HTTP status code received (e.g., 404, 500).
    """

    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        super().__init__(
            f"HTTP download failed with status {status_code} for URL: {url}"
        )


class DownloadTimeoutError(DownloadError):
    """
    Raised when the download operation exceeds the specified timeout limit.
    다운로드 작업이 지정된 시간 제한을 초과했을 때 발생합니다.

    Attributes
    ----------
    url : str
        The URL of the request that timed out.
    timeout : int
        The configured timeout limit in seconds.
    """

    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        super().__init__(f"Download timed out after {timeout} seconds for URL: {url}")


class NetworkError(DownloadError):
    """
    Raised when a low-level network issue (DNS failure, connection reset, etc.) occurs.
    저수준 네트워크 문제(DNS 실패, 연결 초기화 등)가 발생했을 때 발생합니다.

    Attributes
    ----------
    url : str
        The URL involved in the network failure.
    original_error : Exception
        The underlying exception usually from aiohttp or asyncio.
    """

    def __init__(self, url: str, original_error: Exception):
        self.url = url
        self.original_error = original_error
        super().__init__(
            f"Network error occurred while downloading {url}: {original_error}"
        )


class FileWriteError(DownloadError):
    """
    Raised when saving the downloaded content to disk fails.
    다운로드된 콘텐츠를 디스크에 저장하는 데 실패했을 때 발생합니다.

    Attributes
    ----------
    filename : str
        The destination filename that could not be written.
    original_error : Exception
        The file system exception (e.g., PermissionError, IOError).
    """

    def __init__(self, filename: str, original_error: Exception):
        self.filename = filename
        self.original_error = original_error
        super().__init__(f"Failed to write data to file '{filename}': {original_error}")
