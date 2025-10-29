# Standard libraries
import os


def get_bool_env(var_name: str, default: bool = False) -> bool:
    """Return boolean value from environment variable."""
    return os.getenv(var_name, str(default)).lower() in ("true", "1", "yes")
