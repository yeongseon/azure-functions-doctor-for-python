import json
import os
import tempfile

import pytest

from azure_functions_doctor.doctor import Doctor


def test_doctor_checks_pass() -> None:
    """Tests that the Doctor class runs checks and returns results."""
    with tempfile.TemporaryDirectory() as tmp:
        # Ensure v2 rules are available in package assets (no legacy rules.json)

        # Create required files
        with open(os.path.join(tmp, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmp, "requirements.txt"), "w") as f:
            f.write("azure-functions==1.13.0")

        doctor = Doctor(tmp)
        results = doctor.run_all_checks()

        assert isinstance(results, list)
        assert all("title" in section and "items" in section for section in results)

        item_map = {item["label"]: item["status"] for section in results for item in section["items"]}

        assert "Python version" in item_map
        assert item_map.get("host.json") == "pass"
        assert item_map.get("requirements.txt") == "pass"
    # local.settings.json is optional; should be present in the results and pass when missing
    assert item_map.get("local.settings.json") == "pass"


def test_missing_files() -> None:
    """Tests that the Doctor class detects missing files."""
    with tempfile.TemporaryDirectory() as tmp:
        # No rules.json copy; doctor should load v2 rules from package assets
        doctor = Doctor(tmp)
        results = doctor.run_all_checks()

        item_map = {item["label"]: item["status"] for section in results for item in section["items"]}

        assert item_map.get("host.json") == "fail"
        assert item_map.get("requirements.txt") == "fail"
    # local.settings.json is optional; missing should not cause a fail
    assert item_map.get("local.settings.json") == "pass"


def test_v2_compatibility_check() -> None:
    """Test that v2 projects (with decorators) work normally."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create a v2 project with decorators
        with open(os.path.join(tmp, "func.py"), "w") as f:
            f.write("from azure.functions import App\n@app.route('/hello')\ndef main(req):\n    return 'ok'\n")

        # Should not raise any exception
        doctor = Doctor(tmp)
        results = doctor.run_all_checks()

        # Should have normal results (no function mode check)
        assert len(results) > 0


def test_v1_incompatibility_exit() -> None:
    """Test that v1 projects (with function.json) cause the tool to exit."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create a v1 project with function.json
        os.makedirs(os.path.join(tmp, "MyFunction"), exist_ok=True)
        with open(os.path.join(tmp, "MyFunction", "function.json"), "w") as f:
            json.dump({"bindings": []}, f)

        # Should raise SystemExit
        with pytest.raises(SystemExit):
            Doctor(tmp)
