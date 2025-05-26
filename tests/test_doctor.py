from azure_function_doctor import utils

def test_python_version():
    assert utils.check_python_version()
