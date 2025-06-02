import json
import os
import shutil
import tempfile
from importlib.resources import files

from azure_functions_doctor.api import run_diagnostics


def test_run_diagnostics_minimal() -> None:
    """Test running diagnostics with a minimal setup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rules_path = files("azure_functions_doctor.assets").joinpath("rules.json")
        shutil.copy(str(rules_path), os.path.join(tmpdir, "rules.json"))

        with open(os.path.join(tmpdir, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("azure-functions\n")

        results = run_diagnostics(tmpdir)

        assert isinstance(results, list)
        assert all("title" in section and "items" in section for section in results)

        host_check_found = any(
            any("host.json" in item.get("label", "") for item in section["items"]) for section in results
        )
        assert host_check_found, "Expected 'host.json' check not found in results"
