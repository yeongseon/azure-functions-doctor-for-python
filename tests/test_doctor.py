import json
import os
import tempfile

from azure_functions_doctor.doctor import Doctor
from azure_functions_doctor.result import DiagnosticResult


def test_doctor_checks_pass() -> None:
    """Checks that the Doctor runs all checks and returns results."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create required files
        with open(os.path.join(tmp, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmp, "requirements.txt"), "w") as f:
            f.write("azure-functions==1.13.0")

        doctor = Doctor(tmp)
        results = doctor.run_all_checks()

        assert isinstance(results, list)
        assert all(isinstance(r, DiagnosticResult) for r in results)
        assert any(r.check == "Python version" for r in results)
        assert any(r.check == "host.json version" and r.result == "pass" for r in results)
        assert any(r.check == "requirements.txt" and r.result == "pass" for r in results)


def test_missing_files() -> None:
    """Checks that missing files are detected as failures."""
    with tempfile.TemporaryDirectory() as tmp:
        doctor = Doctor(tmp)
        results = doctor.run_all_checks()

        result_dict = {r.check: r.result for r in results}

        assert result_dict["host.json"] == "fail"
        assert result_dict["requirements.txt"] == "fail"
