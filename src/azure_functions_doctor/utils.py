from rich.style import Style
from rich.text import Text

# Status to icon
STATUS_ICONS: dict[str, str] = {
    "pass": "✔",
    "fail": "✖",
    "warn": "⚠",
}

# Status to styled Text (for section headers)
STATUS_STYLES: dict[str, Style] = {
    "pass": Style(color="green", bold=True),
    "fail": Style(color="red", bold=True),
    "warn": Style(color="yellow", bold=True),
}

# Status to plain color strings (for result details)
DETAIL_COLOR_MAP: dict[str, str] = {
    "pass": "green",
    "fail": "red",
    "warn": "yellow",
}


def format_status_icon(status: str) -> str:
    """
    Return a simple icon character based on status.

    Args:
        status: Diagnostic status ("pass", "fail", "warn").

    Returns:
        A string icon such as ✔, ✖, or ⚠.
    """
    return STATUS_ICONS.get(status, "?")


def format_result(status: str) -> Text:
    """
    Return a styled icon Text element based on status.

    Args:
        status: Diagnostic status ("pass", "fail", "warn").

    Returns:
        A Rich Text object with icon and style for headers.
    """
    style = STATUS_STYLES.get(status, Style(color="white"))
    icon = format_status_icon(status)
    return Text(icon, style=style)


def format_detail(status: str, value: str) -> Text:
    """
    Return a colored Text element based on status and value.

    Args:
        status: Diagnostic status ("pass", "fail", "warn").
        value: Text to display, typically a description.

    Returns:
        A Rich Text object styled with status color.
    """
    color = DETAIL_COLOR_MAP.get(status, "white")
    return Text(value, style=color)
