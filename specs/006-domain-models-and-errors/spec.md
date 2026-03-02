# Feature Specification: Domain Models and Errors

**Feature Branch**: `006-domain-models-and-errors`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: 도메인 분석 기반 명세. 엔티티 데이터클래스와 모든 종류의 커스텀 에러 계층 명세.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - 명확한 타입의 다운로드 요청과 응답 모델 (Priority: P2)

개발자로서, 다운로드 처리를 요청할 때는 `DownloadRequest` 단일 타입을 사용하고, 처리 결과로 반환받을 때는 성공(`DownloadSuccess`)과 실패(`DownloadFailure`) 이벤트가 명확히 분리된 모델 구조를 통해 타입 힌팅 기반의 안전한 코드를 작성하고 싶다.

**Why this priority**: Python 같은 동적 언어에서 외부 인터페이스(API)의 타입 안정성은 매우 중요하다. `mypy`나 `pyright`와 같은 정적 타입 검사기가 정확히 동작해야 한다.

**Independent Test**: 모델을 초기화 해보고, `mypy`로 해당 모델의 타입 에러가 체크되지 않는지 확인.

**Acceptance Scenarios**:

1. **Given** 결과 리스트를 반환 받은 사용자 코드, **When** `isinstance(result, DownloadSuccess)` 로 분기를 타면, **Then** 성공 시에는 파일 경로를 보장 받고, 실패 분기에서는 반드시 에러 객체를 리턴 받는다.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: 모든 핵심 입력 및 결과 모델은 Pydantic `BaseModel`을 사용하여 정의되어야 한다 (`frozen=True` 설정을 통한 불변성).
- **FR-002**: `models.request.DownloadRequest`는 최소한 대상 URL과 선택적으로 로컬 저장 시 사용할 파일명을 프로퍼티로 포함해야 한다.
- **FR-003**: `models.result.DownloadSuccess`는 성공 시의 저장 경로 및 다운로드 완료 소요 정보 등을 제공해야 한다.
- **FR-004**: 에러 처리 체계는 도메인별 기본 예외(`DownloadError`, `FilenameExtractionError`)를 상속 받는 커스텀 예외 계층 구조를 이룬다.
- **FR-005**: 예외 구조는 성격에 따라 다음처럼 세분화된다: `download_errors.py` (통신 및 스트림), `extraction_errors.py` (파일명 및 압축 문제), `validation_errors.py` (사전 검증 이슈).

### Key Entities

- `DownloadRequest`, `DownloadSuccess`, `DownloadFailure`
- Base Errors: `DownloadError` (통신 계열), `FilenameExtractionError` (추출 계열), `BulkValidationError` (검증 계열)

## Success Criteria _(mandatory)_

- **SC-001**: 코어 도메인 로직에 Python의 기본 `Exception` 이나 빌트인 예외가 직접적으로 외부 사용자에게 노출되지 않고, 정의된 도메인 에러로 반환된다.
