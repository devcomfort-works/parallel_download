# Feature Specification: Filesystem Management

**Feature Branch**: `005-filesystem-management`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: 도메인 분석 기반 명세. 시스템 내 파일 읽기 및 쓰기 권한, 디렉토리 제어 모듈 명세.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - 동적 출력 디렉토리 생성 (Priority: P2)

설치 관리자로서, 다운로더가 호출될 때 다운로드를 지시한 대상 디렉토리가 존재하지 않는다면, 프로그램이 에러를 발생시키지 않고 스스로 폴더(및 상위 폴더)를 생성하여 다운로드를 준비해주기를 원한다.

**Why this priority**: 파일 파이프라인의 시작은 안전한 저장 공간을 확보하는 것.

**Independent Test**: 존재하지 않는 서브 디렉토리(예: `/tmp/a/b/c`)를 지정하여 Downloader를 초기화했을 때, 해당 경로가 성공적으로 만들어졌는지 확인.

**Acceptance Scenarios**:

1. **Given** 존재하지 않는 출력 디렉토리 경로, **When** `Downloader` 초기화 시, **Then** `os.makedirs(exist_ok=True)`와 동일한 방식으로 모든 중간 디렉토리가 생성된다.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: `filesystem.directory.Directory` 객체는 다운로드 디렉토리 경로를 관리해야 한다. [✅ Implemented]
- **FR-002**: `ensure()` 메서드를 통해 초기화 단계에서 주어진 경로가 실제로 시스템 상에 존재하도록 만들어야 한다. [✅ Implemented]
- **FR-003**: `ensure()` 실행 중 `PermissionError` 발생 시 `DirectoryPermissionError`로 래핑하여 도메인 에러로 전환해야 한다. [✅ Implemented]

### Non-Functional Requirements

- **NFR-001**: `pathlib.Path` 기반으로 POSIX 및 Windows에서 동일하게 동작해야 한다.

### Key Entities

- `Directory`: 파일 시스템 디렉토리 경로의 생명주기를 캡슐화하는 클래스

## Success Criteria _(mandatory)_

- **SC-001**: 상대 경로, 절대 경로, 복잡한 트리 구조의 디렉토리가 주어져도 다운로드 전에 안전하게 생성될 수 있다.
