from pathlib import Path
from urllib.parse import unquote, urlparse

from ..errors import DirectoryPathError, NoPathInURLError


def extract_filename_from_url(url: str) -> str:
    """
    Extract the filename from the URL.
    URL에서 파일명을 추출합니다.

    Parameters
    ----------
    url : str
        The URL to extract the filename from.
        파일명이 포함된 URL입니다.

    Returns
    -------
    str
        The extracted filename.
        추출된 파일명입니다.

    Raises
    ------
    NoPathInURLError
        If the URL has no path information or the filename is empty.
        URL에 경로 정보가 없거나 파일명이 비어있는 경우 발생합니다.
    DirectoryPathError
        If the URL path points to a directory.
        URL 경로가 디렉토리를 가리키는 경우 발생합니다.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path

    if not path:
        raise NoPathInURLError(url)
    if path.endswith("/"):
        raise DirectoryPathError(url)

    filename = Path(path).name
    if not filename:
        raise NoPathInURLError(url)

    return unquote(filename)
