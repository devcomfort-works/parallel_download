# Research: Filesystem Management

**Feature**: 005-filesystem-management  
**Date**: 2026-03-03  
**Purpose**: Technical Context의 미결 사항(NEEDS CLARIFICATION) 해소 및 설계 결정 기록

---

## Research Task 1: FR-003 쓰기 권한 검증 방법

### 배경

spec.md FR-003은 "디렉토리에 대한 쓰기 권한을 확인하고, 쓰기 불가능 시 관련된 권한 에러를 발생시켜야 한다"고 요구한다. 현재 `Directory` 클래스에는 이 기능이 없다.

### 조사 내용

**Option A: `os.access(path, os.W_OK)` 사전 검사**

- 장점: 간단하고 직관적, cross-platform.
- 단점: `os.access()`는 effective UID가 아닌 real UID 기준이므로 setuid 환경에서 부정확할 수 있음.
- Windows 동작: `os.W_OK`는 Windows에서 read-only 속성만 검사. ACL은 무시됨.

**Option B: 임시 파일 쓰기 테스트 (probe)**

- 장점: 실제로 쓸 수 있는지 100% 확인 가능.
- 단점: I/O 오버헤드 (미미함, 1회성), 클린업 필요.

**Option C: 예외 기반 후처리 (EAFP)**

- 장점: Pythonic. 실제 `mkdir` 또는 파일 쓰기 시 `PermissionError`를 잡아서 도메인 에러로 변환.
- 단점: 검증이 "실패 시점"까지 지연됨.

### 결정

- **Decision**: Option C (EAFP) 전용
- **Rationale**:
  - `ensure()` 내부의 `mkdir` 에서 발생하는 `PermissionError`를 도메인 에러(`DirectoryPermissionError`)로 래핑한다.
  - 병렬 단일 다운로드 시퀀스에서 사전 권한 검사는 불필요하며, 실제 실패 시점에서 명확한 도메인 에러를 제공하는 것이 충분하다.
- **Alternatives Rejected**:
  - Option A (`os.access`): 사전 검사는 병렬 다운로드 컨텍스트에서 불필요한 복잡성. real UID vs effective UID 문제도 있음.
  - Option B: 임시 파일 probe는 과도한 복잡성.

---

## Research Task 2: 도메인 에러 클래스 설계

### 배경

Constitution Principle III(Explicit Error Handling)에 따라 `PermissionError` 등 빌트인 예외를 그대로 노출하면 안 된다. 도메인 전용 에러로 래핑해야 한다.

### 조사 내용

현재 에러 구조:

- `errors/download_errors.py`: `DownloadError` ← `HTTPError`, `DownloadTimeoutError`, `NetworkError`, `FileWriteError`
- `errors/extraction_errors.py`: `FilenameExtractionError` ← `NoPathInURLError`, `DirectoryPathError`
- `errors/validation_errors.py`: `BulkValidationError`

파일시스템 관련 에러의 위치:

- `FileWriteError`는 이미 `download_errors.py`에 존재 (파일 쓰기 실패 시 사용).
- 디렉토리 권한 관련 에러는 아직 없음.

### 결정

- **Decision**: `errors/download_errors.py`에 `DirectoryPermissionError(DownloadError)` 클래스 추가
- **Rationale**:
  - 디렉토리 쓰기 권한 부재는 다운로드 파이프라인의 사전 조건 실패이므로 `DownloadError` 계열에 속하는 것이 자연스러움.
  - `FileWriteError`(개별 파일 쓰기 실패)와 의미적으로 구분됨: `DirectoryPermissionError`는 "출력 디렉토리 자체"에 대한 사전 검증 실패.
- **Alternatives Rejected**:
  - 별도 `filesystem_errors.py` 신설: 에러 클래스 1개를 위해 새 파일 생성은 과도. 향후 파일시스템 에러가 3개 이상 늘면 재평가.

---

## Research Task 3: Cross-platform 경로 처리 베스트 프랙티스

### 배경

Constitution의 Target Platform은 Cross-platform이며, `pathlib.Path`를 사용 중이다.

### 조사 내용

- `pathlib.Path`는 OS별 구현을 자동 선택(`PosixPath`, `WindowsPath`).
- `Path.mkdir(parents=True, exist_ok=True)`는 POSIX/Windows 양쪽에서 안전.
- `shutil.rmtree()`는 Windows에서 read-only 파일 삭제 시 `PermissionError` 발생 가능 → `onerror` 핸들러 필요할 수 있음.

### 결정

- **Decision**: 현재 `pathlib.Path` 사용 패턴 유지. `clear(reset=True)` 시 Windows read-only 파일 이슈는 현 스코프 외로 판단.
- **Rationale**: 다운로드된 파일에 read-only 플래그가 설정될 가능성은 극히 낮음. 문제 발생 시 별도 이슈로 처리.
