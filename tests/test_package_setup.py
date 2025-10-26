"""Smoke tests ensuring the package can be imported without side-effects."""
from __future__ import annotations

import importlib
import sys

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "python_web_tutorial",
        "python_web_tutorial.utils",
        "python_web_tutorial.utils.db",
        "python_web_tutorial.tools.bootstrap_data",
    ],
)
def test_modules_import(module_name: str) -> None:
    """Verify key modules can be imported."""
    importlib.import_module(module_name)


def test_database_config_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_HOST", "test-host")
    monkeypatch.setenv("POSTGRES_PORT", "5439")

    for module in [
        "python_web_tutorial.utils.db",
        "python_web_tutorial.utils",
    ]:
        importlib.invalidate_caches()
        sys.modules.pop(module, None)

    db_module = importlib.import_module("python_web_tutorial.utils.db")
    config = db_module.DatabaseConfig()

    assert config.host == "test-host"
    assert config.port == 5439


def test_bootstrap_cli_parsing() -> None:
    from python_web_tutorial.tools.bootstrap_data import parse_args

    args = parse_args(["--check", "--tables", "customers", "orders"])
    assert args.check is True
    assert args.tables == ["customers", "orders"]
    assert args.force is False
