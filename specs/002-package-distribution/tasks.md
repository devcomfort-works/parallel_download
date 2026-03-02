# Tasks: Package Distribution

**Feature**: Package Distribution
**Status**: In Progress
**Spec**: [Spec](spec.md)

## Phase 1: Setup & Configuration

_Goal: Prepare the environment and project configuration for release._

- [x] T001 Update package version to `0.1.0` in `pyproject.toml`
- [x] T002 Update `__version__` to `0.1.0` in `src/parallel_download/__init__.py`
- [x] T003 Install `twine` as a dev dependency via `rye add --dev twine`

## Phase 2: Code Quality & Coverage Assurance (US1)

_Goal: Ensure code meets Constitution standards (Coverage > 80%, Types, Style) and migrate to Ruff._

- [x] T004 [US1] Remove legacy linting dependencies (`flake8`, `black`, `isort`) via `rye remove --dev flake8 black isort`
- [x] T005 [US1] Remove `.flake8` file and clean up legacy config sections in `pyproject.toml`
- [x] T006 [US1] Configure `[tool.ruff]` in `pyproject.toml` (target-version = py38, line-length = 100)
- [x] T007 [P] [US1] Run strict type checking using `rye run mypy src`
- [x] T008 [P] [US1] Run linting and formatting using `rye lint --fix` and `rye fmt`
- [x] T009 [US1] Run test suite with coverage enforcement using `rye run pytest --cov=src/parallel_download --cov-fail-under=80`

## Phase 3: User Story 2 (Build and Verify Package)

_Goal: Produce valid distribution artifacts._

- [x] T010 [US2] Clean `dist/` directory and build new artifacts using `rye build --clean`
- [x] T011 [P] [US2] Verify artifact metadata (README rendering, license) using `rye run twine check dist/*`
- [x] T012 [P] [US2] Verify artifact installation: Create temp venv, install wheel from `dist/`, and verify import works

## Phase 4: User Story 3 (Comprehensive Documentation)

_Goal: Ensure documentation reflects the current API._

- [x] T013 [US3] Verify `README.md` "Quick Start" code works with new simplified API (No recipes)
- [x] T014 [US3] Update `README.md` badges to reflect v0.1.0 and Python versions

## Phase 5: Final Verification

_Goal: Final sanity check before merge._

- [x] T015 Perform final "clean build & check" run to ensure repeatability

## Dependencies

1. **Setup** (T001-T006) must complete before **Linting/Testing** (T008, T009).
2. **Setup** must complete before **Build** (T010).
3. **Build** (T010) must complete before **Verification** (T011, T012).

## Implementation Strategy

- **Ruff Migration First**: Prioritize swapping the toolchain to ensure subsequent checks use the new standard.
- **Sequential Execution**: Steps are largely sequential due to build dependencies.
- **Manual Verification**: T012 requires manual shell commands (creating venv) outside the standard test suite.
