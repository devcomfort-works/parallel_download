---
description: "Task list for Filesystem Management"
---

# Tasks: Filesystem Management

**Input**: Design documents from `/specs/005-filesystem-management/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Testing is MANDATORY per Constitution Principle IV. Every feature and user story must have associated tests covering happy paths and edge cases.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 신규 에러 클래스 및 **init**.py exports 준비

- [x] T001 Add `DirectoryPermissionError` class to `src/parallel_download/errors/download_errors.py` — inherits `DownloadError`, fields: `path: str`, `original_error: Optional[Exception]`, message format: `"Cannot write to directory '{path}': {detail}"`
- [x] T002 Export `DirectoryPermissionError` in `src/parallel_download/errors/__init__.py` — add to imports and `__all__` list

---

## Phase 2: Implementation & Tests

**Purpose**: `ensure()` 메서드에 도메인 에러 래핑 적용 및 검증 (Constitution Principle III 준수)

- [x] T003 Wrap `PermissionError` in `Directory.ensure()` with `DirectoryPermissionError` in `src/parallel_download/filesystem/directory.py` — `Path.mkdir()` 호출을 try/except로 감싸고, `PermissionError` 발생 시 `DirectoryPermissionError(path, original_error)` 로 변환하여 re-raise
- [x] T004 [P] Add test `test_ensure_permission_error_raises_domain_error` in `tests/test_directory.py` — `Path.mkdir` 를 모킹하여 `PermissionError` 발생 시 `DirectoryPermissionError`로 래핑되는지 확인
- [x] T005 [P] Add test `test_ensure_on_non_existing_nested_path` in `tests/test_directory.py` — 깊은 중첩 경로(`a/b/c/d/e`)에서 `ensure()` 호출 후 디렉토리 존재 확인

**Checkpoint**: ensure()가 도메인 에러를 올바르게 래핑하고 중첩 경로를 안전하게 생성

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: exports 정비 및 최종 검증

- [x] T006 [P] Export `Directory` in `src/parallel_download/filesystem/__init__.py` — 현재 빈 파일이므로 `from .directory import Directory` 및 `__all__` 추가
- [x] T007 [P] Run `pytest tests/test_directory.py -v` to verify all new and existing tests pass
- [x] T008 Run quickstart.md validation — quickstart.md의 코드 예제를 실제로 실행하여 동작 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — 에러 클래스 신설만 수행
- **Implementation & Tests (Phase 2)**: Depends on Phase 1 (T001) — `DirectoryPermissionError`가 정의되어야 래핑 가능
- **Polish (Phase 3)**: Depends on Phase 2 — 모든 구현 완료 후 검증

### Parallel Opportunities

```text
Phase 1:  T001 ──▶ T002 (순차: __init__.py는 클래스 정의 후 export)

Phase 2:  T003 ──▶ T004 ─┬─ (병렬: 서로 다른 테스트 함수)
                   T005 ─┘

Phase 3:  T006 ─┬─ (병렬 가능)
          T007 ─┘
                ▼
          T008 (최종 검증)
```

---

## Implementation Strategy

### MVP

1. Complete Phase 1: `DirectoryPermissionError` 에러 클래스 추가 및 export
2. Complete Phase 2: `ensure()` 에러 래핑 구현 + 테스트
3. **STOP and VALIDATE**: `pytest tests/test_directory.py -v` 실행
4. Complete Phase 3: exports 정비 및 quickstart 검증

---

## Notes

- 이 기능의 핵심은 `ensure()` 내부의 `PermissionError`를 `DirectoryPermissionError`로 래핑하는 것 (Constitution Principle III)
- 기존 `ensure()`와 `clear()` 테스트는 변경 불필요 (하위 호환)
