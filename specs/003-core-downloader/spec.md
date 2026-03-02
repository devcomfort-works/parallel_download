# Feature Specification: Core Downloader

**Feature Branch**: `003-core-downloader`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: 도메인 분석 기반 명세 분리 작업. 기존 `downloader.py`의 핵심 병렬 다운로드 로직.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - 동시성 제어 지원 병렬 다운로드 (Priority: P1)

라이브러리 사용자로서, 여러 개의 파일 URL을 입력하면 지정된 최대 동시 접속 수 이내로 동시에 다운로드 되어 전체 처리 시간을 단축하고 서버 측에 과도한 부하를 주지 않기를 원한다.

**Why this priority**: 패키지의 근본적인 핵심 기능("Parallel Download").

**Independent Test**: asyncio.Semaphore가 올바르게 작동하는지, max_concurrent 매개변수에 따른 동시 요청 수를 모킹된 딜레이 서버를 통해 검증.

**Acceptance Scenarios**:

1. **Given** 10개의 다운로드 요청과 `max_concurrent=3` 설정, **When** 다운로드가 시작되면, **Then** 동시에 처리되는 요청 수는 3개를 초과하지 않는다.
2. **Given** 여러 URL 리스트, **When** 성공적으로 파일들이 시스템에 저장되면, **Then** 사용자는 각 요청에 대한 `DownloadSuccess` 응답(저장된 파일 경로 등) 리스트를 받는다.

### User Story 2 - 안정적인 예외 치환 및 통합 처리 (Priority: P1)

유저로서, 개별 파일 다운로드 중 네트워크 에러나 타임아웃 등의 오류가 발생하더라도 전체 다운로드 프로세스가 종료되지 않고 나머지 파일들은 계속 다운로드 되기를 원한다.

**Why this priority**: 병렬 처리 중 일부 에러로 인해 전체 워크플로우가 멈추지 않아야 함이 중요.

**Independent Test**: 잘못된 URL이나 타임아웃을 강제 발생시킨 후, 전체 응답 리스트에 `DownloadFailure`가 포함되고, 프로세스는 에러 없이 종료되는지 확인.

**Acceptance Scenarios**:

1. **Given** 1개의 유효한 URL과 1개의 잘못된 URL이 주어질 때, **When** 다운로드를 요청하면, **Then** 1개는 저장(Success)되고 1개는 실패(Failure) 객체로 반환된다. (Fail-safe)
2. **Given** timeout 시간을 넘기는 서버 응답 지연 요청이 있을 때, **When** 다운로드 시도 시, **Then** 해당 파일은 DownloadTimeoutError 에러를 담고 실패 처리된다.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: `Downloader` 클래스는 `max_concurrent`(최대 동시 다운로드 개수), `timeout`(요청 당 만료시간) 설정값을 제공해야 한다.
- **FR-002**: 동시성 제어를 위해 비동기 통신(e.g., `asyncio`, `aiohttp`)을 활용하여 백그라운드 태스크 방식으로 수집(Gather)해야 한다.
- **FR-003**: 다운로드 작업 단위는 `asyncio.Semaphore`를 활용하여 `max_concurrent` 개수만큼 동시 실행 제어가 강제되어야 한다.
- **FR-004**: 발생할 수 있는 내부 라이브러리 예외(`aiohttp.ClientError`, `asyncio.TimeoutError`)는 도메인 전용 에러 클래스(`NetworkError`, `DownloadTimeoutError` 등)로 추상화되어 변환되어야 한다.
- **FR-005**: 각 파일 스트림은 메모리에 전부 적재되지 않고 비동기 파일 입출력(`aiofiles`)을 통해 Chunk 단위로 디스크에 바로 써져야 한다(OOM 방지).

### Key Entities

- `Downloader`: 핵심 진입점, 내부 asyncio/aiohttp 세션을 책임짐.

## Success Criteria _(mandatory)_

- **SC-001**: 동시성 통제를 위반하지 않으며, 모든 다운로드 결과를 `DownloadResultType`의 리스트로 정확히 반환한다.
- **SC-002**: 대용량 파일 다운로드 시 메모리 초과 현상이 없어야 한다 (Chunk 단위 쓰기).
