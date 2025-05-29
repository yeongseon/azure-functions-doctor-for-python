import json
import os
import tempfile

from azure_functions_doctor.doctor import Doctor


def test_check_python_version() -> None:
    """Test the Python version check."""
    doctor = Doctor(".")
    result = doctor.check_python_version()
    assert result["check"] == "Python version"
    assert result["result"] in {"pass", "fail"}


def test_check_host_json_pass() -> None:
    """Test the host.json check for a valid version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        doctor = Doctor(tmpdir)
        result = doctor.check_host_json()
        assert result["result"] == "pass"


def test_check_requirements_txt_fail() -> None:
    """Test the requirements.txt check when the file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        doctor = Doctor(tmpdir)
        result = doctor.check_requirements_txt()
        assert result["result"] == "fail"
