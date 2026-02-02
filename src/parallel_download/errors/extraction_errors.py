"""Filename extraction related errors."""


class FilenameExtractionError(Exception):
    """
    Base exception for errors occurring during filename extraction from URLs.
    URL에서 파일명을 추출하는 동안 발생하는 에러의 기본 예외 클래스입니다.
    """

    pass


class NoPathInURLError(FilenameExtractionError):
    """
    Raised when the URL contains only a domain (root) without a specific file path.
    URL에 구체적인 파일 경로 없이 도메인(루트)만 포함된 경우 발생합니다.
    """

    def __init__(self, url: str):
        super().__init__(f"Could not extract filename from URL (no path found): {url}")


class DirectoryPathError(FilenameExtractionError):
    """
    Raised when the URL path ends with a slash '/', indicating a directory rather than a file.
    URL 경로가 슬래시 '/'로 끝나 파일이 아닌 디렉토리를 나타내는 경우 발생합니다.
    """

    def __init__(self, url: str):
        super().__init__(f"URL path points to a directory, not a file: {url}")
