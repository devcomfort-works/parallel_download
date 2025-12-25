from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, unquote
from pathlib import Path

from .errors import (
    NoPathInURLError,
    DirectoryPathError,
)


@dataclass
class DownloadRequest:
    url: str  # pydantic으로 이관하여, url 형식 검사를 하도록 처리
    filename: Optional[str] = None

    def __post_init__(self):
        # filename이 없으면 url에서 추출
        if self.filename is None:
            self.filename = self._extract_filename_from_url()

    def _can_extract_filename(self) -> bool:
        """
        Check if a filename can be extracted from the URL.

        Returns
        -------
        bool
            True if filename can be extracted, False otherwise.
        """
        parsed_url = urlparse(self.url)
        path = parsed_url.path

        # path is empty or points to a directory
        if not path or path.endswith("/"):
            return False

        # extract filename part
        filename = Path(path).name

        # filename is empty
        if not filename:
            return False

        return True

    def _extract_filename_from_url(self) -> str:
        """
        Extract filename from the URL.

        Returns
        -------
        str
            Extracted filename.

        Raises
        ------
        NoPathInURLError
            If the URL has no path information.
        DirectoryPathError
            If the URL path points to a directory.
        """
        if not self._can_extract_filename():
            parsed_url = urlparse(self.url)
            path = parsed_url.path

            # Provide detailed reason for each case
            if not path:
                raise NoPathInURLError(
                    f"Cannot extract filename from URL: no path information. URL: {self.url}"
                )
            elif path.endswith("/"):
                raise DirectoryPathError(
                    f"Cannot extract filename from URL: path points to a directory. URL: {self.url}"
                )

        # Extract filename after URL decoding
        parsed_url = urlparse(self.url)
        filename = Path(parsed_url.path).name
        filename = unquote(filename)

        return filename
