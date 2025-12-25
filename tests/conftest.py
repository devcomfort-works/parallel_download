"""Pytest configuration and fixtures for parallel_download tests."""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for async tests.

    Yields
    ------
    Generator
        Event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_download_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for download tests.

    Yields
    ------
    Path
        Temporary directory path.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def httpbin_urls() -> dict:
    """
    Provide httpbin test URLs for various scenarios.

    Returns
    -------
    dict
        Dictionary containing httpbin URLs for testing.
    """
    return {
        "small_file": "https://httpbin.org/bytes/1024",  # 1KB
        "medium_file": "https://httpbin.org/bytes/1048576",  # 1MB
        "large_file": "https://httpbin.org/bytes/10485760",  # 10MB
        "text_file": "https://httpbin.org/robots.txt",
        "json_response": "https://httpbin.org/json",
        "status_200": "https://httpbin.org/status/200",
        "status_404": "https://httpbin.org/status/404",
        "status_500": "https://httpbin.org/status/500",
        "delay_1s": "https://httpbin.org/delay/1",
        "delay_5s": "https://httpbin.org/delay/5",
    }


@pytest.fixture(params=["1024", "10240", "102400"])
def file_size_param(request) -> str:
    """
    Parametrize file sizes for factorial testing.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest fixture request object.

    Returns
    -------
    str
        File size parameter (1KB, 10KB, 100KB - httpbin max is ~100KB).
    """
    return request.param


@pytest.fixture(params=[True, False])
def explicit_filename_param(request) -> bool:
    """
    Parametrize explicit filename for factorial testing.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest fixture request object.

    Returns
    -------
    bool
        Whether to use explicit filename.
    """
    return request.param


@pytest.fixture(params=[1, 5, 10])
def max_concurrent_param(request) -> int:
    """
    Parametrize max concurrent downloads for factorial testing.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest fixture request object.

    Returns
    -------
    int
        Maximum concurrent downloads.
    """
    return request.param

