# 📘 Rules Documentation

Azure Functions Doctor uses a modular rules system to define diagnostic checks declaratively. The tool now supports both **Programming Model v1** and **v2** with separate rule sets for each model.

Each rule specifies what to validate, how to validate it, and what to show when the check passes or fails — without modifying the core Python code. This makes the tool extensible and customizable.

---

## 📁 Location

The rules are organized in separate files under the **assets/rules/** directory:

```
src/
└── azure_functions_doctor/
    └── assets/
      └── rules/
        ├── v1.json         👈 v1 Programming Model rules
        └── v2.json         👈 v2 Programming Model rules
```

### Rule File Selection

The tool automatically selects the appropriate rule file based on the detected programming model:

- **v1 projects**: Uses `v1.json` (function.json-based projects)
- **v2 projects**: Uses `v2.json` (decorator-based projects)  
Rules are read from the `assets/rules/v1.json` or `assets/rules/v2.json` files depending on the detected programming model. Legacy `rules.json` support has been removed.

---

## ⌐ Structure of a Rule

Each rule is a JSON object with the following fields:

```json
{
  "id": "check_python_version",
  "section": "python_env",
  "label": "Python version",
  "type": "compare_version",
  "target": "python",
  "operator": ">=",
  "value": "3.9",
  "hint": "Install Python 3.9 or higher."
}
```

### 🔑 Fields Explained

| Field      | Type   | Description                                          |
| ---------- | ------ | ---------------------------------------------------- |
| `id`       | string | Unique identifier for the rule                       |
| `section`  | string | Logical group (e.g. `python_env`, `config_files`)    |
| `label`    | string | Human-readable label for the check                   |
| `type`     | string | Rule type (see below)                                |
| `target`   | string | Subject to evaluate (e.g. Python version, file path) |
| `operator` | string | Comparison operator (e.g. `==`, `!=`, `>=`)          |
| `value`    | any    | Expected value to compare                            |
| `hint`     | string | Suggestion if the rule fails                         |

---

## Supported Rule Types

### 1. `compare_version`

Compare semantic versions.

```json
{
  "type": "compare_version",
  "target": "python",
  "operator": ">=",
  "value": "3.9"
}
```

* Valid `target`: `"python"`, `"azure-functions-core-tools"`

---

### Additional rule types (v2 additions)

The project also includes several adapter-style and higher-level validation checks used by the default `v2.json` ruleset:

- `executable_exists` — verifies an executable is available on PATH (condition: `{"target": "func"}` or similar).
- `any_of_exists` — accepts `targets: [ ... ]` and passes if any listed target exists (supports env vars, host.json keys via `host.json:<path>`, or relative file paths).
- `file_glob_check` — searches the project for files matching provided glob `patterns` (useful to flag unwanted files like secrets or build artifacts).
- `host_json_property` — lightweight check for presence of a property in `host.json` using a simple JSON pointer string (e.g. `"$.extensionBundle"`).
- `binding_validation` — shallow validation of `function.json` bindings (e.g. ensures `httpTrigger` bindings declare `authLevel` and have `methods` where expected).
- `cron_validation` — heuristic validation for `timerTrigger` `schedule` expressions found in `function.json` (accepts 5- or 6-field cron-like strings).

These checks are implemented as adapters in `src/azure_functions_doctor/handlers.py` and are intentionally lightweight: they cover common misconfigurations without attempting full schema validation. If you need stricter validation, consider adding a custom handler or extending the existing one.

---

### 2. `file_exists`

Check whether a file exists.

```json
{
  "type": "file_exists",
  "target": "host.json"
}
```

---

### 3. `file_contains`

Check whether a file contains a specific string or key path.

```json
{
  "type": "file_contains",
  "target": "host.json",
  "key_path": ["version"],
  "value": "2.0"
}
```

---

### 4. `custom`

You may register custom handlers in code using the `@handler.register("your_type")` decorator. Add a `"type": "custom"` field and let your handler interpret additional keys under `condition`.

---

## 📁 Grouping by `section`

Sections allow grouping related checks together for better readability in the CLI output:

Example:

```json
{
  "section": "python_env",
  "label": "Python Version",
  ...
}
```

Predefined sections might include:

* `python_env`
* `core_tools`
* `config_files`
* `dependencies`
* `network`

You can create your own section names if desired.

---

## 🧹 Extending the Rules

To add a new rule:

### For v2 Projects (Recommended)
1. Open `src/azure_functions_doctor/assets/rules/v2.json`
2. Append your rule object to the array
3. Save and rerun `azure-functions doctor`

### For v1 Projects
1. Open `src/azure_functions_doctor/assets/rules/v1.json`
2. Append your rule object to the array
3. Save and rerun `azure-functions doctor`

### For Universal Rules
If you want a rule to apply to both v1 and v2 projects, you'll need to add it to both files with appropriate model-specific configurations.

Example:

```json
{
  "id": "check_requirements_txt_exists",
  "section": "dependencies",
  "label": "requirements.txt exists",
  "type": "file_exists",
  "target": "requirements.txt",
  "hint": "Create a requirements.txt file to declare Python dependencies."
}
```

---

## Tips

* Use `hint` to provide helpful, actionable suggestions.
* Use consistent `section` names for better CLI grouping.
* If you're writing custom rule types, register them in `handlers.py`.

---

## 🥪 Testing Your Changes

After editing `v1.json` or `v2.json`, you can run:

```bash
azure-functions doctor --verbose
```

To see grouped results and hints.

---

## 📟 Example `rules.json` (simplified)

```json
[
  {
    "id": "check_python_version",
    "section": "python_env",
    "label": "Python version",
    "type": "compare_version",
    "target": "python",
    "operator": ">=",
    "value": "3.9",
    "hint": "Install Python 3.9 or higher."
  },
  {
    "id": "check_host_json_exists",
    "section": "config_files",
    "label": "host.json exists",
    "type": "file_exists",
    "target": "host.json"
  }
]
```

---

## 📬 Contribute New Rules

Want to improve the default rules? Feel free to open a PR or discussion on  
👉 [GitHub Repository](https://github.com/yeongseon/azure-functions-doctor-for-python)