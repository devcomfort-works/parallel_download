from typing import Optional, Union, Any
from pydantic import (
    BaseModel,
    HttpUrl,
    ConfigDict,
    field_validator,
    ValidationInfo,
    model_validator,
)


class DownloadRequest(BaseModel):
    """
    Flexible request schema that developers can create directly.
    개발자가 직접 생성할 수 있는 유연한 요청 스키마입니다.

    Attributes
    ----------
    url : HttpUrl
        The URL to download.
        다운로드할 URL입니다.
    filename : Optional[str], optional
        The target filename. If not provided, it will be extracted from the URL.
        대상 파일명입니다. 제공되지 않으면 URL에서 추출됩니다.

    Examples
    --------
    >>> req = DownloadRequest(url="https://example.com/file.zip")
    >>> req.url
    'https://example.com/file.zip'
    """

    model_config = ConfigDict(frozen=True)

    url: HttpUrl
    filename: Optional[str] = None

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: Optional[str]) -> Optional[str]:
        """
        Validator to ensure filename does not contain path separators.
        파일명에 경로 구분자가 포함되어 있지 않은지 확인합니다.
        """
        # 1. 파일명이 제공되었고, 경로 구분자가 포함되어 있는지 검사합니다.
        if v and ("/" in v or "\\" in v):
            raise ValueError("filename must not contain path separators")

        # 2. 검증된 파일명을 반환합니다.
        return v

    @model_validator(mode="before")
    @classmethod
    def normalize_input(
        cls,
        data: Union["DownloadRequest", str, dict[str, Any]],
        info: ValidationInfo,
    ) -> dict[str, Optional[str]]:
        """
        Pre-process input data into a dictionary format *before* Pydantic validation.
        Pydantic 검증 전에 입력 데이터를 딕셔너리 형태로 전처리합니다.

        [Transformation Examples / 변환 예시]

        Case 1: String Input (단순 문자열 입력)
        ---------------------------------------
        Input:  "https://example.com/data.csv"
        Output: {'url': 'https://example.com/data.csv', 'filename': 'data.csv'}
        (Effect: Automatically extracts filename from URL. / URL에서 파일명을 자동 추출합니다.)

        Case 2: Dictionary without filename (파일명 없는 딕셔너리)
        ------------------------------------------------------
        Input:  {'url': 'https://example.com/report.pdf'}
        Output: {'url': 'https://example.com/report.pdf', 'filename': 'report.pdf'}
        (Effect: Automatically extracts filename from URL. / URL에서 파일명을 자동 추출합니다.)

        Case 3: Complete Dictionary (완전한 딕셔너리)
        -----------------------------------------
        Input:  {'url': 'https://example.com/image.png', 'filename': 'logo.png'}
        Output: {'url': 'https://example.com/image.png', 'filename': 'logo.png'}
        (Effect: Uses provided filename. / 제공된 파일명을 그대로 사용합니다.)

        Case 4: Existing DownloadRequest Object (기존 DownloadRequest 객체)
        -----------------------------------------------
        Input:  DownloadRequest(url='https://example.com/file.txt')
        Output: {'url': 'https://example.com/file.txt', 'filename': 'file.txt'}
        (Effect: Converts object back to dictionary. / 객체를 다시 딕셔너리로 변환합니다.)
        """
        # 1. 입력 데이터의 타입에 따라 딕셔너리 형태로 변환합니다.
        if isinstance(data, DownloadRequest):
            data = {"url": data.url, "filename": data.filename}
        elif isinstance(data, str):
            data = {"url": data}
        elif isinstance(data, dict):
            data = dict(data)
        else:
            raise TypeError(f"Unsupported input type: {type(data)}")

        # 2. 'url' 키가 포함되어 있는지 확인합니다.
        if "url" not in data:
            raise ValueError("Dictionary input must contain 'url' key")

        url_str = str(data["url"])
        filename = data.get("filename")

        # 3. 파일명이 명시되지 않은 경우, URLProcessor를 사용하여 파일명을 추출합니다.
        if not filename:
            from ..url_processor.extract_filename_from_url import (
                extract_filename_from_url,
            )

            filename = extract_filename_from_url(url_str)

        # 4. 정규화된 데이터를 반환합니다.
        return {"url": url_str, "filename": filename}


# Flexible type definition for developer input (Public API)
DownloadInput = Union[str, dict[str, Any], DownloadRequest]
"""
Flexible input type for download requests.
다운로드 요청을 위한 유연한 입력 타입입니다.

Forms
-----
1. str
    Simple URL string. Filename will be extracted automatically.
    단순 URL 문자열. 파일명은 자동으로 추출됩니다.
2. dict
    Dictionary containing 'url' and optionally 'filename'.
    'url'과 선택적으로 'filename'을 포함하는 딕셔너리.
3. DownloadRequest
    Pre-constructed DownloadRequest object.
    미리 생성된 DownloadRequest 객체.

Examples
--------
>>> # Case 1: Simple URL string (filename auto-extracted)
>>> input1: DownloadInput = "https://example.com/file.zip"

>>> # Case 2: Dictionary with URL only (filename auto-extracted)
>>> input2: DownloadInput = {"url": "https://example.com/image.png"}

>>> # Case 3: Dictionary with custom filename
>>> input3: DownloadInput = {"url": "https://example.com/data", "filename": "data.json"}

>>> # Case 4: Pre-constructed DownloadRequest object
>>> input4: DownloadInput = DownloadRequest(url="https://example.com/archive.tar.gz")
"""


def normalize_request(data: DownloadInput) -> DownloadRequest:
    """
    Convert a DownloadInput (str, dict, or DownloadRequest) into a validated DownloadRequest object.
    DownloadInput(문자열, 딕셔너리, 또는 DownloadRequest)을 검증된 DownloadRequest 객체로 변환합니다.

    This function leverages the `DownloadRequest` model's `before` validator to handle
    parsing and filename extraction automatically.
    이 함수는 `DownloadRequest` 모델의 `before` 검증기를 사용하여 파싱 및 파일명 추출을 자동으로 처리합니다.

    Parameters
    ----------
    data : DownloadInput
        The input to normalize.
        정규화할 입력입니다.

    Returns
    -------
    DownloadRequest
        The validated DownloadRequest object.
        검증된 DownloadRequest 객체입니다.

    Examples
    --------
    >>> req = normalize_request("https://example.com/file.zip")
    >>> req.filename
    'file.zip'
    """
    if isinstance(data, DownloadRequest):
        return data
    return DownloadRequest.model_validate(data)
