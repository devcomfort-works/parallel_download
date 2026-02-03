# Research: Release Prep & Ruff Migration

## 1. Ruff Migration Strategy (FR-007)

- **Goal**: Replace `flake8`, `black`, `isort` with `ruff` for linting and formatting.
- **Context**: `rye` uses `ruff` internally.
- **Implementation**:
  - **Dependencies**: Remove `flake8`, `black`, `isort`. Add `ruff`.
  - **Configuration**:
    - Add `[tool.ruff]` to `pyproject.toml`.
    - Set `line-length = 100` (matching previous config).
  - **Cleanup**: Delete `.flake8`. Remove `[tool.black]` and `[tool.isort]` from `pyproject.toml`.

## 2. Build System Validation

- **Goal**: Confirm `rye` commands for building.
- **Findings**: `rye build` invokes `hatchling`.
- **Decision**: Use `rye build --clean`.

## 3. Metadata Verification

- **Goal**: Verify package metadata.
- **Decision**: Add `twine` as dev dependency. Run `twine check dist/*`.

## 4. Coverage Analysis

- **Goal**: Enforce 80% coverage.
- **Decision**: `rye run pytest --cov=src/parallel_download --cov-fail-under=80`.

## 5. Versioning

- **Goal**: Set version to `0.1.0`.
- **Decision**: Update `pyproject.toml` and `src/parallel_download/__init__.py`.
