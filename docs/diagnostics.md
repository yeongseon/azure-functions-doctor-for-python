## 🙺 Diagnostic Checks

This document lists diagnostic checks for **Azure Functions Doctor**, based on [Azure Functions Python Reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators) and [Best Practices](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python).

The tool supports both **Programming Model v1** (function.json-based) and **Programming Model v2** (decorator-based) projects, automatically detecting the model and applying appropriate checks.

Note: Each check includes a Severity that indicates likely deployment/runtime impact:

(In the JSON rule assets `src/azure_functions_doctor/assets/rules/*.json` the same values are stored in the `severity` field: `"error"`, `"warning"`, `"info"`.)


## v2 Programming Model Checks (Decorator-based)

| #  | Diagnostic Check                           | Description                                                                                                  | Status         | Severity |
| -- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | -------------- | -------- |
| 1  | Python version (supported)                 | Verify runtime Python version is supported by Azure Functions (v2 recommends Python 3.9+ per MS docs)       | ✅ Implemented  | error    |
| 2  | Virtual environment (.venv) active         | Ensure Python environment is isolated (use virtualenv/venv for local development)                            | ✅ Implemented  | warning  |
| 3  | Python executable exists                   | Validate Python executable path is present and usable                                                       | ✅ Implemented  | error    |
| 4  | `requirements.txt` exists                  | Check for dependency file; recommend pinning critical packages and checking for incompatible packages        | ✅ Implemented  | error    |
| 5  | `azure-functions-python-library` installed | Ensure `azure.functions` package present for decorator-based programming model                              | ✅ Implemented  | error    |
| 6  | `host.json` exists                         | Ensure `host.json` is present; validate basic schema and common fields (e.g., logging, extensionBundle)      | ✅ Implemented  | error    |
| 7  | `local.settings.json` exists (optional)    | Optional local settings file for development (check presence and warn about missing common keys/SECRETS)      | ✅ Implemented  | info     |
| 8  | Azure Functions Core Tools (`func`)        | Recommend checking `func` is installed for local testing and tooling (version compatibility)                 | Planned        | warning  |
| 9  | Durable Functions config in `host.json`    | Check for `durableTask` section and that required extension/config is present                                | Planned        | error    |
| 10 | HTTP trigger validation                    | Validate HTTP trigger binding fields (`authLevel`, `methods`, `route`) and common misconfigurations         | Planned        | error    |
| 11 | Timer trigger CRON validation              | Validate `schedule` exists and CRON expression format is valid (consider second-field differences)            | Planned        | error    |
| 12 | App Insights configuration                 | Check for Application Insights settings: env vars (`APPLICATIONINSIGHTS_CONNECTION_STRING` or instrumentation key) or host.json connection | Planned        | warning  |
| 13 | extensionBundle / binding extensions       | Validate `extensionBundle` in `host.json` or presence of required binding extensions for triggers            | Planned        | error    |
| 15 | ASGI/WSGI compatibility                    | Detect whether app exposes ASGI/WSGI callable (for frameworks like FastAPI/Starlette)                         | Planned        | warning  |
| 16 | Detect unused or invalid files             | Warn about common unwanted files in project root or deployment (`.pyc`, `__pycache__`, `.venv`, tests`)      | Planned        | info     |


---

## v1 Programming Model Checks (function.json-based)

| #  | Diagnostic Check                           | Description                                                                                                  | Status         | Severity |
| -- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | -------------- | -------- |
| 1  | Python version (supported)                 | Verify runtime Python version supported by v1 projects (legacy; document recommended versions, e.g., >=3.6)  | ✅ Implemented  | error    |
| 2  | Virtual environment (.venv) active         | Ensure Python environment is isolated (use virtualenv/venv for local development)                            | ✅ Implemented  | warning  |
| 3  | Python executable exists                   | Validate Python executable path is present and usable                                                       | ✅ Implemented  | error    |
| 4  | `requirements.txt` exists                  | Check for dependency file; recommend pinning and validate azure-functions version compatibility              | ✅ Implemented  | error    |
| 5  | `azure-functions-worker` installed         | Ensure worker package for v1 function.json projects is present                                              | ✅ Implemented  | error    |
| 6  | `host.json` exists                         | Ensure `host.json` is present; validate basic schema and common fields (e.g., extensionBundle)                | ✅ Implemented  | error    |
| 7  | `local.settings.json` exists (optional)    | Optional local settings file for development (check presence and warn about missing common keys/SECRETS)      | ✅ Implemented  | info     |
| 8  | Azure Functions Core Tools (`func`)        | Recommend checking `func` is installed for local testing and tooling (version compatibility)                 | Planned        | warning  |
| 9  | Durable Functions config in `host.json`    | Check for `durableTask` section and that required extension/config is present                                | Planned        | error    |
| 10 | HTTP trigger validation                    | Validate `httpTrigger` binding fields (`authLevel`, `methods`, `route`) and `binding` correctness            | Planned        | error    |
| 11 | Timer trigger CRON validation              | Validate `schedule` exists in binding and CRON expression format is valid                                    | Planned        | error    |
| 12 | App Insights configuration                 | Check for Application Insights settings: env vars or host.json/telemetry configuration                       | Planned        | warning  |
| 13 | EntryPoint in `function.json` (v1 only)    | Verify `entryPoint` / `scriptFile` references a real module/function and is importable at runtime            | Planned        | error    |
| 14 | Function name and folder match (v1 only)   | Ensure function folder, `function.json` name and script location align                                       | Planned        | error    |
| 15 | extensionBundle / binding extensions       | Validate `extensionBundle` configuration or presence of required binding extensions (v1 binding support)    | Planned        | error    |
| 16 | Detect unused or invalid files             | Warn about common unwanted files in project root or deployment (`.pyc`, `__pycache__`, `.venv`, tests`)      | Planned        | info     |

---

## Not Feasible Checks

| #  | Diagnostic Check                           | Reason                                                            |
| -- | ------------------------------------------ | ----------------------------------------------------------------- |
| 17 | Detect long-running blocking patterns      | Requires runtime analysis, not feasible by static analysis        |
| 18 | Excessive logging                          | Requires runtime analysis, not feasible by static analysis        |
| 19 | Monolithic layout warning                  | Requires context analysis, not feasible by static analysis        |

---

### ✅ Key Features

* **Programming Model Support**: Supports both v1 and v2 projects with automatic detection
* **Model-Specific Rules**: Different requirements and checks for each programming model
* **Unified Interface**: Same CLI interface for both models with clear model indication
* **v1 Limited Support**: v1 projects show "(limited support)" warning but still get basic diagnostics
* **Rule Separation**: Separate rule sets for v1 and v2 with independent check_order management
* **Extensible Design**: Easy to add new checks for either programming model
