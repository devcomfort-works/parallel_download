"""Tests for DownloadRequest class."""

import pytest

from parallel_download.download_request import DownloadRequest
from parallel_download.errors import (
    NoPathInURLError,
    DirectoryPathError,
)


class TestDownloadRequestBasic:
    """Basic tests for DownloadRequest initialization and core functionality."""

    def test_explicit_filename(self):
        """Test DownloadRequest with explicit filename."""
        url = "https://example.com/data"
        filename = "myfile.pdf"
        req = DownloadRequest(url=url, filename=filename)

        assert req.url == url
        assert req.filename == filename

    def test_auto_extract_simple_filename(self):
        """Test automatic filename extraction from simple URL."""
        url = "https://example.com/documents/report.pdf"
        req = DownloadRequest(url=url)

        assert req.filename == "report.pdf"

    def test_override_auto_extracted_filename(self):
        """Test overriding auto-extracted filename with explicit one."""
        url = "https://example.com/auto_name.pdf"
        override_filename = "custom_name.pdf"
        req = DownloadRequest(url=url, filename=override_filename)

        assert req.filename == override_filename


class TestDownloadRequestExtraction:
    """Tests for various URL extraction scenarios and special cases."""

    def test_auto_extract_with_query_string(self):
        """Test filename extraction ignores query string."""
        url = "https://example.com/files/data.csv?token=abc123"
        req = DownloadRequest(url=url)

        assert req.filename == "data.csv"

    def test_auto_extract_url_encoded_filename(self):
        """Test URL-decoded filename extraction."""
        url = "https://example.com/files/my%20document.pdf"
        req = DownloadRequest(url=url)

        assert req.filename == "my document.pdf"

    def test_auto_extract_no_extension(self):
        """Test automatic filename extraction without extension (like README)."""
        url = "https://example.com/files/README"
        req = DownloadRequest(url=url)

        assert req.filename == "README"

    def test_auto_extract_with_spaces(self):
        """Test automatic filename extraction with spaces in name."""
        url = "https://example.com/files/my%20document"
        req = DownloadRequest(url=url)

        assert req.filename == "my document"

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
        """Test filename extraction from various URL patterns."""
        req = DownloadRequest(url=url)
        assert req.filename == expected_filename


class TestDownloadRequestErrorHandling:
    """Tests for error scenarios and edge cases."""

    def test_error_no_path(self):
        """Test error when URL has no path."""
        url = "https://example.com"

        with pytest.raises(NoPathInURLError):
            DownloadRequest(url=url)

    def test_error_directory_path(self):
        """Test error when URL path is a directory."""
        url = "https://example.com/files/"

        with pytest.raises(DirectoryPathError):
            DownloadRequest(url=url)

    @pytest.mark.parametrize(
        "url,error_type",
        [
            ("https://example.com", NoPathInURLError),
            ("https://example.com/", DirectoryPathError),
            ("https://example.com/path/", DirectoryPathError),
        ],
    )
    def test_various_error_cases(self, url: str, error_type):
        """Test various error cases for filename extraction."""
        with pytest.raises(error_type):
            DownloadRequest(url=url)


class TestDownloadRequestInternalLogic:
    """Tests for internal _can_extract_filename method behavior."""

    def test_can_extract_simple_file(self):
        """Test that simple file URL can be extracted."""
        req = DownloadRequest(url="https://example.com/file.pdf", filename="dummy.pdf")
        assert req._can_extract_filename() is True

    def test_cannot_extract_no_path(self):
        """Test that URL without path cannot be extracted."""
        req = DownloadRequest(url="https://example.com", filename="dummy.pdf")
        assert req._can_extract_filename() is False

    def test_cannot_extract_directory(self):
        """Test that directory path cannot be extracted."""
        req = DownloadRequest(url="https://example.com/files/", filename="dummy.pdf")
        assert req._can_extract_filename() is False

    def test_can_extract_no_extension(self):
        """Test that filename without extension can be extracted."""
        req = DownloadRequest(url="https://example.com/README", filename="dummy.pdf")
        assert req._can_extract_filename() is True
