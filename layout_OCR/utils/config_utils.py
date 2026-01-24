from __future__ import annotations

import configparser
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def load_config(path: str | None) -> configparser.ConfigParser | None:
    if not path:
        return None
    config = configparser.ConfigParser()
    config.read(Path(path))
    return config


def get_config_value(
    config: configparser.ConfigParser | None,
    section: str,
    key: str,
    default: T,
    cast: Callable[[str], T],
) -> T:
    if config is None:
        return default
    if not config.has_option(section, key):
        return default
    value = config.get(section, key)
    if value == "":
        return default
    return cast(value)


def to_bool(value: str) -> bool:
    value = value.strip().lower()
    return value in {"1", "true", "yes", "y", "on"}
