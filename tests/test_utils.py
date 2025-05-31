from azure_functions_doctor.utils import format_detail, format_result, format_status_icon


def test_format_status_icon() -> None:
    """Tests the format_status_icon function for different statuses."""
    assert format_status_icon("pass") == "✔"
    assert format_status_icon("fail") == "✖"


def test_format_result() -> None:
    """Tests the format_result function for different statuses."""
    result = format_result("pass")
    assert "✔" in str(result)


def test_format_detail() -> None:
    """Tests the format_detail function for different statuses."""
    result = format_detail("fail", "missing")
    assert "missing" in str(result)
