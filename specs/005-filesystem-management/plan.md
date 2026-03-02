# Implementation Plan: Filesystem Management

**Branch**: `005-filesystem-management` | **Date**: 2026-03-03 | **Spec**: [Spec](spec.md)
**Input**: Feature specification from `/specs/005-filesystem-management/spec.md`

## Summary

`parallel_download.filesystem` 모듈의 디렉토리 관리 기능을 명세화하고 설계한다. `Directory` 클래스가 다운로드 출력 경로의 존재 보장(`ensure`)과 내용 초기화(`clear`)를 안전하게 수행하고, 실패 시 도메인 에러로 명확히 보고하도록 한다. 현재 `ensure()`와 `clear()`는 구현 완료 상태이며, FR-003(`ensure()` 내 `PermissionError` 도메인 래핑)은 미구현 상태로 본 플랜에서 설계한다.

## Technical Context

**Language/Version**: Python 3.8+  
**Primary Dependencies**: 표준 라이브러리만 사용 (`pathlib`, `shutil`)  
**Storage**: 로컬 파일시스템  
**Testing**: pytest  
**Target Platform**: Cross-platform (Linux/macOS/Windows)  
**Project Type**: Python Library (single project)  
**Performance Goals**: N/A (파일시스템 I/O는 OS에 위임; 디렉토리 생성은 1회성 호출)  
**Constraints**: Python 3.8+ 호환, `pathlib.Path` 기반 cross-platform 동작  
**Scale/Scope**: 파일 1개 (`directory.py`, ~75 LOC), 테스트 1개 (`test_directory.py`)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### I. Type Safety First

- **Compliance**: ✅
- **Notes**: `Directory.__init__`은 `Union[str, Path]` 타입 힌트 완료. `ensure()` → `bool`, `clear()` → `bool` 반환 타입 명시됨. 신규 메서드도 동일 기준 적용.

### II. Asynchronous By Design

- **Compliance**: ✅ (해당 없음)
- **Notes**: `Directory`는 순수 동기 파일시스템 유틸리티. `Downloader.__init__`에서 동기적으로 호출되므로 async 불필요. Constitution의 "I/O operations MUST be non-blocking" 원칙에서 디렉토리 생성은 1회성 초기화이므로 예외 적용 타당.

### III. Explicit Error Handling

- **Compliance**: ✅ (설계 완료, 구현 대기)
- **Notes**: research.md에서 `DirectoryPermissionError(DownloadError)` 도입 결정. `ensure()` 내부의 `PermissionError`를 래핑하도록 설계됨. data-model.md에 상세 명세 기록.

### IV. Comprehensive Testing

- **Compliance**: ✅
- **Notes**: `test_directory.py`에 ensure/clear에 대한 happy path + edge case 테스트 존재. 권한 검증 추가 시 테스트도 함께 추가 필요.

### V. Code Style Consistency

- **Compliance**: ✅
- **Notes**: NumPy 스타일 docstring 적용됨. `ruff` 통과.

## Project Structure

### Documentation (this feature)

```text
specs/005-filesystem-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/parallel_download/
└── filesystem/
    ├── __init__.py          # 패키지 초기화 (현재 빈 docstring만 존재)
    └── directory.py         # Directory 클래스 (ensure, clear + 신규: PermissionError 래핑)

tests/
└── test_directory.py        # Directory 유닛 테스트
```

**Structure Decision**: 기존 single project 구조 유지. `filesystem/` 서브모듈은 001-architecture-refactoring에서 이미 확립됨. 추가 디렉토리 생성 불필요.

## Complexity Tracking

> Constitution Check 위반 없음. 테이블 생략.
