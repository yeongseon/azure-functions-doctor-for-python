# Basic Hello (Programming Model v1)

HTTP trigger Azure Function using **Programming Model v1** (`function.json` based).

## Structure
```
v1/basic-hello/
├── HttpExample/
│   ├── __init__.py
│   └── function.json
├── host.json
├── requirements.txt
├── local.settings.sample.json
└── README.md
```

## Run Locally
```bash
cd examples/v1/basic-hello
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp local.settings.sample.json local.settings.json
func start
```

Test:
```bash
curl "http://localhost:7071/api/HttpExample?name=Azure"
```

## Run Diagnostics
```bash
azure-functions doctor --path .
```

Expected differences versus v2:
* `function.json` present per function
* No decorator usage
* Different dependency expectations (may warn about worker package depending on rules)

## v1 vs v2 (Quick Comparison)
| Aspect | v1 | v2 |
|--------|----|----|
| Trigger definition | function.json | Decorators in code |
| Entry point | `entryPoint` + `scriptFile` | Function decorated | 
| Binding updates | Edit JSON | Edit Python code |
| Recommended for new apps | No | Yes |

See `examples/v2/basic-hello` for the modern structure.
