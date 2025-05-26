# Utility functions for the doctor tool


def check_python_version():
    import sys

    return sys.version_info >= (3, 9)
