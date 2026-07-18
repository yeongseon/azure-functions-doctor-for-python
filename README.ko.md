# Azure Functions Doctor

[![PyPI](https://img.shields.io/pypi/v/azure-functions-doctor.svg)](https://pypi.org/project/azure-functions-doctor/)
[![Downloads](https://static.pepy.tech/badge/azure-functions-doctor/month)](https://pepy.tech/project/azure-functions-doctor)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-doctor/)
[![CI](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/ci-test.yml)
[![Release](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/publish-pypi.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-doctor-python/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-doctor-python/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-doctor-python)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-doctor-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

다른 언어: [English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

Azure Functions Doctor는 **Azure Functions Python v2 프로그래밍 모델**로 구축된 프로젝트를 위한 진단 CLI 도구입니다.

이 도구는 로컬 프로젝트에서 다음과 같은 일반적인 문제들을 점검합니다:

- 지원되지 않는 Python 버전
- `host.json` 또는 `requirements.txt` 누락
- `azure-functions` 의존성 누락
- 가상 환경(virtual environments) 누락
- Azure Functions Core Tools 누락
- 불완전한 로컬 개발 환경 설정

## Why Use It

Azure Functions Python 프로젝트를 설정하려면 여러 설정 파일, 의존성, 도구가 필요합니다. 그 중 하나라도 빠지면 이해하기 어려운 런타임 오류가 발생합니다. `azure-functions-doctor`는 엄선된 규칙 집합을 기반으로 프로젝트를 점검하고, 문제가 프로덕션에 도달하기 전에 보고합니다.

## Scope

이 리포지토리는 데코레이터 기반의 Azure Functions Python v2 프로그래밍 모델만을 대상으로 합니다.

- 지원되는 모델: `@app.route()`와 같은 데코레이터를 사용하는 `func.FunctionApp()`
- 지원되지 않는 모델: 기존 `function.json` 기반의 Python v1 프로젝트

## Installation

PyPI에서 설치:

```bash
pip install azure-functions-doctor
```

소스에서 설치:

```bash
git clone https://github.com/yeongseon/azure-functions-doctor-python.git
cd azure-functions-doctor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

현재 프로젝트에서 doctor 실행:

```bash
azure-functions doctor
```

특정 프로젝트 경로에서 실행:

```bash
azure-functions doctor --path ./examples/v2/http-trigger
```

필수 항목만 점검하는 프로필 사용:

```bash
azure-functions doctor --profile minimal
```

CI를 위한 JSON 출력:

```bash
azure-functions doctor --format json
```

## Demo

아래 데모는 VHS를 사용하여 [`demo/doctor-demo.tape`](demo/doctor-demo.tape)에서 생성되었습니다.
대표적인 예시 프로젝트와 의도적으로 오류를 발생시킨 복사본에 대해 실제 `azure-functions doctor` CLI를 실행하여 성공/실패 대비를 보여줍니다.

![Doctor demo](docs/assets/doctor-demo.gif)

최종 터미널 상태는 빠른 확인을 위해 정지 이미지로도 캡처되었습니다.

![Doctor final output](docs/assets/doctor-demo-final.png)

## Features

기본 규칙 집합은 다음 사항들을 검증합니다:

- Azure Functions Python v2 데코레이터 사용 여부
- Python 버전
- 가상 환경 활성화 여부
- Python 실행 파일 사용 가능 여부
- `requirements.txt`
- `azure-functions` 의존성 선언
- `host.json`
- `local.settings.json` (선택 사항)
- Azure Functions Core Tools 존재 및 버전 (선택 사항)
- Durable Functions 호스트 설정 (선택 사항)
- Application Insights 설정 (선택 사항)
- `extensionBundle` 설정 (선택 사항)
- ASGI/WSGI callable 노출 (선택 사항)
- 프로젝트 트리 내의 일반적인 불필요한 파일 (선택 사항)

## Examples

- [examples/v2/http-trigger/README.md](examples/v2/http-trigger/README.md)
- [examples/v2/multi-trigger/README.md](examples/v2/multi-trigger/README.md)

## Requirements

- Python 3.10+
- 개발 워크플로우를 위한 Hatch
- 로컬 실행을 위해 Azure Functions Core Tools v4+ 권장

## Documentation

- [docs/index.md](docs/index.md)
- [docs/usage.md](docs/usage.md)
- [docs/rules.md](docs/rules.md)
- [docs/diagnostics.md](docs/diagnostics.md)
- [docs/development.md](docs/development.md)

## Ecosystem

- [azure-functions-validation](https://github.com/yeongseon/azure-functions-validation) — 요청 및 응답 검증
- [azure-functions-openapi](https://github.com/yeongseon/azure-functions-openapi) — OpenAPI 및 Swagger UI
- [azure-functions-langgraph](https://github.com/yeongseon/azure-functions-langgraph) — LangGraph 배포 어댑터
- [azure-functions-logging](https://github.com/yeongseon/azure-functions-logging) — 구조화된 로깅
- [azure-functions-scaffold](https://github.com/yeongseon/azure-functions-scaffold) — 프로젝트 스캐폴딩
- [azure-functions-durable-graph](https://github.com/yeongseon/azure-functions-durable-graph) — Durable Functions 기반 그래프 런타임 *(계획)*
- [azure-functions-python-cookbook](https://github.com/yeongseon/azure-functions-python-cookbook) — 레시피 및 예제

## Disclaimer

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 Microsoft와 제휴되어 있지 않고, Microsoft의 후원이나 유지보수를 받지 않습니다.

Azure 및 Azure Functions는 Microsoft Corporation의 상표입니다.

## License

MIT
