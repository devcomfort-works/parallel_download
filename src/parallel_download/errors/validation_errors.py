"""Validation related errors."""

try:
    ExceptionGroup
except (
    NameError
):  # pragma: no cover — Python 3.11 미만에서만 실행; 단일 환경 CI에서는 구조적으로 커버 불가
    from exceptiongroup import ExceptionGroup


class BulkValidationError(ExceptionGroup):
    """
    Exception group that aggregates multiple validation failures from a batch of requests.
    배치 요청 처리 중 발생한 여러 검증 실패를 집계하는 예외 그룹입니다.

    It allows handling multiple validation errors simultaneously using Python 3.11+
    `except*` syntax.
    Python 3.11+의 `except*` 구문을 사용하여 여러 검증 에러를 동시에 처리할 수 있게 합니다.

    Examples
    --------
    >>> errors = [ValueError("Invalid URL"), ValueError("Missing filename")]
    >>> raise BulkValidationError("Batch validation failed", errors)
    """
