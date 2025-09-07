# 핸들러 (Handlers)

이 문서는 `src/azure_functions_doctor/handlers.py`에 구현된 검사(핸들러)의 계약, 기본 제공 핸들러 설명, 어댑터 패턴 사용 예시, 확장 방법 및 테스트/디버깅 팁을 정리합니다.

## 목적

핸들러는 규칙(rule) 정의(`assets/rules/*.json`)와 실제 검사 로직을 연결합니다. 규칙은 선언적이며, 핸들러는 다음 계약을 따릅니다:

핸들러 계약(간단한 명세)
- 입력: `rule: dict` (rule 오브젝트 전체), `path: pathlib.Path` (프로젝트 루트)
- 출력: `bool` 또는 `HandlerResult`(프로젝트에는 간단한 불리언/메시지 반환을 사용)
- 실패 모드: 핸들러는 예외를 직접 노출하기보다는 실패(False)로 판단하거나, 로거에 상세 정보를 남겨야 합니다.

핸들러는 `HandlerRegistry`에 등록되어 `type` 필드로 매핑됩니다. 커스텀 핸들러는 `@handler.register("your_type")` 데코레이터로 등록할 수 있습니다.

---

## 기본 제공 핸들러 요약

다음은 저장소에 포함된 주요 핸들러와 사용 예시입니다. 구체 구현은 `src/azure_functions_doctor/handlers.py`를 참고하세요.

1) compare_version
- 설명: 버전 비교(예: Python 또는 Core Tools).
- 예시 rule:
  ```json
  {"type": "compare_version", "target": "python", "operator": ">=", "value": "3.9"}
  ```

2) file_exists
- 설명: 지정한 파일이 존재하는지 확인.
- 예시 rule:
  ```json
  {"type": "file_exists", "target": "host.json"}
  ```

3) file_contains
- 설명: 파일 내 키/문자열 존재 여부 확인. (단순 텍스트 또는 키 경로)

---

## v2에서 추가된 어댑터/유틸형 핸들러

v2 규칙집(`assets/rules/v2.json`) 에서 사용하는 경량 핸들러들입니다. 의도적으로 간단한 휴리스틱으로 구현되어 일반적인 설정 문제를 포착합니다.

- executable_exists
  - 기능: PATH 상에 실행 파일(예: `func`) 존재 확인.
  - condition 예시: `{ "target": "func" }`

- any_of_exists
  - 기능: `targets: [ ... ]` 목록 중 하나라도 존재하면 통과 (환경변수 참조, `host.json:<jsonpath>` 또는 상대 경로 파일 지원).
  - condition 예시: `{ "targets": ["requirements.txt", "Pipfile"] }`

- file_glob_check
  - 기능: 프로젝트 루트에서 glob 패턴으로 파일 검색. 민감 파일(예: .env, .pem) 또는 불필요한 아티팩트 탐지에 유용.
  - condition 예시: `{ "patterns": ["**/.env", "**/*.pem"] }`

- host_json_property
  - 기능: `host.json` 안의 단순 경로(예: `$.extensionBundle.id`) 존재 또는 값 체크.
  - condition 예시: `{ "key": "$.extensionBundle" }`

- binding_validation
  - 기능: `function.json` 기반 바인딩을 약식 검사 (예: `httpTrigger`에 `authLevel` 및 `methods` 유무 확인).
  - 목적: 심층 스키마 검증 대신 일반적인 누락/오타를 빠르게 잡음.

- cron_validation
  - 기능: `timerTrigger`의 `schedule` 문자열에 대한 휴리스틱 검사(5-혹은 6-필드 cron 형태 허용).
  - 목적: 흔한 형식 오류(필드 수, 비어있는 필드 등)를 감지.

> 주: 이들 핸들러는 전체 스키마/표준을 강제하지 않습니다. 더 엄격한 검증이 필요하면 `croniter`나 `jsonschema` 같은 라이브러리를 사용하도록 커스텀 핸들러를 작성하세요.

---

## 어댑터 패턴 사용 가이드

중복되는 로직을 줄이고 여러 규칙에서 재사용하려면 어댑터 스타일 핸들러를 작성하세요. 핵심 아이디어:
- 규칙 JSON은 간단한 조건(예: `targets`, `patterns`, `key`)만 정의합니다.
- 핸들러는 다양한 입력 형태(환경변수, 파일 경로, host.json 키 등)를 해석하여 공통 검사 함수로 위임합니다.

예: `any_of_exists`는 목록을 순회하고 각 항목에 대해 다음을 시도합니다n- 환경변수(`$ENV`) 확인
- `host.json:<path>` 구문 파싱
- 상대 경로 파일 존재 확인

성공 조건: 목록 중 하나라도 발견되면 통과.

---

## 커스텀 핸들러 작성 (간단 예시)

1. `src/azure_functions_doctor/handlers.py`에서 새로운 함수를 추가합니다.
2. `@handler.register("my_custom")` 로 타입을 등록합니다.
3. 규칙 JSON에서 `"type": "my_custom"`을 사용합니다.

간단 템플릿:

```python
# src/azure_functions_doctor/handlers.py

@handler.register("my_custom")
def _handle_my_custom(rule: dict, path: pathlib.Path) -> bool:
    condition = rule.get("condition", {})
    # ... 검사 로직 ...
    return True  # 또는 False
```

테스트 예:
```json
{
  "id": "check_my_custom",
  "section": "custom",
  "label": "My custom check",
  "type": "my_custom",
  "condition": {"key": "value"},
  "hint": "Do X if missing"
}
```

---

## 테스트 및 디버깅 팁

- 단위 테스트: `tests/test_handler.py`를 참고하여 새 핸들러의 해피패스와 실패 케이스를 추가하세요.
- 로깅: 핸들러 내부에서 `logging`을 사용해 실패 원인을 남기면 CLI의 verbose 모드에서 유용합니다.
- 성능: 파일 글로빙/대규모 검색이 필요한 핸들러는 경로 필터링을 추가해 검색 범위를 제한하세요.

---

## 예시 규칙

```json
{
  "id": "no_env_files",
  "section": "secrets",
  "label": ".env files present",
  "type": "file_glob_check",
  "condition": { "patterns": ["**/.env"] },
  "hint": "Remove secrets from repository or add to .gitignore"
}
```

---

## 확장 아이디어

- JSONPath 지원 강화: 복잡한 host.json 쿼리를 위해 `jsonpath-ng` 통합.
- Cron 엄격 검증: `croniter`를 사용해 표현식의 유효성을 검사.
- 고급 바인딩 검사: `azure-functions` 런타임 스키마에 맞춘 심층 검증.

---

더 자세한 API 레퍼런스는 `docs/api.md`의 `Handlers` 섹션에서 자동 문서화를 확인하세요.
