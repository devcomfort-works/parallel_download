# parallel-download

A high-performance, type-safe parallel file downloader using asyncio and aiohttp.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-77%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## ✨ Features

- 🚀 **Concurrent Downloads**: Download multiple files in parallel with configurable concurrency limits using asyncio
- 🎯 **Recipe-Based Configuration**: Predefined timeout recipes (`FOR_LARGE_FILES`, `BALANCED`, `FOR_SMALL_FILES`) optimized for different scenarios
- 📁 **Automatic Filename Extraction**: Auto-extract filenames from URLs with URL-decoding support. Raises explicit errors on invalid URLs (no path, directory paths, empty filenames) to prevent silent failures. This design ensures data traceability and forces developers to make explicit decisions, avoiding hidden bugs in automated workflows.
- 🛡️ **Type-Safe**: Full type hints with Literal types for better IDE support and compile-time checks
- 📊 **Structured Results**: Detailed result objects (`DownloadSuccess`, `DownloadFailure`) for precise error handling
- ⚡ **Semaphore-Based Control**: Prevent resource exhaustion with configurable concurrent download limits
- ✅ **Comprehensive Testing**: 77 tests covering all edge cases and error scenarios
- 🔍 **Detailed Error Handling**: Custom exception classes with meaningful error messages

## 📦 Installation

### Using rye (recommended)

```bash
rye add parallel-download
```

### Using pip

```bash
pip install parallel-download
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from pathlib import Path
from parallel_download import Downloader, DownloadRequest

async def main():
    # Create downloader with BALANCED timeout (60 seconds)
    downloader = Downloader(
        out_dir=Path("./downloads"),
        timeout="BALANCED",
        max_concurrent=5
    )
    
    # Create download requests
    requests = [
        DownloadRequest(
            url="https://example.com/file1.pdf",
            filename="file1.pdf"
        ),
        DownloadRequest(
            url="https://example.com/file2.pdf",
            filename="file2.pdf"
        ),
    ]
    
    # Download in parallel
    results = await downloader.download(requests)
    
    # Process results
    for result in results:
        if result.status == "success":
            print(f"✓ Downloaded: {result.filename} to {result.file_path}")
        else:
            print(f"✗ Failed: {result.filename} - {result.error}")

asyncio.run(main())
```

### Automatic Filename Extraction

The library extracts filenames from URLs automatically, but raises explicit errors for invalid cases. This design ensures data integrity and traceability.

#### ✅ Valid Cases (Automatically Extracted)

```python
from parallel_download import DownloadRequest

# Simple filename extraction
request = DownloadRequest(url="https://example.com/documents/report.pdf")
print(request.filename)  # Output: report.pdf

# URL-encoded filenames are decoded
request = DownloadRequest(url="https://example.com/files/my%20document.pdf")
print(request.filename)  # Output: my document.pdf

# Multiple dots in filename
request = DownloadRequest(url="https://example.com/archive.backup.2024.tar.gz")
print(request.filename)  # Output: archive.backup.2024.tar.gz
```

#### ❌ Invalid Cases (Explicit Errors Required)

The following cases raise errors to force explicit handling:

```python
from parallel_download import DownloadRequest
from parallel_download.errors import NoPathInURLError, DirectoryPathError

# No path in URL - raises NoPathInURLError
# Prevents silent failures in bulk operations
try:
    request = DownloadRequest(url="https://example.com")
except NoPathInURLError as e:
    print(f"Must provide explicit filename: {e}")

# Directory path (ends with /) - raises DirectoryPathError
# Ensures you don't accidentally treat directories as files
try:
    request = DownloadRequest(url="https://example.com/data/")
except DirectoryPathError as e:
    print(f"Use explicit filename for directory URLs: {e}")

# Workaround: Provide explicit filename
request = DownloadRequest(url="https://example.com/data/", filename="data.zip")
print(request.filename)  # Output: data.zip
```

#### Design Philosophy

**Why explicit errors instead of silent defaults?**

1. **Data Traceability**: Researchers and developers need to know exactly where files came from
2. **Prevents Hidden Bugs**: Auto-generating filenames like `download_123.bin` masks the original source
3. **Explicit Intention**: Forces developers to consider each edge case in batch operations
4. **Safer Workflows**: Errors fail fast in automated systems instead of creating cryptic output filenames

## 📖 Usage Guide

### Timeout Recipes

Choose the appropriate recipe based on your file sizes:

#### FOR_LARGE_FILES (300 seconds / 5 minutes)
Use for downloading large files (several GB to tens of GB):
```python
downloader = Downloader(
    out_dir=Path("./large_files"),
    timeout="FOR_LARGE_FILES",  # 300s
    max_concurrent=3
)
```

#### BALANCED (60 seconds / 1 minute)
Default recipe for mixed file sizes:
```python
downloader = Downloader(
    out_dir=Path("./downloads"),
    timeout="BALANCED",  # 60s (default)
    max_concurrent=5     # (default)
)
```

#### FOR_SMALL_FILES (15 seconds)
Use for downloading small files (KB-MB range):
```python
downloader = Downloader(
    out_dir=Path("./small_files"),
    timeout="FOR_SMALL_FILES",  # 15s
    max_concurrent=10
)
```

### Custom Timeout Values

Specify timeout in seconds directly:
```python
downloader = Downloader(
    out_dir=Path("./downloads"),
    timeout=120,         # 2 minutes
    max_concurrent=7
)
```

### Error Handling

Handle different error scenarios with custom exceptions:

```python
from parallel_download import (
    Downloader,
    DownloadRequest,
    DownloadSuccess,
    DownloadFailure,
    HTTPError,
    DownloadTimeoutError,
    NetworkError,
)

async def download_with_error_handling():
    downloader = Downloader(out_dir=Path("./downloads"))
    
    requests = [
        DownloadRequest(url="https://example.com/file.pdf", filename="file.pdf"),
    ]
    
    results = await downloader.download(requests)
    
    for result in results:
        if isinstance(result, DownloadSuccess):
            print(f"Downloaded: {result.file_path}")
        elif isinstance(result, DownloadFailure):
            error_msg = result.error
            if "HTTP 404" in error_msg:
                print(f"File not found: {result.url}")
            elif "timeout" in error_msg.lower():
                print(f"Download timed out: {result.url}")
            else:
                print(f"Download failed: {error_msg}")
```

## 🔌 API Reference

### Downloader

Main class for parallel downloads.

```python
class Downloader:
    def __init__(
        self,
        out_dir: Path,
        timeout: Literal["FOR_LARGE_FILES", "BALANCED", "FOR_SMALL_FILES"] | int = "BALANCED",
        max_concurrent: int = 5,
    ) -> None:
        """
        Initialize the parallel downloader.
        
        Args:
            out_dir: Output directory for downloaded files
            timeout: Timeout recipe or seconds (must be positive)
            max_concurrent: Maximum concurrent downloads (must be positive)
            
        Raises:
            ValueError: If timeout or max_concurrent are invalid
        """
    
    async def download(
        self, 
        requests: Iterable[DownloadRequest]
    ) -> list[DownloadSuccess | DownloadFailure]:
        """
        Download files in parallel.
        
        Args:
            requests: Iterable of DownloadRequest objects
            
        Returns:
            List of download results (success or failure)
        """
```

### DownloadRequest

Request object for a single file download.

```python
@dataclass
class DownloadRequest:
    url: str                      # Download URL
    filename: Optional[str] = None # Target filename (auto-extracted if None)
    
    # Raises:
    # - NoPathInURLError: If URL has no path
    # - DirectoryPathError: If URL path is a directory
```

### Download Results

#### DownloadSuccess

```python
@dataclass
class DownloadSuccess:
    url: str              # Source URL
    filename: str         # Target filename
    file_path: str        # Full path to downloaded file
    status: Literal["success"] = "success"
```

#### DownloadFailure

```python
@dataclass
class DownloadFailure:
    url: str              # Source URL
    filename: str         # Target filename
    error: str            # Error message
    status: Literal["failed"] = "failed"
```

### Custom Exceptions

```python
class FilenameExtractionError(Exception)
    """Base exception for filename extraction errors"""

class NoPathInURLError(FilenameExtractionError)
    """URL has no path information"""

class DirectoryPathError(FilenameExtractionError)
    """URL path points to a directory"""

class DownloadError(Exception)
    """Base exception for download errors"""

class HTTPError(DownloadError)
    """HTTP request returned non-2xx status"""

class DownloadTimeoutError(DownloadError)
    """Download request timed out"""

class NetworkError(DownloadError)
    """Network error during download"""

class FileWriteError(DownloadError)
    """Error writing file to disk"""
```

## 📚 Examples

### Download Multiple Files with Progress Tracking

```python
import asyncio
from pathlib import Path
from parallel_download import Downloader, DownloadRequest, DownloadSuccess, DownloadFailure

async def download_with_progress():
    downloader = Downloader(
        out_dir=Path("./downloads"),
        timeout="BALANCED",
        max_concurrent=5
    )
    
    urls = [
        ("https://example.com/file1.pdf", "file1.pdf"),
        ("https://example.com/file2.pdf", "file2.pdf"),
        ("https://example.com/file3.pdf", "file3.pdf"),
    ]
    
    requests = [
        DownloadRequest(url=url, filename=filename)
        for url, filename in urls
    ]
    
    results = await downloader.download(requests)
    
    # Summary
    successes = [r for r in results if isinstance(r, DownloadSuccess)]
    failures = [r for r in results if isinstance(r, DownloadFailure)]
    
    print(f"\n✓ Downloaded: {len(successes)}/{len(results)}")
    if failures:
        print(f"✗ Failed: {len(failures)}")
        for failure in failures:
            print(f"  - {failure.filename}: {failure.error}")

asyncio.run(download_with_progress())
```

### Batch Processing with Recipe Selection

```python
async def batch_download(file_size_category: str):
    # Select recipe based on file size
    recipe_map = {
        "small": "FOR_SMALL_FILES",
        "medium": "BALANCED",
        "large": "FOR_LARGE_FILES",
    }
    
    downloader = Downloader(
        out_dir=Path(f"./downloads/{file_size_category}"),
        timeout=recipe_map[file_size_category],
    )
    
    requests = [
        DownloadRequest(url=f"https://example.com/{i}.bin", filename=f"file_{i}.bin")
        for i in range(10)
    ]
    
    results = await downloader.download(requests)
    return results

# Download large files with optimized settings
asyncio.run(batch_download("large"))
```

### Error Recovery with Retry Logic

```python
from parallel_download import NetworkError, HTTPError

async def download_with_retry(url: str, filename: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            downloader = Downloader(out_dir=Path("./downloads"))
            result = (await downloader.download([
                DownloadRequest(url=url, filename=filename)
            ]))[0]
            
            if isinstance(result, DownloadSuccess):
                return result
            
            # Retry on network errors
            if "Network error" in result.error or "timeout" in result.error.lower():
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retry in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
            
            raise Exception(f"Download failed: {result.error}")
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}")

asyncio.run(download_with_retry("https://example.com/file.pdf", "file.pdf"))
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/parallel-download.git
cd parallel-download

# Sync with rye
rye sync

# Activate virtual environment (optional)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Running Tests

```bash
# Run all tests
rye run pytest

# Run specific test file
rye run pytest tests/test_downloader.py

# Run with coverage
rye run pytest --cov=src/parallel_download

# Run specific test class
rye run pytest tests/test_downloader.py::TestDownloaderInitializationValidation

# Run tests in verbose mode
rye run pytest -vv
```

### Test Coverage

The project includes 77 comprehensive tests:
- **23 tests** for `DownloadRequest` (filename extraction, URL parsing, error handling)
- **9 tests** for `Downloader` initialization validation (recipe validation, parameter checks)
- **45 tests** for `Downloader` functionality (basic downloads, parallel downloads, full-factorial tests, edge cases)

### Code Quality

```bash
# Format code with black
rye run black src tests

# Check style with flake8
rye run flake8 src tests

# Type check with mypy
rye run mypy src
```

### Project Structure

```
parallel-download/
├── src/parallel_download/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Timeout recipe definitions
│   ├── downloader.py         # Main Downloader class
│   ├── download_request.py   # DownloadRequest dataclass
│   ├── download_result.py    # Result dataclasses
│   ├── errors.py             # Custom exceptions
│   └── utils.py              # Utility functions
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_downloader.py   # Downloader tests
│   ├── test_download_request.py # DownloadRequest tests
│   └── test_utils.py        # Utils tests
├── examples/                # Example scripts
│   ├── __init__.py
│   └── download_dry_preview.py  # dry_run preview with tabulate
├── pyproject.toml           # Project configuration
├── README.md               # This file
└── TESTING.md              # Testing guide
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests to ensure everything passes
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📚 Examples

### Preview Downloads with dry_run

The library provides a `download_dry` method to preview downloads without performing actual HTTP requests. This is useful for validating requests before batch downloads.

**Example with tabulate output:**

```python
import asyncio
from pathlib import Path
from parallel_download import Downloader, DownloadRequest
from tabulate import tabulate

async def preview_downloads():
    downloader = Downloader(out_dir=Path("./downloads"))
    
    requests = [
        DownloadRequest(url="https://example.com/file1.pdf", filename="file1.pdf"),
        DownloadRequest(url="https://example.com/file2.csv", filename="file2.csv"),
        DownloadRequest(url="https://example.com/file3.zip", filename="bad/path/file3.zip"),  # Invalid
    ]
    
    # Preview without downloading
    previews = await downloader.download_dry(requests)
    
    # Prepare table data
    table_data = []
    for preview in previews:
        status_icon = "✓" if preview.status == "valid" else "✗"
        reason = preview.reason if preview.reason else "-"
        table_data.append([
            status_icon,
            preview.filename,
            preview.status.upper(),
            reason,
        ])
    
    # Display results
    print(tabulate(
        table_data,
        headers=["Status", "Filename", "Validation", "Error/Notes"],
        tablefmt="grid"
    ))

asyncio.run(preview_downloads())
```

**Output:**
```
┌────────┬──────────────────────┬────────────┬──────────────────────────────────┐
│ Status │ Filename             │ Validation │ Error/Notes                      │
├────────┼──────────────────────┼────────────┼──────────────────────────────────┤
│ ✓      │ file1.pdf            │ VALID      │ -                                │
│ ✓      │ file2.csv            │ VALID      │ -                                │
│ ✗      │ bad/path/file3.zip   │ INVALID    │ Filename cannot contain path ... │
└────────┴──────────────────────┴────────────┴──────────────────────────────────┘
```

For more comprehensive examples, see the `examples/download_dry_preview.py` file:

```bash
pip install tabulate
python examples/download_dry_preview.py
```

This demonstrates:
- Basic dry_run preview with table output
- Batch processing and reporting
- Filtering valid/invalid requests
- Summary statistics

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**DevComfort**
- GitHub: [@devcomfort](https://github.com/devcomfort)
- Email: im@devcomfort.me

## 🤝 Acknowledgments

- Built with [aiohttp](https://docs.aiohttp.org/) for HTTP requests
- Uses [aiofiles](https://github.com/Tinche/aiofiles) for async file operations
- Tested with [pytest](https://pytest.org/) and [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

## 📞 Support

For issues, questions, or suggestions, please [open an issue](https://github.com/devcomfort/parallel-download/issues) on GitHub.

