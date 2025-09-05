## 🙺 Diagnostic Checks

This document lists diagnostic checks for **Azure Functions Doctor**, based on [Azure Functions Python Reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators) and [Best Practices](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python).

The tool supports both **Programming Model v1** (function.json-based) and **Programming Model v2** (decorator-based) projects, automatically detecting the model and applying appropriate checks.

---

## v2 Programming Model Checks (Decorator-based)

| #  | Diagnostic Check                           | Description                                                        | Status         |
| -- | ------------------------------------------ | ------------------------------------------------------------------ | -------------- |
| 1  | Python version ≥ 3.9                       | Check if the runtime meets minimum requirements for v2             | ✅ Implemented  |
| 2  | Virtual environment (.venv) active         | Ensure Python environment is isolated via virtualenv               | ✅ Implemented  |
| 3  | Python executable exists                   | Validate Python executable path                                   | ✅ Implemented  |
| 4  | `requirements.txt` exists                  | Check for dependency management file                               | ✅ Implemented  |
| 5  | `azure-functions-python-library` installed | Required for Programming Model v2 decorator syntax                 | ✅ Implemented  |
| 6  | `host.json` exists                         | Required runtime configuration file must be present                | ✅ Implemented  |
| 7  | `local.settings.json` exists (optional)    | Useful for storing app settings locally                            | ✅ Implemented  |

---

## v1 Programming Model Checks (function.json-based)

| #  | Diagnostic Check                           | Description                                                        | Status         |
| -- | ------------------------------------------ | ------------------------------------------------------------------ | -------------- |
| 1  | Python version ≥ 3.6                       | Check if the runtime meets minimum requirements for v1             | ✅ Implemented  |
| 2  | Virtual environment (.venv) active         | Ensure Python environment is isolated via virtualenv               | ✅ Implemented  |
| 3  | Python executable exists                   | Validate Python executable path                                   | ✅ Implemented  |
| 4  | `requirements.txt` exists                  | Check for dependency management file                               | ✅ Implemented  |
| 5  | `azure-functions-worker` installed         | Required for Programming Model v1 function.json syntax            | ✅ Implemented  |
| 6  | `host.json` exists                         | Required runtime configuration file must be present                | ✅ Implemented  |
| 7  | `local.settings.json` exists (optional)    | Useful for storing app settings locally                            | ✅ Implemented  |

---

## Planned Future Checks

| #  | Diagnostic Check                           | Description                                                        | v1 Support | v2 Support | Priority |
| -- | ------------------------------------------ | ------------------------------------------------------------------ | ---------- | ---------- | -------- |
| 9  | Durable Functions config in `host.json`    | Check for presence of `durableTask` section                        | ✅         | ✅         | Medium   |
| 10 | HTTP trigger validation                    | Ensure `authLevel`, `methods`, `route` in binding are valid        | ✅         | ✅         | Medium   |
| 11 | Timer trigger CRON validation              | Validate correct CRON format                                       | ✅         | ✅         | Medium   |
| 12 | App Insights configuration                 | Validate presence of instrumentation key or connection string      | ✅         | ✅         | Medium   |
| 13 | EntryPoint in `function.json` (v1 only)    | Check if entryPoint matches a real function (v1 only)              | ✅         | ❌         | Low      |
| 14 | Function name and folder match (v1 only)   | Ensure folder/function naming aligns (v1 only)                     | ✅         | ❌         | Low      |
| 15 | ASGI/WSGI compatibility                    | Check if app exposes ASGI/WSGI callable                            | ✅         | ✅         | Low      |
| 16 | Detect unused or invalid files             | Warn about `.pyc`, `__pycache__`, or legacy files                  | ✅         | ✅         | Low      |

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
