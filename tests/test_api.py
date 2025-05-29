import json
import os
import tempfile

from azure_functions_doctor.api import run_diagnostics


def test_run_diagnostics_minimal() -> None:
    """Test running diagnostics with a minimal setup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("azure-functions\n")

        results = run_diagnostics(tmpdir)

        assert isinstance(results, list)
        assert any(r["check"] == "host.json version" for r in results)
        assert all("result" in r for r in results)
