from _pytest.capture import CaptureFixture

from azure_functions_doctor import doctor
from azure_functions_doctor.doctor import run_diagnostics


def test_dummy_check() -> None:
    assert hasattr(doctor, "run_diagnostics")


def test_run_diagnostics_prints_output(capsys: CaptureFixture[str]) -> None:
    run_diagnostics()
    captured = capsys.readouterr()
    assert "Azure Function Doctor is running" in captured.out
