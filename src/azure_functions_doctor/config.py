"""Configuration management for Azure Functions Doctor."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)


class Config:
    """Centralized configuration management with environment variable support."""

    # Default configuration values
    _defaults = {
        "log_level": "WARNING",
        "log_format": "simple",
        "max_file_size_mb": 10,
        "search_timeout_seconds": 30,
        "rules_file": "rules.json",
        "output_width": 120,
        "enable_colors": True,
        "parallel_execution": False,
    }

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._load_defaults()
        self._load_from_environment()

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config.update(self._defaults)
        logger.debug("Loaded default configuration")

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables with FUNC_DOCTOR_ prefix."""
        env_prefix = "FUNC_DOCTOR_"

        for key, default_value in self._defaults.items():
            env_key = f"{env_prefix}{key.upper()}"
            env_value = os.getenv(env_key)

            if env_value is not None:
                # Type conversion based on default value type
                if isinstance(default_value, bool):
                    self._config[key] = env_value.lower() in ("true", "1", "yes", "on")
                elif isinstance(default_value, int):
                    try:
                        self._config[key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_key}: {env_value}")
                elif isinstance(default_value, float):
                    try:
                        self._config[key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Invalid float value for {env_key}: {env_value}")
                else:
                    self._config[key] = env_value

                logger.debug(f"Loaded {key}={self._config[key]} from environment")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        old_value = self._config.get(key)
        self._config[key] = value
        logger.debug(f"Configuration changed: {key}={old_value} -> {value}")

    def get_log_level(self) -> str:
        """Get logging level."""
        return str(self._config["log_level"])

    def get_log_format(self) -> str:
        """Get logging format style."""
        return str(self._config["log_format"])

    def get_max_file_size_mb(self) -> int:
        """Get maximum file size for processing in MB."""
        return int(self._config["max_file_size_mb"])

    def get_search_timeout_seconds(self) -> int:
        """Get search operation timeout in seconds."""
        return int(self._config["search_timeout_seconds"])

    def get_rules_file(self) -> str:
        """Get rules file name."""
        return str(self._config["rules_file"])

    def get_output_width(self) -> int:
        """Get output width for formatting."""
        return int(self._config["output_width"])

    def is_colors_enabled(self) -> bool:
        """Check if color output is enabled."""
        return bool(self._config["enable_colors"])

    def is_parallel_execution_enabled(self) -> bool:
        """Check if parallel execution is enabled."""
        return bool(self._config["parallel_execution"])

    def get_custom_rules_path(self) -> Optional[Path]:
        """Get custom rules file path from environment."""
        custom_path = os.getenv("FUNC_DOCTOR_CUSTOM_RULES")
        if custom_path:
            path = Path(custom_path)
            if path.exists():
                return path
            logger.warning(f"Custom rules path does not exist: {custom_path}")
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def override_config(**kwargs: Any) -> None:
    """Override configuration values (useful for testing)."""
    for key, value in kwargs.items():
        config.set(key, value)
