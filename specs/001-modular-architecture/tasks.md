---
description: "Task list for Refactor: Modularize Codebase Structure"
---

# Tasks: Refactor: Modularize Codebase Structure

**Input**: Design documents from `/specs/001-refactor-structure/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Testing is MANDATORY per Constitution Principle IV. Every feature and user story must have associated tests covering happy paths and edge cases.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create submodule directories in `src/parallel_download/`: `models`, `errors`, `url_processor`, `filesystem`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the new module structure before refactoring logic.

- [x] T002 Verify or Create `src/parallel_download/filesystem/__init__.py`
- [x] T003 Verify or Create `src/parallel_download/models/__init__.py`
- [x] T004 Verify or Create `src/parallel_download/errors/__init__.py`
- [x] T005 Verify or Create `src/parallel_download/url_processor/__init__.py`

## Phase 3: User Story 1 - Structured Module Access (Priority: P1)

**Goal**: Move code to dedicated submodules to improve maintainability.
**Independent Test criteria**: Source tree inspection confirms files are in new locations; `pylint`/`mypy` checks pass on individual modules.

### Tests

- [x] T006 [US1] Create/Update test for verify module structure (optional, can relay on manual verification)

### Implementation

- [x] T007 [P] [US1] Move/Verify `DownloadRequest` class in `src/parallel_download/models/request.py`
- [x] T008 [P] [US1] Move/Verify `DownloadResult` class in `src/parallel_download/models/result.py`
- [x] T009 [P] [US1] Move/Verify `Directory` class in `src/parallel_download/filesystem/directory.py` (Move from root directory.py)
- [x] T010 [P] [US1] Ensure `errors.py` is split into `src/parallel_download/errors/download_errors.py`, `validation_errors.py`, `extraction_errors.py`
- [x] T011 [P] [US1] Ensure URL processing logic is in `src/parallel_download/url_processor/extract_filename_from_url.py` and `request_parser.py`
- [x] T012 [P] [US1] Empty `src/parallel_download/__init__.py` exports (Implement Clean Break - remove `from .models import ...`)

## Phase 4: User Story 2 - Backward Compatible Execution (Priority: P1)

**Goal**: Update internal references and tests to ensure functionality persists.
**Independent Test criteria**: Full test suite passes.

### Tests

- [x] T013 [US2] Update test imports in `tests/test_download_request.py`, `tests/test_downloader.py`, `tests/test_directory.py` etc. to point to new submodule paths

### Implementation

- [x] T014 [US2] Update imports in `src/parallel_download/downloader.py` to use `parallel_download.models`, `parallel_download.filesystem`, etc.
- [x] T015 [US2] Update imports in `src/parallel_download/config.py` (if any dependencies exist)
- [x] T016 [US2] Run `pytest` and fix any import errors or breakages
- [x] T017 [US2] Run `mypy src/parallel_download` to ensure type consistency across new modules

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final cleanup.

- [x] T018 Update `README.md` code examples to reflect new import paths (Breaking Change documentation)
- [x] T019 Clean up any residual files in `src/parallel_download/` (e.g., old `utils.py`, `errors.py` if they still exist)

## Dependencies

- US2 depends on US1 (Code moves must happen before import fixes)

## Implementation Strategy

1. **Move & Split**: Execute US1 tasks to physically move files and split the code.
2. **Fix Internal References**: Update `downloader.py` to find the moved code.
3. **Fix External References**: Update Tests and README.
