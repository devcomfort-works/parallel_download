# Testing Guide for parallel_download

## Setup

1. Install development environment using rye:

```bash
rye sync
```

## Running Tests

### Run all tests:

```bash
pytest
```

### Run specific test file:

```bash
pytest tests/test_downloader.py
```

### Run specific test class:

```bash
pytest tests/test_downloader.py::TestDownloaderBasic
```

### Run specific test:

```bash
pytest tests/test_downloader.py::TestDownloaderBasic::test_downloader_initialization
```

### Run with specific markers:

```bash
# Run only async tests
pytest -m asyncio

# Run only factorial tests
pytest -m factorial

# Run excluding slow tests
pytest -m "not slow"
```

### Run with coverage report:

```bash
pytest --cov=src/parallel_download --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with verbose output:

```bash
pytest -vv
```

### Run tests in parallel (requires pytest-xdist):

```bash
pip install pytest-xdist
pytest -n auto
```

## Test Structure

### `tests/conftest.py`
- Shared fixtures for all tests
- Event loop fixture for async tests
- Temporary directory fixture
- httpbin URL fixtures
- Parametrized fixtures for factorial testing

### `tests/test_download_request.py`
- Tests for filename extraction
- Tests for error handling
- Tests for URL pattern variations

### `tests/test_downloader.py`
- Basic download tests
- Parallel download tests
- **Full Factorial Tests** (3 × 2 × 3 = 18 combinations):
  - File sizes: 1KB, 1MB, 10MB
  - Filename mode: Explicit vs Auto-extracted
  - Concurrency: 1, 5, 10
- **Concurrent Download Tests** (3 × 3 = 9 combinations):
  - Number of files: 1, 5, 10
  - Concurrency levels: 1, 5, 10
- **Timeout & Concurrency Tests** (2 × 2 × 3 = 12 combinations):
  - Delays: 1s, 5s
  - Concurrency: 1, 5, 10
- Edge case tests

### `tests/test_utils.py`
- Tests for utility functions
- Directory creation tests
- Directory clearing tests

## Test Results

Total test combinations with factorial design:
- DownloadRequest: ~20 tests
- Downloader (full factorial): 18 + 9 + 12 + edge cases = 50+ tests
- Utils: ~15 tests
- **Total: ~85 tests**

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -r requirements-dev.txt
    - run: pytest --cov
```

## Notes

- Tests using httpbin require internet connection
- Some tests may take time due to large file downloads (10MB)
- Async tests use pytest-asyncio plugin
- Full factorial tests ensure comprehensive coverage across parameter combinations

