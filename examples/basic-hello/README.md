# 🔪 Basic Hello Function

This is a minimal Azure Function example with an HTTP trigger.

## 📁 Structure

```
.
├── HttpExample/
├── host.json
└── requirements.txt
```

## 🚀 Run Locally

1. Create and activate a virtual environment:

```bash
cd examples/basic-hello
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install azure-functions-doctor  # Local test only
```

3. Start the function:

```bash
func start
```

## 🩺 Diagnostics Output

Run the CLI in the same environment:

```bash
$ hatch run azfunc-doctor diagnose

         Azure Function Diagnostics          
                                             
  Check               Result    Detail       
 ─────────────────────────────────────────── 
  Python version      ✅ PASS   3.12.3       
  host.json version   ✅ PASS   version=2.0  
  requirements.txt    ✅ PASS   Found        
```
