# Diagnostic Checks

This document lists potential diagnostic features for Azure Functions Doctor, based on [Azure Functions Python Reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators) and [Azure Functions Best Practices](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python). 

| #  | Diagnostic Check                             | Description                                                                 | Feasibility | Status         |
|----|----------------------------------------------|-----------------------------------------------------------------------------|-------------|----------------|
| 1  | Python version ≥ 3.9                         | Check if the runtime meets minimum requirements                            | ✅ Easy      | ✅ Implemented |
| 2  | Virtual environment (.venv) exists           | Ensure isolation of dependencies                                           | ✅ Easy      | ✅ Implemented |
| 3  | Azure Functions Core Tools installed         | Validate that `func` CLI is available                                      | ✅ Easy      | ✅ Implemented |
| 4  | host.json exists and is valid                | Ensure configuration file is present                                       | ✅ Easy      | ✅ Implemented |
| 5  | function.json exists per function            | Ensure each function folder has its own function.json                      | ✅ Easy      | ✅ Implemented |
| 6  | Directory structure validation               | Check if directory matches Azure Functions layout                          | ✅ Easy      | ✅ Implemented |
| 7  | requirements.txt or pyproject.toml present   | Check for dependency file                                                  | ✅ Easy      | 🔧 Planned     |
| 8  | local.settings.json exists                   | Verify local dev settings file exists                                      | ✅ Easy      | 🔧 Planned     |
| 9  | EntryPoint function exists                   | Ensure the entryPoint in function.json matches a real Python function      | ✅ Easy      | 🔧 Planned     |
|10  | Function name and folder match               | Ensure function directory and entryPoint are aligned                       | ✅ Easy      | 🔧 Planned     |
|11  | Durable Functions config in host.json        | Detect durableTask section for durable functions                           | ✅ Medium    | 🔧 Planned     |
|12  | HTTP trigger config validation               | Validate authLevel, route, and methods                                     | ✅ Medium    | 🔧 Planned     |
|13  | Timer trigger CRON expression validation     | Check CRON format in bindings                                              | ✅ Medium    | 🔧 Planned     |
|14  | App Insights configuration                   | Validate instrumentation key or connection string                          | ✅ Medium    | 🔧 Planned     |
|15  | Function mode detection (decorator or json)  | Detect whether function app uses decorators or function.json model         | ✅ Medium    | 🔧 Planned     |
|16  | ASGI/WSGI compatibility                      | Check if the app exposes ASGI/WSGI interfaces                              | ✅ Medium    | 🔧 Planned     |
|17  | Detect unused or invalid files               | Warn about `.pyc`, `__pycache__`, or other irrelevant files                | ✅ Low       | 🧭 Possible     |
|18  | Detect long-running code patterns            | Flag suspicious code like `time.sleep` or infinite loops                   | ❌ Hard      | ❌ Not feasible |
|19  | Excessive logging                            | Identify overuse of `print()` or `logging.debug()`                         | ❌ Runtime   | ❌ Not feasible |
|20  | Monolith vs modular layout                   | Warn if everything is in one file or single large function                 | ❌ Context   | ❌ Not feasible |

> Legend:
> ✅ Easy = statically checkable  
> ✅ Medium = requires additional parsing/context  
> ❌ = not feasible by static analysis  
> 🔧 Planned = scheduled for future implementation  
> 🧭 Possible = technically feasible but lower priority
