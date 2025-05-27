"""Utility functions for Azure Functions Doctor.

Provides helper routines for environment and version checks.
"""

# Utility functions for the doctor tool


def check_python_version() -> bool:
    """Check if the current Python version is 3.9 or higher."""
    import sys

    return sys.version_info >= (3, 9)
