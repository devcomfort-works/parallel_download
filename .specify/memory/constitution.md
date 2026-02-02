<!--
SYNC IMPACT REPORT
Version: 1.0.0 (Initial Ratification)
Status: ✅ Constitution Established

Changes:
- Defined Project Name: Parallel Download
- Principle I: Type Safety First (Added)
- Principle II: Asynchronous By Design (Added)
- Principle III: Explicit Error Handling (Added)
- Principle IV: Comprehensive Testing (Added)
- Principle V: Code Style Consistency (Added)
- Development Standards: Python 3.8+, Rye, Minimal Deps
- Documentation Standards: Mandatory docstrings
- Governance: Initial ratification

Impact Analysis:
- .specify/templates/tasks-template.md: ✅ UPDATED (Tests marked Mandatory)
- .specify/templates/plan-template.md: ✅ Compatible (Constitution Gates will now populate)
- .specify/templates/spec-template.md: ✅ Compatible
-->

# Parallel Download Constitution

## Core Principles

### I. Type Safety First

The codebase relies on static analysis to prevent runtime errors. All code MUST be fully type-hinted. `mypy` strict mode should pass without errors. Explicit types are required; use of `Any` is strongly discouraged and must be justified.

### II. Asynchronous By Design

I/O operations (network, file system) MUST be non-blocking. The architecture utilizes `asyncio` for concurrency. Use `aiohttp` for network requests and `aiofiles` for file I/O. Blocking calls in async paths are prohibited.

### III. Explicit Error Handling

Silent failures are forbidden. Operations must return structured result objects (e.g., `DownloadSuccess`, `DownloadFailure`) or raise specific, semantic exception classes. Errors must be traceable and actionable by the consumer.

### IV. Comprehensive Testing

**NON-NEGOTIABLE:** All features and bug fixes MUST include tests. Test coverage should cover happy paths, edge cases, and error scenarios. Passing the full test suite is a requirement for merging.

### V. Code Style Consistency

Code must strictly adhere to the project's formatting and linting rules.

- Format with `black`.
- Sort imports with `isort`.
- Lint with `flake8`.
- Commit hooks should ensure these standards are met before push.

## Development Standards

### Technology Stack

- **Language**: Python 3.8+
- **Dependency Management**: `rye` is the authoritative tool for package management.
- **Dependencies**: Keep dependencies minimal. Prefer standard library unless a package offers significant correctness or performance benefits (e.g., `pydantic`, `loguru`).

### Performance & Security

- **Concurrency**: Use semaphores to limit concurrent operations and prevent resource exhaustion.
- **Validation**: Validate all external inputs (URLs, file paths) at the boundary using `pydantic` or strict parsing logic.

## Documentation Requirements

### Public API

All public modules, classes, and methods MUST have docstrings resembling Google or NumPy style.

### Runtime Guidance

- **README**: Must be kept in sync with code changes using the `speckit` flow.
- **Usage Examples**: New features must include usage examples in documentation or `quickstart.md`.

## Governance

This constitution defines the non-negotiable rules for the _Parallel Download_ project.

- **Supremacy**: These principles supersede individual preferences or ad-hoc decisions.
- **Amendments**: Changes to this constitution require a formal Pull Request, explicitly labeled as a Governance change, and must include a Sync Impact Report.
- **Compliance**: All PRs must verify compliance with these principles. CI pipelines will enforce automated checks (Types, Linting, Tests).

**Version**: 1.0.0 | **Ratified**: 2026-02-02 | **Last Amended**: 2026-02-02
