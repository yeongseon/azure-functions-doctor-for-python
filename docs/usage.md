# 🖥️ CLI Usage: Azure Functions Doctor

Azure Functions Doctor provides a CLI to help validate and troubleshoot your Python Azure Functions project.

---

## 🔧 Basic Usage

Run the CLI from your terminal:

```bash
hatch run azfunc-doctor
```

This will display the help menu and available commands.

Or alternatively:

```bash
python -m azure_functions_doctor.cli
```

---

## 🩺 Run Diagnostics

To check your local Azure Functions setup:

```bash
hatch run azfunc-doctor diagnose
```

You can also specify options:

```bash
hatch run azfunc-doctor diagnose --format json --verbose
```

### What It Checks:

- ✅ Python version is ≥ 3.9
- ✅ `.venv` directory exists
- ✅ Azure Functions Core Tools (`func`) is installed
- ✅ `host.json` and `function.json` are valid
- ✅ Expected directory structure is present
- ⚠️ Optional files like `requirements.txt` (future support)

---

## 🆘 Help

To view available options and subcommands:

```bash
hatch run azfunc-doctor --help
hatch run azfunc-doctor diagnose --help
```

---

## 💡 Example Output

```bash
$ hatch run azfunc-doctor diagnose
                             Azure Function Diagnostics                             
                                                                                   
  Check              Result    Detail                                               
 ───────────────────────────────────────────────────────────────────────────────── 
  Python version     ✅ PASS   3.12.3                                               
  host.json          ❌ FAIL   [Errno 2] No such file or directory: './host.json'  
  requirements.txt   ❌ FAIL   Not found                                            
```
