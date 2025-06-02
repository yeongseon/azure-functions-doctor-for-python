## 🙺 Diagnostic Checks (Updated for Azure Functions Python Programming Model v2)

This document lists diagnostic checks for **Azure Functions Doctor**, based on [Azure Functions Python Reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators) and [Best Practices](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python).

| #  | Diagnostic Check                           | Description                                                        | Feasibility | Status         |
| -- | ------------------------------------------ | ------------------------------------------------------------------ | ----------- | -------------- |
| 1  | Python version ≥ 3.9                       | Check if the runtime meets minimum requirements                    | ✅ Easy      | ✅ Implemented  |
| 2  | Virtual environment (.venv) active         | Ensure Python environment is isolated via virtualenv               | ✅ Easy      | ✅ Implemented  |
| 3  | Azure Functions Core Tools installed       | Validate that `func` CLI is installed and accessible               | ✅ Easy      | ✅ Implemented  |
| 4  | `host.json` exists                         | Required runtime configuration file must be present                | ✅ Easy      | ✅ Implemented  |
| 5  | `requirements.txt` exists                  | Check for dependency management file                               | ✅ Easy      | ✅ Implemented  |
| 6  | `azure-functions` package installed        | Ensure required Azure Functions SDK is installed                   | ✅ Easy      | ✅ Implemented  |
| 7  | `azure-functions-python-library` installed | Required for Programming Model v2 decorator syntax                 | ✅ Easy      | ✅ Implemented  |
| 8  | `local.settings.json` exists (optional)    | Useful for storing app settings locally                            | ✅ Easy      | 🔧 Planned     |
| 9  | Detect use of decorators                   | Confirm use of v2-style decorators like `@function_name`           | ✅ Easy      | ✅ Implemented  |
| 10 | Function mode detection (v1 vs v2)         | Detect whether app uses function.json or decorators                | ✅ Medium    | 🔧 Planned     |
| 11 | Directory structure validation             | Warn if folder structure is non-standard or missing expected files | ✅ Easy      | ✅ Implemented  |
| 12 | Durable Functions config in `host.json`    | Check for presence of `durableTask` section                        | ✅ Medium    | 🔧 Planned     |
| 13 | HTTP trigger validation                    | Ensure `authLevel`, `methods`, `route` in binding are valid        | ✅ Medium    | 🔧 Planned     |
| 14 | Timer trigger CRON validation              | Validate correct CRON format                                       | ✅ Medium    | 🔧 Planned     |
| 15 | App Insights configuration                 | Validate presence of instrumentation key or connection string      | ✅ Medium    | 🔧 Planned     |
| 16 | EntryPoint in `function.json` (v1 only)    | Check if entryPoint matches a real function (v1 only)              | ✅ Easy      | ❌ Not needed   |
| 17 | Function name and folder match (v1 only)   | Ensure folder/function naming aligns (v1 only)                     | ✅ Easy      | ❌ Not needed   |
| 18 | ASGI/WSGI compatibility                    | Check if app exposes ASGI/WSGI callable                            | ✅ Medium    | 🔧 Planned     |
| 19 | Detect unused or invalid files             | Warn about `.pyc`, `__pycache__`, or legacy files                  | ✅ Low       | 🔝 Possible    |
| 20 | Detect long-running blocking patterns      | Detect `sleep()`, infinite loops, or sync IO blocking              | ❌ Hard      | ❌ Not feasible |
| 21 | Excessive logging                          | Detect overuse of `print()` or `logging.debug()`                   | ❌ Runtime   | ❌ Not feasible |
| 22 | Monolithic layout warning                  | Detect if everything is in one large file                          | ❌ Context   | ❌ Not feasible |

> Legend:
> ✅ Easy = statically checkable  
> ✅ Medium = requires additional parsing/context  
> ❌ = not feasible by static analysis  
> 🔧 Planned = scheduled for future implementation  
> 🧭 Possible = technically feasible but lower priority

---

### ✅ Key Changes

* Removed `main.py` check (was v1 specific)
* Added decorator detection (v2 model confirmation)
* Excluded v1-only checks like `entryPoint`, `function.json` folder matching
* Included v2-only checks like `azure-functions-python-library`
* Clarified feasibility and implementation status across all checks
