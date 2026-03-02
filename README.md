# parallel-download

`parallel-download`는 `asyncio`와 `aiohttp`를 기반으로 작동하는 고성능 병렬 파일 다운로드 라이브러리입니다.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-91%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 주요 기능

*   **병렬 다운로드**: `asyncio` 세마포어를 사용하여 시스템 리소스 고갈 없이 여러 파일을 동시에 빠르게 다운로드합니다.
*   **자동 파일명 추출**: URL에서 파일명을 자동으로 추출합니다. 파일명을 확정할 수 없는 모호한 URL은 명시적 에러를 발생시켜 예기치 않은 동작을 방지합니다.
*   **타입 안정성**: Pydantic v2 모델과 완벽한 타입 힌트를 적용하여 런타임 환경의 안정성을 보장합니다.
*   **구조화된 결과 반환**: `DownloadSuccess`와 `DownloadFailure`로 구성된 판별 유니온(Discriminated Union)을 통해 다운로드 결과를 직관적으로 처리할 수 있습니다.
*   **계층적 에러 처리**: `HTTPError`, `NetworkError`, `DownloadTimeoutError` 등 상황에 맞는 세분화된 예외 클래스를 제공합니다.
*   **신뢰성 높은 코드**: 91개의 테스트 케이스를 통해 100%의 테스트 커버리지를 유지합니다.

## 설치 방법

사용 중인 패키지 관리자에 맞춰 라이브러리를 설치하세요.

### pip

```bash
pip install git+https://github.com/devcomfort/parallel_download.git
```

### uv

```bash
uv add git+https://github.com/devcomfort/parallel_download.git
```

### rye

```bash
rye add parallel-download --git https://github.com/devcomfort/parallel_download.git
```

**참고:** 특정 버전(태그)을 설치하려면 명령어 끝에 `@v0.1.0` (pip) 또는 `--tag v0.1.0` (uv, rye)을 추가하세요.

## 빠른 시작

다음은 `Downloader`를 사용하여 여러 파일을 동시에 다운로드하는 기본 예시입니다.

```python
import asyncio
from pathlib import Path
from parallel_download import Downloader

async def main():
    # 다운로더 인스턴스 생성
    downloader = Downloader(
        out_dir=Path("./downloads"),
        timeout=60,
        max_concurrent=5,
    )

    # 다운로드 실행
    results = await downloader.download([
        "https://example.com/file1.pdf",
        "https://example.com/file2.csv",
        {"url": "https://example.com/data", "filename": "data.json"},
    ])

    # 결과 처리
    for r in results:
        if r.status == "success":
            print(f"✓ {r.filename} → {r.file_path}")
        else:
            print(f"✗ {r.filename}: {r.error}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 사용 가이드

### 지원하는 입력 형식

`Downloader.download()` 메서드는 세 가지 형태의 입력을 지원합니다.

1.  **URL 문자열**: 파일명을 URL 경로에서 자동으로 추출합니다.
    ```python
    "https://example.com/report.pdf"
    ```
2.  **딕셔너리 (Dictionary)**: 다운로드할 파일명을 직접 지정할 수 있습니다.
    ```python
    {"url": "https://example.com/data", "filename": "data.json"}
    ```
3.  **DownloadRequest 객체**: 명시적인 타입 안정성이 필요할 때 사용합니다.
    ```python
    from parallel_download import DownloadRequest
    
    DownloadRequest(url="https://example.com/file.zip")
    ```

**주의:** 파일명을 지정하지 않은 상태에서 URL로부터 파일명을 추출할 수 없는 경우(예: `https://example.com/` 또는 `https://example.com/dir/`), 라이브러리는 임의로 파일명을 추측하지 않고 명시적인 에러를 발생시킵니다.

## API 참조

### `Downloader` 클래스

다운로드를 관리하는 핵심 클래스입니다.

```python
Downloader(
    out_dir: str | Path,      # 다운로드한 파일을 저장할 디렉토리 경로
    timeout: int = 60,        # HTTP 요청 타임아웃 (초 단위)
    max_concurrent: int = 5,  # 동시에 실행할 최대 다운로드 수
)
```

#### 주요 메서드

| 메서드 | 설명 | 반환 타입 |
| --- | --- | --- |
| `await download(requests)` | 전달받은 요청 목록을 병렬로 다운로드합니다. | `list[DownloadSuccess | DownloadFailure]` |
| `await validate_requests(requests)` | 실제 다운로드를 수행하지 않고 요청의 유효성만 검증합니다. | `list[DownloadRequest]` |

### 결과 모델

다운로드 결과는 Pydantic의 판별 유니온(Discriminated Union)을 사용하여 `status` 필드로 성공 여부를 구분합니다.

#### 성공 (`DownloadSuccess`)
```python
DownloadSuccess(
    url="https://...",
    filename="file.pdf",
    file_path="/path/to/file.pdf",
    status="success",
)
```

#### 실패 (`DownloadFailure`)
```python
DownloadFailure(
    url="https://...",
    filename="file.pdf",
    error="Download timed out after 60s",
    status="failed",
)
```

### 예외 (Exceptions)

발생할 수 있는 주요 예외 클래스는 다음과 같습니다.

| 예외 클래스 | 설명 |
| --- | --- |
| `NoPathInURLError` | URL에 파일 경로가 포함되어 있지 않습니다. |
| `DirectoryPathError` | URL 경로가 디렉토리를 가리킵니다 (`/`로 끝남). |
| `HTTPError` | HTTP 응답 코드가 2xx 성공 상태가 아닙니다. |
| `DownloadTimeoutError` | HTTP 요청이 지정된 타임아웃을 초과했습니다. |
| `NetworkError` | 네트워크 연결에 실패했습니다. |
| `FileWriteError` | 디스크에 파일을 쓰는 중 오류가 발생했습니다. |
| `BulkValidationError` | 여러 요청을 검증하는 과정에서 복수의 에러가 발생했습니다 (`ExceptionGroup` 기반). |

## 고급 사용 예시

### 다운로드 결과 분리 처리

성공한 다운로드와 실패한 다운로드를 분리하여 처리하는 방법입니다.

```python
from parallel_download import DownloadSuccess, DownloadFailure

results = await downloader.download(urls)

successes = [r for r in results if isinstance(r, DownloadSuccess)]
failures = [r for r in results if isinstance(r, DownloadFailure)]

print(f"성공: {len(successes)}건, 실패: {len(failures)}건")
for f in failures:
    print(f"  - {f.filename} 실패 사유: {f.error}")
```

### 요청 사전 검증

다운로드를 시작하기 전에 URL의 유효성을 미리 검사할 수 있습니다.

```python
from parallel_download import BulkValidationError

try:
    valid_requests = await downloader.validate_requests([
        "https://example.com/file.pdf",
        "https://example.com",  # 에러 발생: 경로 없음
    ])
except BulkValidationError as e:
    for err in e.exceptions:
        print(f"검증 실패: {err}")
```

### 지수 백오프(Exponential Backoff)를 적용한 재시도

네트워크 오류 등에 대비하여 재시도 로직을 구현하는 예시입니다.

```python
async def download_with_retry(downloader, url, retries=3):
    for attempt in range(retries):
        result = (await downloader.download([url]))[0]
        if result.status == "success":
            return result
        
        if attempt < retries - 1:
            await asyncio.sleep(2 ** attempt)  # 지수 백오프 대기
            
    return result
```

## 개발 가이드

프로젝트에 기여하거나 로컬에서 개발 환경을 설정하는 방법입니다.

### 환경 설정

```bash
git clone https://github.com/devcomfort/parallel_download.git
cd parallel_download
rye sync
```

### 테스트 실행

```bash
rye run pytest                           # 전체 테스트 실행 및 커버리지 측정
rye run pytest tests/test_downloader.py  # 특정 테스트 파일 실행
rye run pytest -k "test_timeout"         # 특정 패턴의 테스트만 실행
```

### 코드 품질 관리

```bash
rye run ruff check src tests             # 린트(Lint) 검사
rye run ruff format src tests            # 코드 포맷팅
rye run mypy src                         # 정적 타입 검사
```

### 프로젝트 구조

```text
parallel_download/
├── src/parallel_download/
│   ├── __init__.py          # 패키지 exports
│   ├── downloader.py        # Downloader 클래스
│   ├── errors/              # 계층적 예외 클래스
│   ├── filesystem/          # 디렉토리 관리
│   ├── models/              # DownloadRequest, Result 모델
│   └── url_processor/       # URL 파싱, 파일명 추출
├── tests/                   # 91개 테스트 (100% coverage)
├── examples/                # 데모 스크립트
└── pyproject.toml           # 프로젝트 설정
```

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)에 따라 배포됩니다.

## 작성자

**DevComfort** — [GitHub](https://github.com/devcomfort) · [Email](mailto:im@devcomfort.me)
