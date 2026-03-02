"""
DownloadRequest 입력 정규화와 URL 파일명 추출 규칙을 검증한다.

주요 범위:
- DownloadRequest 검증/정규화
- URL 기반 파일명 추출 성공/실패 케이스
- 관련 예외 및 에러 객체 계약
"""

import pytest

from parallel_download.errors import (
    BulkValidationError,
    DirectoryPathError,
    DownloadTimeoutError,
    FileWriteError,
    HTTPError,
    NetworkError,
    NoPathInURLError,
)
from parallel_download.models import DownloadRequest
from parallel_download.models.request import normalize_request
from parallel_download.url_processor import extract_filename_from_url


class TestBulkValidationError:
    """배치 검증 예외(BulkValidationError)의 기본 계약을 검증한다."""

    def test_bulk_validation_error_creation(self):
        """Test BulkValidationError can be instantiated and raised."""
        errors = [ValueError("Invalid URL"), ValueError("Missing filename")]
        with pytest.raises(BulkValidationError) as exc_info:
            raise BulkValidationError("Batch validation failed", errors)

        assert len(exc_info.value.exceptions) == 2
        assert "Batch validation failed" in str(exc_info.value)


class TestDownloadErrors:
    """다운로드 에러 객체들이 메타데이터를 보존하는지 검증한다."""

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
    """URL 인코딩/특수문자 환경에서 파일명 추출 규칙을 검증한다."""

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
    """DownloadRequest model validator의 입력 정규화/오류 처리를 검증한다."""

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
        original_req = DownloadRequest.model_validate("https://example.com/file.txt")
        result = normalize_request(original_req)
        assert result is original_req  # Should return same object


class TestDownloadRequestModelValidatorRemaining:
    """validator의 보조 오류 경로를 추가 검증한다."""

    def test_normalize_request_with_invalid_input_type(self):
        """Test normalize_request with unsupported input type"""
        with pytest.raises(TypeError, match="Unsupported input type"):
            DownloadRequest.model_validate(123)  # Pass an integer instead of supported types


class TestDownloadRequestNormalization:
    """
    DownloadRequest 생성 시 입력이 어떻게 정규화되는지 검증한다.

    - 명시적 filename 우선
    - URL 기반 자동 filename 추출
    - 자동 추출값 오버라이드
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
    `extract_filename_from_url`의 정상 추출 규칙을 검증한다.

    쿼리/프래그먼트 무시, URL decode, 다양한 경로 패턴을 포함한다.
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
    파일명을 추출할 수 없는 URL 입력에 대한 오류 경로를 검증한다.

    경로 없음, 디렉터리 경로, 모델 검증 단계 전파를 포함한다.
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
    """`normalize_request()`가 다양한 입력 타입을 일관된 모델로 변환하는지 검증한다."""

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
    """`RequestParser.parse()`가 단일 입력(str/dict)도 허용하는지 검증한다."""

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
