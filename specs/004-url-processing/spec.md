# Feature Specification: URL Processing

**Feature Branch**: `004-url-processing`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: 도메인 분석 기반 명세. URL 파싱 및 파일명 추출 로직 명세.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - URL에서 능동적 파일명 추출 (Priority: P1)

유저로서, 파일명이 지정되지 않은 URL만 입력하더라도 라이브러리가 적절한 파일명(예: HTTP Header 혹은 URL 파싱)을 알아서 추출하여 저장해주기를 원한다.

**Why this priority**: 유저는 항상 파일명을 알 수 없거나 직접 지정하기 번거로울 수 있기 때문.

**Independent Test**: `extract_filename_from_url` 함수에 파일명이 포함된 URL과 포함되지 않은 주소를 넣었을 때 정확한 파일명을 리턴하는지 `test_downloader.py` 또는 모킹 테스트를 통해 검증.

**Acceptance Scenarios**:

1. **Given** URL `http://example.com/data.csv`, **When** 파일명 추출 함수를 호출하면, **Then** `data.csv`가 반환되어야 한다.
2. **Given** URL `http://example.com/path/` (디렉토리 경로), **When** 파일명 추출 함수를 호출하면, **Then** `DirectoryPathError`가 발생해야 한다.
3. **Given** URL `http://example.com` (경로 없음), **When** 파일명 추출 함수를 호출하면, **Then** `NoPathInURLError`가 발생해야 한다.

### User Story 2 - 다양한 타입의 입력 데이터 파싱 (Priority: P2)

유저로서, `str`, `dict`, 그리고 전용 `DownloadRequest` 객체 등 다양한 형태의 입력을 리스트로 넣어도 내부적으로 통일된 다운로드 객체로 알아서 매핑해주기를 원한다.

**Why this priority**: 개발자의 편의성을 극대화하기 위해 다형적인 입력을 허용하는 것이 파이썬의 관례.

**Independent Test**: `RequestParser.parse()` 함수에 `str`, `dict`, `DownloadRequest`를 혼합해서 넣고, 결과물이 전부 `DownloadRequest` 타입인지 단위테스트로 검증.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: `url_processor/request_parser.py`는 `str` 혹은 `dict` 형태의 입력을 `DownloadRequest` 데이터클래스로 변환해야 한다.
- **FR-002**: 파싱 실패 시, 적절한 `ValidationError`를 발생시켜야 한다.
- **FR-003**: `url_processor/extract_filename_from_url.py`는 URL을 `urllib.parse`로 분석하여 마지막 경로를 확장자와 함께 파일명으로 추출해야 한다.
- **FR-004**: URL에 경로가 없거나 디렉토리를 가리키는 경우, 각각 `NoPathInURLError` 및 `DirectoryPathError`를 발생시켜야 한다.
- **FR-005**: 파일명 미지정 시 `DownloadRequest`의 `model_validator`가 URL에서 파일명을 자동 추출하여 채워야 한다.

### Key Entities

- `RequestParser`: 다형적 입력 데이터를 표준 모델로 변경
- `extract_filename_from_url`: 파일명 결정 휴리스틱 함수

## Success Criteria _(mandatory)_

- **SC-001**: 문자열 URL 리스트를 넘겨도 에러없이 정상적인 `DownloadRequest` 리스트로 파싱된다.
- **SC-002**: 어떤 형태의 정상적인 리소스 요청이든 최종적으로 저장될 '파일명'이 도출된다.
