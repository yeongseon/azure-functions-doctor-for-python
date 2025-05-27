@echo off
echo 🧹 Cleaning all Python artifacts and virtual environment...

REM Remove .venv
if exist .venv rmdir /S /Q .venv

REM Remove all __pycache__ directories
for /R %%D in (__pycache__) do (
    if exist %%D rmdir /S /Q %%D
)

REM Remove all .pyc / .pyo files
for /R %%F in (*.pyc *.pyo) do (
    if exist %%F del /Q %%F
)

REM Remove caches and coverage files
if exist .mypy_cache rmdir /S /Q .mypy_cache
if exist .ruff_cache rmdir /S /Q .ruff_cache
if exist .pytest_cache rmdir /S /Q .pytest_cache
if exist .coverage del /Q .coverage
if exist coverage.xml del /Q coverage.xml
if exist .DS_Store del /Q .DS_Store
