# parallel-download

asyncio + aiohttp 기반의 고성능 병렬 파일 다운로더입니다.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-91%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **병렬 다운로드** — asyncio 세마포어 기반 동시성 제어로 리소스 고갈 없이 빠르게 다운로드
- **자동 파일명 추출** — URL에서 파일명을 자동 추출하며, 모호한 URL은 명시적 에러로 거부
- **타입 안전** — Pydantic v2 모델 + 전체 타입 힌트로 런타임 안전성 보장
- **구조화된 결과** — `DownloadSuccess` / `DownloadFailure` 판별 유니온(Discriminated Union)으로 결과 처리
- **계층적 에러** — 목적별 예외 클래스(`HTTPError`, `NetworkError`, `DownloadTimeoutError` 등)
- **100% 테스트 커버리지** — 91개 테스트, 브랜치 커버리지 포함

## 설치

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

특정 버전(태그)을 설치하려면:

```bash
# pip
pip install git+https://github.com/devcomfort/parallel_download.git@v0.1.0

# uv
uv add git+https://github.com/devcomfort/parallel_download.git --tag v0.1.0

# rye
rye add parallel-download --git https://github.com/devcomfort/parallel_download.git --tag v0.1.0
```

`requirements.txt`에 추가할 경우:

```text
parallel-download @ git+https://github.com/devcomfort/parallel_download.git
```

## Quick Start

```python
import asyncio
from pathlib import Path
from parallel_download import Downloader

async def main():
    downloader = Downloader(
        out_dir=Path("./downloads"),
        timeout=60,
        max_concurrent=5,
    )

    results = await downloader.download([
        "https://example.com/file1.pdf",
        "https://example.com/file2.csv",
        {"url": "https://example.com/data", "filename": "data.json"},
    ])

    for r in results:
        if r.status == "success":
            print(f"✓ {r.filename} → {r.file_path}")
        else:
            print(f"✗ {r.filename}: {r.error}")

asyncio.run(main())
```

## 입력 형식

`Downloader.download()`는 세 가지 입력 형식을 지원합니다:

```python
# 1. URL 문자열 — 파일명 자동 추출
"https://example.com/report.pdf"

# 2. 딕셔너리 — 파일명 지정 가능
{"url": "https://example.com/data", "filename": "data.json"}

# 3. DownloadRequest 객체
DownloadRequest(url="https://example.com/file.zip")
```

파일명이 지정되지 않으면 URL 경로에서 자동 추출됩니다.
파일명을 추출할 수 없는 URL(`https://example.com`, `https://example.com/dir/`)은
추측하지 않고 명시적 에러를 발생시킵니다.

## API

### `Downloader`

```python
Downloader(
    out_dir: str | Path,      # 다운로드 저장 디렉토리
    timeout: int = 60,        # HTTP 요청 타임아웃 (초)
    max_concurrent: int = 5,  # 최대 동시 다운로드 수
)
```

| Method                              | Description                                                         |
| ----------------------------------- | ------------------------------------------------------------------- |
| `await download(requests)`          | 병렬 다운로드 실행, `list[DownloadSuccess \| DownloadFailure]` 반환 |
| `await validate_requests(requests)` | 다운로드 없이 요청만 검증, `list[DownloadRequest]` 반환             |

### 결과 타입

```python
# 성공
DownloadSuccess(
    url="https://...",
    filename="file.pdf",
    file_path="/path/to/file.pdf",
    status="success",
)

# 실패
DownloadFailure(
    url="https://...",
    filename="file.pdf",
    error="Download timed out after 60s",
    status="failed",
)
```

`status` 필드를 판별자(discriminator)로 사용하는 Pydantic Discriminated Union입니다.

### 예외

| Exception              | Description                               |
| ---------------------- | ----------------------------------------- |
| `NoPathInURLError`     | URL에 경로가 없음                         |
| `DirectoryPathError`   | URL 경로가 디렉토리(`/`로 끝남)           |
| `HTTPError`            | HTTP 응답이 2xx가 아님                    |
| `DownloadTimeoutError` | 요청 타임아웃 초과                        |
| `NetworkError`         | 네트워크 연결 실패                        |
| `FileWriteError`       | 파일 쓰기 실패                            |
| `BulkValidationError`  | 배치 검증 시 복수 에러 (`ExceptionGroup`) |

## 예제

### 결과 처리

```python
from parallel_download import DownloadSuccess, DownloadFailure

results = await downloader.download(urls)

successes = [r for r in results if isinstance(r, DownloadSuccess)]
failures = [r for r in results if isinstance(r, DownloadFailure)]

print(f"성공: {len(successes)}, 실패: {len(failures)}")
for f in failures:
    print(f"  {f.filename}: {f.error}")
```

### 요청 사전 검증

```python
from parallel_download import BulkValidationError

try:
    valid = await downloader.validate_requests([
        "https://example.com/file.pdf",
        "https://example.com",  # 에러: 경로 없음
    ])
except BulkValidationError as e:
    for err in e.exceptions:
        print(f"검증 실패: {err}")
```

### 재시도 패턴

```python
async def download_with_retry(downloader, url, retries=3):
    for attempt in range(retries):
        result = (await downloader.download([url]))[0]
        if result.status == "success":
            return result
        if attempt < retries - 1:
            await asyncio.sleep(2 ** attempt)  # exponential backoff
    return result
```

## 개발

### 환경 설정

```bash
git clone https://github.com/devcomfort/parallel_download.git
cd parallel_download
rye sync
```

### 테스트

```bash
rye run pytest                    # 전체 테스트 + 커버리지
rye run pytest tests/test_downloader.py  # 특정 파일
rye run pytest -k "test_timeout"  # 패턴 매칭
```

### 코드 품질

```bash
rye run ruff check src tests      # 린트
rye run ruff format src tests     # 포맷
rye run mypy src                  # 타입 체크
```

### 프로젝트 구조

```
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

## License

[MIT](LICENSE)

## Author

**DevComfort** — [GitHub](https://github.com/devcomfort) · [Email](mailto:im@devcomfort.me)
