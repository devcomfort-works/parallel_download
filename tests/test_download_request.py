"""
Tests for DownloadRequest model and filename extraction.
DownloadRequest 모델 및 파일명 추출에 대한 테스트입니다.
"""

import pytest

from parallel_download.errors import (
    DirectoryPathError,
    NoPathInURLError,
)
from parallel_download.models import DownloadRequest
from parallel_download.url_processor import extract_filename_from_url


class TestDownloadRequestNormalization:
    """
    Tests for DownloadRequest model input normalization.
    DownloadRequest 모델 입력 정규화에 대한 테스트입니다.
    """

    def test_explicit_filename(self):
        """
        Test DownloadRequest with explicit filename.
        명시적인 파일명이 있는 DownloadRequest를 테스트합니다.
        """
        url = "https://example.com/data"
        filename = "myfile.pdf"
        req = DownloadRequest(url=url, filename=filename)  # type: ignore

        assert str(req.url) == url
        assert req.filename == filename

    def test_auto_extract_simple_filename(self):
        """
        Test automatic filename extraction from simple URL.
        단순 URL에서 자동 파일명 추출을 테스트합니다.
        Pydantic DownloadRequest instantiation triggers normalization.
        """
        url = "https://example.com/documents/report.pdf"
        # Passing string to DownloadRequest constructor is not standard Pydantic.
        # But we can pass dict or use model_validate if we want to simulate robust input.
        # However, DownloadRequest(url=url) is the standard usage.
        req = DownloadRequest(url=url)  # type: ignore

        assert req.filename == "report.pdf"

    def test_override_auto_extracted_filename(self):
        """
        Test overriding auto-extracted filename with explicit one.
        자동 추출된 파일명을 명시적인 파일명으로 재정의하는 것을 테스트합니다.
        """
        url = "https://example.com/auto_name.pdf"
        override_filename = "custom_name.pdf"
        req = DownloadRequest(url=url, filename=override_filename)  # type: ignore

        assert req.filename == override_filename


class TestFilenameExtractionLogic:
    """
    Tests for direct filename extraction logic (using extract_filename_from_url).
    직접 파일명 추출 로직에 대한 테스트입니다.
    """

    def test_extract_with_query_string(self):
        """
        Test filename extraction ignores query string.
        파일명 추출 시 쿼리 스트링이 무시되는지 테스트합니다.
        """
        url = "https://example.com/files/data.csv?token=abc123"
        filename = extract_filename_from_url(url)
        assert filename == "data.csv"

    def test_extract_url_encoded_filename(self):
        """
        Test URL-decoded filename extraction.
        URL 인코딩된 파일명 추출을 테스트합니다.
        """
        url = "https://example.com/files/my%20document.pdf"
        filename = extract_filename_from_url(url)
        assert filename == "my document.pdf"

    def test_extract_no_extension(self):
        """
        Test automatic filename extraction without extension.
        확장자가 없는 파일명 자동 추출을 테스트합니다.
        """
        url = "https://example.com/files/README"
        filename = extract_filename_from_url(url)
        assert filename == "README"

    def test_extract_with_spaces(self):
        """
        Test automatic filename extraction with spaces.
        공백이 포함된 파일명 자동 추출을 테스트합니다.
        """
        url = "https://example.com/files/my%20document"
        filename = extract_filename_from_url(url)
        assert filename == "my document"

    @pytest.mark.parametrize(
        "url,expected_filename",
        [
            ("https://example.com/a/b/c/file.txt", "file.txt"),
            ("https://example.com/file.tar.gz", "file.tar.gz"),
            ("https://example.com/file.backup.2024.zip", "file.backup.2024.zip"),
            ("https://example.com/path/to/deep/nested/file.pdf", "file.pdf"),
            ("https://example.com/file.pdf?v=1&token=xyz", "file.pdf"),
            ("https://example.com/file.pdf#section", "file.pdf"),
            ("https://example.com/file.pdf?v=1#section", "file.pdf"),
        ],
    )
    def test_various_url_patterns(self, url: str, expected_filename: str):
        """
        Test filename extraction from various URL patterns.
        다양한 URL 패턴에서 파일명 추출을 테스트합니다.
        """
        assert extract_filename_from_url(url) == expected_filename


class TestFilenameExtractionErrors:
    """
    Tests for error scenarios in filename extraction.
    파일명 추출 시 오류 시나리오에 대한 테스트입니다.
    """

    def test_error_no_path(self):
        """
        Test error when URL has no path.
        URL에 경로가 없을 때의 오류를 테스트합니다.
        """
        url = "https://example.com"
        with pytest.raises(NoPathInURLError):
            extract_filename_from_url(url)

    def test_error_directory_path(self):
        """
        Test error when URL path is a directory.
        URL 경로가 디렉토리일 때의 오류를 테스트합니다.
        """
        url = "https://example.com/files/"
        with pytest.raises(DirectoryPathError):
            extract_filename_from_url(url)

    @pytest.mark.parametrize(
        "url,error_type",
        [
            ("https://example.com", NoPathInURLError),
            ("https://example.com/", DirectoryPathError),
            ("https://example.com/path/", DirectoryPathError),
        ],
    )
    def test_various_error_cases(self, url: str, error_type):
        """
        Test various error cases for filename extraction.
        파일명 추출에 대한 다양한 오류 사례를 테스트합니다.
        """
        with pytest.raises(error_type):
            extract_filename_from_url(url)

    def test_request_wraps_extraction_error(self):
        """
        Test that DownloadRequest model validation raises proper extraction errors.
        DownloadRequest 모델 검증이 적절한 추출 오류를 발생시키는지 테스트합니다.
        """
        # Note: Pydantic wrapping behavior check
        url = "https://example.com/"  # Directory extraction error

        # We expect DirectoryPathError directly as it bubbles up from validation
        with pytest.raises(DirectoryPathError):
            DownloadRequest(url=url)  # type: ignore
