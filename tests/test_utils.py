from azure_functions_doctor import utils


def test_python_version() -> None:
    assert utils.check_python_version()
