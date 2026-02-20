"""
Parallel downloader engine.
병렬 다운로드 엔진입니다.
"""

import asyncio
from collections.abc import Iterable
from pathlib import Path
from typing import Union

import aiofiles  # type: ignore
import aiohttp

from .errors import (
    DownloadTimeoutError,
    FileWriteError,
    HTTPError,
    NetworkError,
)
from .filesystem.directory import Directory
from .models import (
    DownloadFailure,
    DownloadInput,
    DownloadRequest,
    DownloadResultType,
    DownloadSuccess,
)
from .url_processor import RequestParser


class Downloader:
    """
    Parallel downloader engine that manages multiple download tasks.
    여러 다운로드 작업을 관리하는 병렬 다운로드 엔진입니다.

    Attributes
    ----------
    out_dir : Path
        Output directory for downloaded files.
        다운로드된 파일이 저장될 디렉토리입니다.
    timeout : int
        HTTP request timeout in seconds.
        HTTP 요청 제한 시간(초)입니다.
    max_concurrent : int
        Maximum number of concurrent downloads.
        최대 동시 다운로드 수입니다.
    """

    out_dir: Path
    timeout: int
    max_concurrent: int

    def __init__(
        self,
        out_dir: Union[str, Path],
        timeout: int = 60,
        max_concurrent: int = 5,
    ):
        """
        Initialize the parallel downloader.
        병렬 다운로더를 초기화합니다.

        Parameters
        ----------
        out_dir : Union[str, Path]
            Output directory for downloaded files.
            다운로드된 파일이 저장될 디렉토리입니다.
        timeout : int, optional
            HTTP request timeout in seconds.
            HTTP 요청 제한 시간(초)입니다.
            Default is 60.
        max_concurrent : int, optional
            Maximum number of concurrent downloads. Must be positive.
            최대 동시 다운로드 수입니다. 양수여야 합니다.
            Default is 5.

        Raises
        ------
        ValueError
            If timeout or max_concurrent are invalid.
            타임아웃 또는 최대 동시성 값이 유효하지 않은 경우 발생합니다.
        """
        self.out_dir = Path(out_dir)

        # Validate timeout
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError(f"timeout must be a positive integer, got {timeout}")
        self.timeout = timeout

        # Validate max_concurrent
        if not isinstance(max_concurrent, int) or max_concurrent <= 0:
            raise ValueError(f"max_concurrent must be a positive integer, got {max_concurrent}")
        self.max_concurrent = max_concurrent

        # Global semaphore for async-safe concurrency control
        # 인스턴스 전체의 동시성을 보장하는 세마포어
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._parser = RequestParser()
        self._dir = Directory(self.out_dir)
        self._dir.ensure()

    async def download(self, requests: Iterable[DownloadInput]) -> list[DownloadResultType]:
        """
        Download files in parallel from the given requests.
        주어진 요청들에 대해 파일을 병렬로 다운로드합니다.

        Parameters
        ----------
        requests : Iterable[DownloadInput]
            Iterable of download requests (URL string, dict, or DownloadRequest object).
            다운로드 요청의 반복 가능한 객체입니다 (URL 문자열, dict, 또는 DownloadRequest 객체).

        Returns
        -------
        list[DownloadResultType]
            List of download results (DownloadSuccess or DownloadFailure).
            다운로드 결과 리스트입니다 (DownloadSuccess 또는 DownloadFailure).
        """
        # Convert various input formats to DownloadRequest objects
        request_list = self._parser.parse(list(requests))

        # Create timeout configuration for the session
        timeout_cfg = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
            tasks = [self._run_task(session, req) for req in request_list]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        return results

    async def _run_task(
        self, session: aiohttp.ClientSession, request: DownloadRequest
    ) -> DownloadResultType:
        """
        Run a single download task with semaphore protection.
        세마포어 보호 하에 단일 다운로드 작업을 실행합니다.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp session to use.
            사용할 aiohttp 세션입니다.
        request : DownloadRequest
            The request to process.
            처리할 요청입니다.

        Returns
        -------
        DownloadResultType
            The result of the download task.
            다운로드 작업의 결과입니다.
        """
        async with self._semaphore:
            return await self._download_file(session, request)

    async def _download_file(
        self, session: aiohttp.ClientSession, request: DownloadRequest
    ) -> DownloadResultType:
        """
        Execute the actual file download logic.
        실제 파일 다운로드 로직을 실행합니다.
        """
        url_str = str(request.url)

        # filename should be guaranteed by normalization, but check for type safety
        if not request.filename:  # pragma: no cover
            # DownloadRequest는 frozen 모델이며 model_validator가 항상 filename을 채움
            # 방어적 코드
            return DownloadFailure(
                url=url_str,
                filename="unknown",
                error="Filename missing in request",
            )

        file_path = self.out_dir / request.filename

        try:
            # Use streaming to save memory
            # 메모리 절약을 위해 스트리밍 방식 사용
            timeout_cfg = aiohttp.ClientTimeout(total=self.timeout)
            async with session.get(url_str, timeout=timeout_cfg) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)

                    return DownloadSuccess(
                        url=url_str,
                        filename=request.filename,
                        file_path=str(file_path),
                    )
                else:
                    error = HTTPError(url_str, response.status)
                    return DownloadFailure(
                        url=url_str,
                        filename=request.filename,
                        error=str(error),
                    )

        except asyncio.TimeoutError:
            timeout_error = DownloadTimeoutError(url_str, self.timeout)
            return DownloadFailure(
                url=url_str,
                filename=request.filename,
                error=str(timeout_error),
            )
        except aiohttp.ClientError as e:
            network_error = NetworkError(url_str, e)
            return DownloadFailure(
                url=url_str,
                filename=request.filename,
                error=str(network_error),
            )
        except (IOError, OSError) as e:
            write_error = FileWriteError(request.filename, e)
            return DownloadFailure(
                url=url_str,
                filename=request.filename,
                error=str(write_error),
            )
        except Exception as e:
            return DownloadFailure(
                url=url_str,
                filename=request.filename,
                error=f"Unexpected error: {str(e)}",
            )

    async def validate_requests(
        self,
        requests: Iterable[DownloadInput],
    ) -> list[DownloadRequest]:
        """
        Validate download requests without performing actual downloads.
        실제 다운로드를 수행하지 않고 다운로드 요청을 검증합니다.

        Validates all download requests and returns a list of DownloadRequest.
        모든 다운로드 요청을 검증하고 DownloadRequest 리스트를 반환합니다.

        Parameters
        ----------
        requests : Iterable[DownloadInput]
            Download requests to validate (URL string, dict, or DownloadRequest object).
            검증할 다운로드 요청입니다 (URL 문자열, dict, 또는 DownloadRequest 객체).

        Returns
        -------
        list[DownloadRequest]
            List of request objects.
            요청 객체 리스트입니다.

        Raises
        ------
        BulkValidationError
            If one or more requests fail validation.
            하나 이상의 요청이 검증에 실패한 경우 발생합니다.

        Examples
        --------
        >>> downloader = Downloader(out_dir=Path("./downloads"))
        >>> requests = [
        ...     "https://example.com/file.pdf",
        ...     {"url": "https://example.com/data.csv", "filename": "data.csv"},
        ... ]
        >>> try:
        ...     valid_reqs = await downloader.validate_requests(requests)
        ...     print(f"All {len(valid_reqs)} requests are valid")
        ... except BulkValidationError as e:
        ...     for err in e.errors:
        ...         print(f"Invalid: {err.input_data}, Reason: {err.reason}")
        """
        return self._parser.parse(list(requests))
