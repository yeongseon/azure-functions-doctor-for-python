@echo off
echo 🧹 Cleaning Windows build artifacts...
for /D %%D in (*.egg-info dist build __pycache__ .pytest_cache) do (
    if exist %%D rmdir /S /Q %%D
)
