"""
Models for Download Results (Discriminated Union)
다운로드 결과 모델 (식별된 유니온)
=================================================

This module defines the data structures for download operation results.
It explicitly implements a **Discriminated Union** pattern to differentiate
between successful and failed downloads using a `status` field.
이 모듈은 다운로드 작업 결과에 대한 데이터 구조를 정의합니다.
`status` 필드를 사용하여 성공적인 다운로드와 실패한 다운로드를 구분하는
**Discriminated Union** 패턴을 명시적으로 구현합니다.

The `DownloadResultType` is the primary type exposed by this module,
allowing generic handling of results while maintaining type safety.
`DownloadResultType`은 이 모듈에서 노출하는 주요 타입으로,
타입 안전성을 유지하면서 결과를 일반화하여 처리할 수 있게 합니다.

Classes
-------
DownloadResultBase
    Base model containing common attributes (url, filename).
    공통 속성(url, filename)을 포함하는 기본 모델입니다.
DownloadSuccess
    Model for successful operations (`status='success'`), including the file path.
    파일 경로를 포함하는 성공적인 작업(`status='success'`) 모델입니다.
DownloadFailure
    Model for failed operations (`status='failed'`), including the error message.
    에러 메시지를 포함하는 실패한 작업(`status='failed'`) 모델입니다.

Types
-----
DownloadResultType
    Annotated Union of `DownloadSuccess` and `DownloadFailure` with a discriminator.
    식별자(discriminator)가 포함된 `DownloadSuccess`와 `DownloadFailure`의 Annotated Union입니다.

Examples
--------
Using types for pattern matching or validation:

>>> from parallel_download.models.result import DownloadSuccess, DownloadFailure
>>> result = DownloadSuccess(url="http://a.com", filename="a.txt", file_path="/tmp/a.txt")
>>> result.status
'success'
"""

from typing import Union, Literal, Annotated
from pydantic import BaseModel, Field


class DownloadResultBase(BaseModel):
    """
    Base class for download operation results.
    다운로드 작업 결과의 기본 클래스입니다.

    Attributes
    ----------
    url : str
        The URL that was downloaded.
        다운로드된 URL입니다.
    filename : str
        The target filename for the download.
        다운로드 대상 파일명입니다.
    """

    url: str
    filename: str


class DownloadSuccess(DownloadResultBase):
    """
    Represents a successful download operation.
    성공한 다운로드 작업을 나타냅니다.

    Attributes
    ----------
    status : Literal["success"]
        Always "success" for successful downloads.
        성공한 다운로드의 경우 항상 "success"입니다.
    file_path : str
        The full path where the file was saved.
        파일이 저장된 전체 경로입니다.
    """

    status: Literal["success"] = Field(default="success")
    file_path: str


class DownloadFailure(DownloadResultBase):
    """
    Represents a failed download operation.
    실패한 다운로드 작업을 나타냅니다.

    Attributes
    ----------
    status : Literal["failed"]
        Always "failed" for failed downloads.
        실패한 다운로드의 경우 항상 "failed"입니다.
    error : str
        Error message describing why the download failed.
        다운로드 실패 원인을 설명하는 에러 메시지입니다.
    """

    status: Literal["failed"] = Field(default="failed")
    error: str


DownloadResultType = Annotated[
    Union[DownloadSuccess, DownloadFailure],
    Field(discriminator="status"),
]


# Alias for backwards compatibility or cleaner typing
DownloadResult = DownloadResultType
