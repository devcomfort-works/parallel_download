import asyncio
from pathlib import Path
from collections.abc import Iterable

import aiohttp
import aiofiles

from .utils import ensure_directory
from .download_request import DownloadRequest
from .download_result import (
    DownloadResultType,
    DownloadSuccess,
    DownloadFailure,
    PreviewResult,
)
from .errors import HTTPError, DownloadTimeoutError, NetworkError, FileWriteError
from .config import TimeoutRecipe, DOWNLOAD_RECIPES


class Downloader:
    out_dir: Path
    timeout: int
    max_concurrent: int

    def __init__(
        self,
        out_dir: Path,
        timeout: TimeoutRecipe | int = "BALANCED",
        max_concurrent: int = 5,
    ):
        """
        Initialize the parallel downloader.

        Parameters
        ----------
        out_dir : Path
            Output directory for downloaded files.
        timeout : TimeoutRecipe | int, optional
            HTTP request timeout. Can be a recipe name or seconds.
            Recipe options:
            - "FOR_LARGE_FILES": 300s (5 min) for downloading large files
            - "BALANCED": 60s (1 min) for mixed file sizes
            - "FOR_SMALL_FILES": 15s for downloading small files
            Can also specify timeout in seconds as an integer (must be positive).
            Default is "BALANCED".
        max_concurrent : int, optional
            Maximum number of concurrent downloads. Must be positive.
            Default is 5.

        Raises
        ------
        ValueError
            If timeout recipe is invalid, or if timeout/max_concurrent are invalid.
        """
        self.out_dir = out_dir

        # Resolve timeout from recipe or use direct value
        if isinstance(timeout, str):
            if timeout not in DOWNLOAD_RECIPES:
                raise ValueError(
                    f"Invalid timeout recipe: {timeout}. "
                    f"Available recipes: {', '.join(DOWNLOAD_RECIPES.keys())}"
                )
            self.timeout = DOWNLOAD_RECIPES[timeout].timeout
        else:
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValueError(f"timeout must be a positive integer, got {timeout}")
            self.timeout = timeout

        # Validate max_concurrent
        if not isinstance(max_concurrent, int) or max_concurrent <= 0:
            raise ValueError(
                f"max_concurrent must be a positive integer, got {max_concurrent}"
            )
        self.max_concurrent = max_concurrent

        ensure_directory(self.out_dir)

    async def download(
        self, requests: Iterable[DownloadRequest]
    ) -> list[DownloadResultType]:
        """
        Download files in parallel from the given requests.

        Parameters
        ----------
        requests : Iterable[DownloadRequest]
            Iterable of DownloadRequest objects to download.

        Returns
        -------
        list[DownloadResultType]
            List of download results (DownloadSuccess or DownloadFailure).
        """
        # Convert iterable to list for multiple iterations
        request_list = list(requests)

        # Create semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [
                self._download_single(session, semaphore, req) for req in request_list
            ]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        return results

    async def download_dry(
        self, requests: Iterable[DownloadRequest]
    ) -> list[PreviewResult]:
        """
        Preview download requests without performing actual downloads.

        Validates all download requests and returns preview results.
        Useful for checking if URLs and filenames are valid before
        starting actual downloads.

        Parameters
        ----------
        requests : Iterable[DownloadRequest]
            Download requests to preview

        Returns
        -------
        list[PreviewResult]
            List of preview results with validation status for each request

        Examples
        --------
        >>> downloader = Downloader(out_dir=Path("./downloads"))
        >>> requests = [
        ...     DownloadRequest(url="https://example.com/file.pdf", filename="file.pdf"),
        ...     DownloadRequest(url="https://example.com/data.csv", filename="data.csv"),
        ... ]
        >>> previews = await downloader.download_dry(requests)
        >>> for preview in previews:
        ...     if preview.status == "valid":
        ...         print(f"✓ {preview.filename}")
        ...     else:
        ...         print(f"✗ {preview.filename}: {preview.reason}")
        """
        request_list = list(requests)
        results = []

        for req in request_list:
            try:
                # DownloadRequest.__post_init__ already validates URL
                # Additional filename validation
                if "/" in req.filename or "\\" in req.filename:
                    raise ValueError("Filename cannot contain path separators")

                results.append(
                    PreviewResult(
                        url=req.url,
                        filename=req.filename,
                        status="valid",
                    )
                )
            except Exception as e:
                # Extract filename safely for error reporting
                filename = getattr(req, "filename", "unknown")
                results.append(
                    PreviewResult(
                        url=req.url,
                        filename=filename,
                        status="invalid",
                        reason=str(e),
                    )
                )

        return results

    async def _download_single(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        request: DownloadRequest,
    ) -> DownloadResultType:
        """
        Download a single file with concurrency control.

        Parameters
        ----------
        session : aiohttp.ClientSession
            Shared HTTP client session.
        semaphore : asyncio.Semaphore
            Semaphore for limiting concurrent downloads.
        request : DownloadRequest
            Download request object.

        Returns
        -------
        DownloadResultType
            Either DownloadSuccess or DownloadFailure object.
        """
        async with semaphore:
            try:
                async with session.get(request.url) as response:
                    if response.status == 200:
                        file_path = self.out_dir / request.filename
                        async with aiofiles.open(file_path, "wb") as f:
                            content = await response.read()
                            await f.write(content)

                        return DownloadSuccess(
                            url=request.url,
                            filename=request.filename,
                            file_path=str(file_path),
                        )
                    else:
                        error = HTTPError(request.url, response.status)
                        return DownloadFailure(
                            url=request.url,
                            filename=request.filename,
                            error=str(error),
                        )
            except asyncio.TimeoutError:
                error = DownloadTimeoutError(request.url, self.timeout)
                return DownloadFailure(
                    url=request.url,
                    filename=request.filename,
                    error=str(error),
                )
            except aiohttp.ClientError as e:
                error = NetworkError(request.url, e)
                return DownloadFailure(
                    url=request.url,
                    filename=request.filename,
                    error=str(error),
                )
            except IOError as e:
                error = FileWriteError(request.filename, e)
                return DownloadFailure(
                    url=request.url,
                    filename=request.filename,
                    error=str(error),
                )
            except Exception as e:
                return DownloadFailure(
                    url=request.url,
                    filename=request.filename,
                    error=f"Unexpected error: {str(e)}",
                )
