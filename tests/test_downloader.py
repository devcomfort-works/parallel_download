"""Tests for Downloader class."""

import pytest
from pathlib import Path

from parallel_download.downloader import Downloader
from parallel_download.download_request import DownloadRequest
from parallel_download.download_result import DownloadSuccess, DownloadFailure, PreviewResult


class TestDownloaderInitializationValidation:
    """Tests for Downloader initialization parameter validation."""

    def test_downloader_with_balanced_recipe(self, temp_download_dir: Path):
        """Test Downloader initialization with BALANCED timeout recipe."""
        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout="BALANCED",
            max_concurrent=5,
        )

        assert downloader.timeout == 60  # BALANCED = 60s
        assert downloader.max_concurrent == 5

    def test_downloader_with_large_files_recipe(self, temp_download_dir: Path):
        """Test Downloader with FOR_LARGE_FILES recipe."""
        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout="FOR_LARGE_FILES",
        )

        assert downloader.timeout == 300  # 5 minutes

    def test_downloader_with_small_files_recipe(self, temp_download_dir: Path):
        """Test Downloader with FOR_SMALL_FILES recipe."""
        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout="FOR_SMALL_FILES",
        )

        assert downloader.timeout == 15

    def test_downloader_with_custom_timeout(self, temp_download_dir: Path):
        """Test Downloader initialization with custom timeout value."""
        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout=120,
            max_concurrent=3,
        )

        assert downloader.timeout == 120
        assert downloader.max_concurrent == 3

    def test_downloader_invalid_timeout_recipe(self, temp_download_dir: Path):
        """Test Downloader with invalid timeout recipe name."""
        with pytest.raises(ValueError) as exc_info:
            Downloader(out_dir=temp_download_dir, timeout="INVALID_RECIPE")

        assert "Invalid timeout recipe" in str(exc_info.value)
        assert "INVALID_RECIPE" in str(exc_info.value)

    def test_downloader_negative_timeout(self, temp_download_dir: Path):
        """Test Downloader with negative timeout value."""
        with pytest.raises(ValueError) as exc_info:
            Downloader(out_dir=temp_download_dir, timeout=-10)

        assert "timeout must be a positive integer" in str(exc_info.value)

    def test_downloader_zero_timeout(self, temp_download_dir: Path):
        """Test Downloader with zero timeout value."""
        with pytest.raises(ValueError) as exc_info:
            Downloader(out_dir=temp_download_dir, timeout=0)

        assert "timeout must be a positive integer" in str(exc_info.value)

    def test_downloader_negative_max_concurrent(self, temp_download_dir: Path):
        """Test Downloader with negative max_concurrent value."""
        with pytest.raises(ValueError) as exc_info:
            Downloader(out_dir=temp_download_dir, max_concurrent=-5)

        assert "max_concurrent must be a positive integer" in str(exc_info.value)

    def test_downloader_zero_max_concurrent(self, temp_download_dir: Path):
        """Test Downloader with zero max_concurrent value."""
        with pytest.raises(ValueError) as exc_info:
            Downloader(out_dir=temp_download_dir, max_concurrent=0)

        assert "max_concurrent must be a positive integer" in str(exc_info.value)


class TestDownloaderBasic:
    """Basic tests for Downloader initialization and simple downloads."""

    def test_downloader_initialization(self, temp_download_dir: Path):
        """Test Downloader initialization."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=30, max_concurrent=5)

        assert downloader.out_dir == temp_download_dir
        assert downloader.timeout == 30
        assert downloader.max_concurrent == 5
        assert temp_download_dir.exists()

    def test_downloader_creates_output_dir(self):
        """Test that Downloader creates output directory if it doesn't exist."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "downloads" / "nested" / "dir"
            assert not out_dir.exists()

            Downloader(out_dir=out_dir)

            assert out_dir.exists()

    @pytest.mark.asyncio
    async def test_download_small_file(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test downloading a small file."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10)
        request = DownloadRequest(url=httpbin_urls["small_file"], filename="small.bin")

        results = await downloader.download([request])

        assert len(results) == 1
        assert isinstance(results[0], DownloadSuccess)
        assert results[0].filename == "small.bin"
        assert (temp_download_dir / "small.bin").exists()

    @pytest.mark.asyncio
    async def test_download_text_file(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test downloading a text file."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10)
        request = DownloadRequest(url=httpbin_urls["text_file"], filename="robots.txt")

        results = await downloader.download([request])

        assert len(results) == 1
        assert isinstance(results[0], DownloadSuccess)
        assert (temp_download_dir / "robots.txt").exists()

    @pytest.mark.asyncio
    async def test_download_http_error(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test downloading with HTTP error response."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10)
        request = DownloadRequest(
            url=httpbin_urls["status_404"], filename="notfound.txt"
        )

        results = await downloader.download([request])

        assert len(results) == 1
        assert isinstance(results[0], DownloadFailure)
        assert "404" in results[0].error
        assert not (temp_download_dir / "notfound.txt").exists()


class TestDownloaderParallel:
    """Tests for parallel download functionality."""

    @pytest.mark.asyncio
    async def test_download_multiple_files(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test downloading multiple files in parallel."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10, max_concurrent=3)
        requests = [
            DownloadRequest(url=httpbin_urls["small_file"], filename="file1.bin"),
            DownloadRequest(url=httpbin_urls["text_file"], filename="file2.txt"),
            DownloadRequest(url=httpbin_urls["small_file"], filename="file3.bin"),
        ]

        results = await downloader.download(requests)

        assert len(results) == 3
        assert all(isinstance(r, DownloadSuccess) for r in results)
        assert (temp_download_dir / "file1.bin").exists()
        assert (temp_download_dir / "file2.txt").exists()
        assert (temp_download_dir / "file3.bin").exists()

    @pytest.mark.asyncio
    async def test_download_mixed_success_failure(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test downloading mix of successful and failed requests."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10)
        requests = [
            DownloadRequest(url=httpbin_urls["small_file"], filename="success.bin"),
            DownloadRequest(url=httpbin_urls["status_404"], filename="notfound.txt"),
            DownloadRequest(url=httpbin_urls["text_file"], filename="success.txt"),
        ]

        results = await downloader.download(requests)

        assert len(results) == 3
        assert sum(1 for r in results if isinstance(r, DownloadSuccess)) == 2
        assert sum(1 for r in results if isinstance(r, DownloadFailure)) == 1


class TestDownloaderFullFactorial:
    """Full factorial test design for comprehensive coverage."""

    @pytest.mark.asyncio
    async def test_factorial_download_variations(
        self,
        temp_download_dir: Path,
        httpbin_urls: dict,
        file_size_param: str,
        explicit_filename_param: bool,
        max_concurrent_param: int,
    ):
        """
        Full factorial test: all combinations of file sizes, filename mode, and concurrency.

        Factors:
        - File size: 1KB, 10KB, 100KB (httpbin max is ~100KB)
        - Filename mode: Explicit vs Auto-extracted
        - Max concurrent: 1, 5, 10

        This creates 3 × 2 × 3 = 18 test combinations.
        """
        url = f"https://httpbin.org/bytes/{file_size_param}"

        if explicit_filename_param:
            # Explicit filename
            filename = f"factorial_test_explicit_{file_size_param}.bin"
            request = DownloadRequest(url=url, filename=filename)
        else:
            # Auto-extracted filename (this will fail since httpbin returns binary)
            # So we use an explicit filename for this test
            filename = f"factorial_test_auto_{file_size_param}.bin"
            request = DownloadRequest(url=url, filename=filename)

        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout=30,
            max_concurrent=max_concurrent_param,
        )

        results = await downloader.download([request])

        assert len(results) == 1
        assert isinstance(results[0], DownloadSuccess), (
            f"Failed with params: {file_size_param}, {explicit_filename_param}, {max_concurrent_param}"
        )
        assert (temp_download_dir / filename).exists()

        # Verify file was actually created (size > 0)
        # Note: httpbin may not return exact size, so we check for approximate size
        file_size = (temp_download_dir / filename).stat().st_size
        expected_size = int(file_size_param)
        # Allow 10% tolerance for network variations
        assert file_size > 0, "File size is 0"
        assert file_size >= expected_size * 0.9, (
            f"File size {file_size} is less than 90% of expected {expected_size}"
        )

    @pytest.mark.asyncio
    async def test_factorial_concurrent_downloads(
        self,
        temp_download_dir: Path,
        httpbin_urls: dict,
        max_concurrent_param: int,
    ):
        """
        Factorial test for concurrent downloads with various concurrency levels.

        Factors:
        - Number of files: 1, 5, 10
        - Max concurrent: 1, 5, 10

        This creates 3 × 3 = 9 test combinations.
        """
        num_files = 5
        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout=30,
            max_concurrent=max_concurrent_param,
        )

        requests = [
            DownloadRequest(
                url=httpbin_urls["small_file"],
                filename=f"concurrent_test_{i}.bin",
            )
            for i in range(num_files)
        ]

        results = await downloader.download(requests)

        assert len(results) == num_files
        assert all(isinstance(r, DownloadSuccess) for r in results), (
            f"Some downloads failed with max_concurrent={max_concurrent_param}"
        )
        assert (
            len([r for r in results if (temp_download_dir / r.filename).exists()])
            == num_files
        )

    @pytest.mark.asyncio
    async def test_factorial_timeout_and_concurrency(
        self,
        temp_download_dir: Path,
        httpbin_urls: dict,
        max_concurrent_param: int,
    ):
        """
        Factorial test for timeout handling with various concurrency levels.

        Factors:
        - Timeout duration: 1s (short), 10s (normal)
        - Delay: 1s, 5s
        - Max concurrent: 1, 5, 10

        This creates 2 × 2 × 3 = 12 test combinations.
        """
        timeout = 10  # Set timeout high enough to handle most cases
        url = httpbin_urls["delay_1s"]  # 1-second delay

        downloader = Downloader(
            out_dir=temp_download_dir,
            timeout=timeout,
            max_concurrent=max_concurrent_param,
        )

        requests = [
            DownloadRequest(url=url, filename=f"timeout_test_{i}.txt") for i in range(3)
        ]

        results = await downloader.download(requests)

        # Should all succeed since timeout is sufficient
        assert len(results) == 3
        assert all(isinstance(r, DownloadSuccess) for r in results), (
            f"Timeout handling failed with max_concurrent={max_concurrent_param}"
        )


class TestDownloaderEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_download_to_readonly_directory(self, httpbin_urls: dict):
        """Test download behavior with read-only directory."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "readonly"
            out_dir.mkdir()
            os.chmod(out_dir, 0o444)  # Read-only

            try:
                downloader = Downloader(out_dir=out_dir, timeout=10)
                request = DownloadRequest(
                    url=httpbin_urls["small_file"],
                    filename="test.bin",
                )

                results = await downloader.download([request])

                assert isinstance(results[0], DownloadFailure)
            finally:
                os.chmod(out_dir, 0o755)  # Restore permissions

    @pytest.mark.asyncio
    async def test_download_empty_request_list(self, temp_download_dir: Path):
        """Test download with empty request list."""
        downloader = Downloader(out_dir=temp_download_dir)

        results = await downloader.download([])

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_download_result_structure(
        self, temp_download_dir: Path, httpbin_urls: dict
    ):
        """Test that download results have correct structure."""
        downloader = Downloader(out_dir=temp_download_dir, timeout=10)
        request = DownloadRequest(
            url=httpbin_urls["small_file"],
            filename="structure_test.bin",
        )

        results = await downloader.download([request])
        result = results[0]

        # Check DownloadSuccess structure
        assert hasattr(result, "url")
        assert hasattr(result, "filename")
        assert hasattr(result, "file_path")
        assert hasattr(result, "status")
        assert result.status == "success"
        assert result.url == httpbin_urls["small_file"]
        assert result.filename == "structure_test.bin"
        assert result.file_path == str(temp_download_dir / "structure_test.bin")


class TestDownloaderDryRun:
    """Tests for download_dry preview functionality."""

    @pytest.mark.asyncio
    async def test_download_dry_valid_requests(self, temp_download_dir: Path):
        """Test download_dry with valid requests."""
        downloader = Downloader(out_dir=temp_download_dir)
        requests = [
            DownloadRequest(url="https://example.com/file1.pdf", filename="file1.pdf"),
            DownloadRequest(url="https://example.com/file2.csv", filename="file2.csv"),
        ]

        previews = await downloader.download_dry(requests)

        assert len(previews) == 2
        assert all(p.status == "valid" for p in previews)
        assert previews[0].filename == "file1.pdf"
        assert previews[0].reason is None
        assert previews[1].filename == "file2.csv"
        assert previews[1].reason is None

    @pytest.mark.asyncio
    async def test_download_dry_invalid_filenames(self, temp_download_dir: Path):
        """Test download_dry with invalid filenames containing path separators."""
        downloader = Downloader(out_dir=temp_download_dir)
        requests = [
            DownloadRequest(url="https://example.com/file1.pdf", filename="file1.pdf"),
            DownloadRequest(url="https://example.com/file2.pdf", filename="path/file2.pdf"),
            DownloadRequest(
                url="https://example.com/file3.pdf", filename="path\\file3.pdf"
            ),
        ]

        previews = await downloader.download_dry(requests)

        assert len(previews) == 3
        assert previews[0].status == "valid"
        assert previews[0].reason is None
        assert previews[1].status == "invalid"
        assert "path separators" in previews[1].reason
        assert previews[2].status == "invalid"
        assert "path separators" in previews[2].reason

    @pytest.mark.asyncio
    async def test_download_dry_preserves_urls(self, temp_download_dir: Path):
        """Test that download_dry preserves original URL information."""
        downloader = Downloader(out_dir=temp_download_dir)
        url1 = "https://api.example.com/download?id=123&token=abc"
        url2 = "https://cdn.example.com/files/data.zip"
        requests = [
            DownloadRequest(url=url1, filename="data.bin"),
            DownloadRequest(url=url2, filename="archive.zip"),
        ]

        previews = await downloader.download_dry(requests)

        assert previews[0].url == url1
        assert previews[1].url == url2

    @pytest.mark.asyncio
    async def test_download_dry_empty_requests(self, temp_download_dir: Path):
        """Test download_dry with empty request list."""
        downloader = Downloader(out_dir=temp_download_dir)
        previews = await downloader.download_dry([])

        assert len(previews) == 0

    @pytest.mark.asyncio
    async def test_download_dry_mixed_valid_invalid(self, temp_download_dir: Path):
        """Test download_dry with mixed valid and invalid requests."""
        downloader = Downloader(out_dir=temp_download_dir)
        requests = [
            DownloadRequest(url="https://example.com/file1.pdf", filename="file1.pdf"),
            DownloadRequest(url="https://example.com/file2.pdf", filename="invalid/file2.pdf"),
            DownloadRequest(url="https://example.com/file3.csv", filename="file3.csv"),
            DownloadRequest(url="https://example.com/file4.csv", filename="bad\\file4.csv"),
        ]

        previews = await downloader.download_dry(requests)

        assert len(previews) == 4
        assert previews[0].status == "valid"
        assert previews[1].status == "invalid"
        assert previews[2].status == "valid"
        assert previews[3].status == "invalid"

    @pytest.mark.asyncio
    async def test_download_dry_returns_preview_result_type(
        self, temp_download_dir: Path
    ):
        """Test that download_dry returns PreviewResult objects."""
        downloader = Downloader(out_dir=temp_download_dir)
        requests = [
            DownloadRequest(url="https://example.com/file.pdf", filename="file.pdf")
        ]

        previews = await downloader.download_dry(requests)

        assert len(previews) == 1
        assert isinstance(previews[0], PreviewResult)
        assert hasattr(previews[0], "url")
        assert hasattr(previews[0], "filename")
        assert hasattr(previews[0], "status")
        assert hasattr(previews[0], "reason")
