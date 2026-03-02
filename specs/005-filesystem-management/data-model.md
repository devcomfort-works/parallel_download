# Data Model: Filesystem Management

**Feature**: 005-filesystem-management  
**Date**: 2026-03-03  
**Source**: spec.md, research.md

---

## Entities

### 1. Directory

파일시스템 디렉토리 경로의 생명주기를 관리하는 유틸리티 클래스.

| Field  | Type   | Description                                                               | Validation           |
| ------ | ------ | ------------------------------------------------------------------------- | -------------------- |
| `path` | `Path` | 관리 대상 디렉토리 경로 (생성자에서 `Union[str, Path]` → `Path`로 정규화) | N/A (모든 경로 허용) |

**Methods**:

| Method     | Signature                       | Returns | Description                                                                     |
| ---------- | ------------------------------- | ------- | ------------------------------------------------------------------------------- |
| `__init__` | `(path: Union[str, Path])`      | `None`  | 경로를 `Path` 객체로 정규화하여 저장                                            |
| `ensure`   | `() -> bool`                    | `bool`  | 디렉토리가 존재하지 않으면 생성 (`parents=True, exist_ok=True`). 성공 시 `True` |
| `clear`    | `(reset: bool = False) -> bool` | `bool`  | `reset=True`면 디렉토리 삭제 후 재생성. 디렉토리 존재 시 `True`                 |

**State Transitions**:

```text
[초기화] ──▶ path 저장 (Path 정규화)
   │
   ▼
[ensure()] ──▶ 디렉토리 존재 보장
   │             ├── 성공: True
   │             └── PermissionError → DirectoryPermissionError 래핑
   ▼
[clear(reset)] ──▶ 디렉토리 초기화 (선택적)
```

### 2. DirectoryPermissionError (신규)

| Field            | Type                   | Description                      |
| ---------------- | ---------------------- | -------------------------------- |
| `path`           | `str`                  | 권한 문제가 발생한 디렉토리 경로 |
| `original_error` | `Exception` (optional) | 원본 OS 예외                     |

**Hierarchy**: `DownloadError` → `DirectoryPermissionError`

**Message Format**: `"Cannot write to directory '{path}': {detail}"`

---

## Relationships

```text
Downloader ──uses──▶ Directory
                        │
                        ├── ensure()  → called in Downloader.__init__
                        └── clear()   → called optionally for reset

Directory ──raises──▶ DirectoryPermissionError (DownloadError 계열)
```

## API Contracts

이 기능에는 외부 REST/GraphQL API가 없음. `Directory` 클래스의 Python 인터페이스가 유일한 계약이며, 위 Methods 테이블이 이를 정의함. 별도 `contracts/` 디렉토리는 생성하지 않음.
