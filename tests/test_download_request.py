"""
Tests for DownloadRequest model and filename extraction.
DownloadRequest 모델 및 파일명 추출에 대한 테스트입니다.
"""

import asyncio
import pytest
from unittest.mock import patch
from exceptiongroup import ExceptionGroup

from parallel_download.errors import (
    BulkValidationError,
    DirectoryPathError,
    NoPathInURLError,
    HTTPError,
    DownloadTimeoutError,
    NetworkError,
    FileWriteError,
)
from parallel_download.models import DownloadRequest
from parallel_download.models.request import normalize_request
from parallel_download.url_processor import extract_filename_from_url


class TestBulkValidationError:
    """Test BulkValidationError coverage for validation_errors.py"""

    def test_bulk_validation_error_creation(self):
        """Test BulkValidationError can be instantiated and raised."""
        errors = [ValueError("Invalid URL"), ValueError("Missing filename")]
        with pytest.raises(BulkValidationError) as exc_info:
            raise BulkValidationError("Batch validation failed", errors)

        assert len(exc_info.value.exceptions) == 2
        assert "Batch validation failed" in str(exc_info.value)


class TestDownloadErrors:
    """Test coverage for download_errors.py"""

    def test_http_error_creation(self):
        """Test HTTPError can be instantiated."""
        error = HTTPError("https://example.com", 404)
        assert error.url == "https://example.com"
        assert error.status_code == 404
        assert "404" in str(error)

    def test_download_timeout_error_creation(self):
        """Test DownloadTimeoutError can be instantiated."""
        error = DownloadTimeoutError("https://example.com", 30)
        assert error.url == "https://example.com"
        assert error.timeout == 30
        assert "30" in str(error)

    def test_network_error_creation(self):
        """Test NetworkError can be instantiated."""
        original_error = ConnectionError("Connection failed")
        error = NetworkError("https://example.com", original_error)
        assert error.url == "https://example.com"
        assert error.original_error == original_error
        assert "Connection failed" in str(error)

    def test_file_write_error_creation(self):
        """Test FileWriteError can be instantiated."""
        original_error = PermissionError("Permission denied")
        error = FileWriteError("test.txt", original_error)
        assert error.filename == "test.txt"
        assert error.original_error == original_error
        assert "Permission denied" in str(error)


class TestExtractFilenameFromUrlCoverage:
    """Test coverage for extract_filename_from_url.py"""

    def test_extract_filename_with_url_encoded_characters(self):
        """Test extract_filename_from_url with URL-encoded characters"""
        from parallel_download.url_processor.extract_filename_from_url import (
            extract_filename_from_url,
        )

        # Test with URL-encoded filename
        url = "https://example.com/path/to/my%20file%20with%20spaces.pdf"
        filename = extract_filename_from_url(url)
        assert filename == "my file with spaces.pdf"

    def test_extract_filename_with_special_characters(self):
        """Test extract_filename_from_url with special characters"""
        from parallel_download.url_processor.extract_filename_from_url import (
            extract_filename_from_url,
        )

        # Test with special characters that are valid in URLs
        url = "https://example.com/path/to/file-with_special.chars%2Bmore.pdf"
        filename = extract_filename_from_url(url)
        assert filename == "file-with_special.chars+more.pdf"


class TestDownloadRequestModelValidator:
    """Test coverage for DownloadRequest model validator"""

    def test_normalize_request_with_dict_missing_url(self):
        """Test normalize_request with dict missing url raises ValueError"""
        with pytest.raises(ValueError, match="Dictionary input must contain 'url' key"):
            DownloadRequest.model_validate({})

    def test_normalize_request_with_invalid_type(self):
        """Test normalize_request with invalid type raises TypeError"""
        with pytest.raises(TypeError, match="Unsupported input type"):
            DownloadRequest.model_validate(123)

    def test_normalize_request_function_with_request_object(self):
        """Test normalize_request function with DownloadRequest object"""
        original_req = DownloadRequest(url="https://example.com/file.txt")
        result = normalize_request(original_req)
        assert result is original_req  # Should return same object


class TestDownloadRequestModelValidatorRemaining:
    """Test remaining coverage for DownloadRequest model validator"""

    def test_normalize_request_with_invalid_input_type(self):
        """Test normalize_request with unsupported input type"""
        with pytest.raises(TypeError, match="Unsupported input type"):
            DownloadRequest.model_validate(123)  # Pass an integer instead of supported types


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


class TestNormalizeRequestFunction:
    """Tests for normalize_request() function with non-DownloadRequest inputs."""

    def test_normalize_request_with_string(self):
        """Test normalize_request with a plain URL string."""
        result = normalize_request("https://example.com/file.zip")
        assert isinstance(result, DownloadRequest)
        assert result.filename == "file.zip"

    def test_normalize_request_with_dict(self):
        """Test normalize_request with a dict input."""
        result = normalize_request({"url": "https://example.com/data.csv"})
        assert isinstance(result, DownloadRequest)
        assert result.filename == "data.csv"

    def test_normalize_request_with_dict_and_filename(self):
        """Test normalize_request with a dict containing explicit filename."""
        result = normalize_request({"url": "https://example.com/data", "filename": "custom.csv"})
        assert isinstance(result, DownloadRequest)
        assert result.filename == "custom.csv"


class TestRequestParserSingleInput:
    """Tests for RequestParser.parse() with single (non-list) input."""

    def test_parse_single_string_input(self):
        """Test parse() accepts a single string instead of a list."""
        from parallel_download.url_processor import RequestParser

        parser = RequestParser()
        result = parser.parse("https://example.com/file.pdf")
        assert len(result) == 1
        assert result[0].filename == "file.pdf"

    def test_parse_single_dict_input(self):
        """Test parse() accepts a single dict instead of a list."""
        from parallel_download.url_processor import RequestParser

        parser = RequestParser()
        result = parser.parse({"url": "https://example.com/report.pdf"})
        assert len(result) == 1
        assert result[0].filename == "report.pdf"
