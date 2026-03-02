# Quickstart: Filesystem Management

**Feature**: 005-filesystem-management  
**Date**: 2026-03-03

---

## 기본 사용법

### 디렉토리 생성 보장

```python
from parallel_download.filesystem.directory import Directory

# 존재하지 않는 깊은 경로도 안전하게 생성
d = Directory("/tmp/downloads/2026/03")
success = d.ensure()  # True — 모든 중간 디렉토리 포함 생성
```

### 디렉토리 초기화 (내용 삭제 후 재생성)

```python
d = Directory("./output")
d.ensure()

# 기존 내용을 모두 삭제하고 빈 디렉토리로 리셋
d.clear(reset=True)
```

## Downloader 통합 예시

```python
from parallel_download import Downloader

# Downloader는 내부에서 Directory.ensure()를 자동 호출
downloader = Downloader(
    out_dir="./my_downloads",  # 존재하지 않아도 자동 생성됨
    timeout=30,
    max_concurrent=5,
)
```

## 에러 처리

```python
from parallel_download.filesystem.directory import Directory
from parallel_download.errors import DirectoryPermissionError  # 계획된 신규 에러

d = Directory("/root/restricted")
try:
    d.ensure()
except DirectoryPermissionError as e:
    print(f"디렉토리 생성 실패: {e}")
    # → "Cannot write to directory '/root/restricted': Permission denied"
```
