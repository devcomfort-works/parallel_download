from typing import List, Union

from ..errors import BulkValidationError
from ..models import DownloadInput, DownloadRequest


class RequestParser:
    """
    A parser for converting various input formats into DownloadRequest objects.
    다양한 입력 형식을 DownloadRequest 객체로 변환하는 파서 클래스입니다.

    This class handles the normalization and validation of input data,
    supporting single items or lists of items. It aggregates validation errors
    into a single BulkValidationError.
    이 클래스는 입력 데이터의 정규화 및 검증을 처리하며, 단일 항목 또는 항목 리스트를 지원합니다.
    검증 에러는 하나의 BulkValidationError로 집계됩니다.

    Examples
    --------
    >>> parser = RequestParser()
    >>> inputs = ["https://example.com/file1.zip", {"url": "https://example.com/file2.zip"}]
    >>> requests = parser.parse(inputs)
    >>> len(requests)
    2
    >>> str(requests[0].url)
    'https://example.com/file1.zip'
    """

    def parse(
        self,
        inputs: Union[DownloadInput, List[DownloadInput]],
    ) -> List[DownloadRequest]:
        """
        Convert single or list of inputs into a list of validated DownloadRequest objects.
        단일 또는 리스트 형태의 입력을 검증된 DownloadRequest 객체 리스트로 변환합니다.

        Parameters
        ----------
        inputs : Union[DownloadInput, List[DownloadInput]]
            Single input (str, dict, DownloadRequest) or a list of inputs.
            단일 입력(문자열, 딕셔너리, DownloadRequest) 또는 입력 리스트입니다.

        Returns
        -------
        List[DownloadRequest]
            A list of validated DownloadRequest objects.
            검증된 DownloadRequest 객체 리스트입니다.

        Raises
        ------
        BulkValidationError
            If one or more inputs fail validation. Contains a list of all errors.
            하나 이상의 입력이 검증에 실패한 경우 발생합니다. 모든 에러의 리스트를 포함합니다.

        Examples
        --------
        >>> parser = RequestParser()
        >>> # Single input / 단일 입력
        >>> reqs = parser.parse("https://example.com/file.zip")
        >>> len(reqs)
        1

        >>> # List input with mixed types / 혼합 타입 리스트 입력
        >>> inputs = [
        ...     "https://a.com/1.png",
        ...     {"url": "https://b.com/2.png", "filename": "custom.png"}
        ... ]
        >>> reqs = parser.parse(inputs)
        >>> len(reqs)
        2
        """
        if not isinstance(inputs, list):
            inputs = [inputs]

        validated_requests = []
        errors = []

        # Use map to apply processing, but manage error collection manually
        # map을 사용하여 처리를 적용하지만, 에러 수집은 수동으로 관리합니다.
        results = map(self._safe_normalize, inputs)

        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                validated_requests.append(result)

        if errors:
            raise BulkValidationError(f"Validation failed for {len(errors)} requests", errors)

        return validated_requests

    def _safe_normalize(self, item: DownloadInput) -> Union[DownloadRequest, Exception]:
        """
        Wrapper to catch exceptions during normalization for use with map.
        map과 함께 사용하기 위해 정규화 중 발생하는 예외를 잡는 래퍼입니다.
        """
        try:
            return self._normalize_input(item)
        except Exception as e:
            return ValueError(f"Invalid input '{item}': {str(e)}")

    def _normalize_input(
        self,
        data: Union[DownloadInput, DownloadRequest],
    ) -> DownloadRequest:
        """
        Normalize various input formats into a DownloadRequest object.
        다양한 형태의 입력을 DownloadRequest 객체로 정규화합니다.
        """
        return DownloadRequest.model_validate(data)
