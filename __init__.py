"""Top-level package for the Python Web tutorial project."""

from importlib.metadata import version, PackageNotFoundError

__all__ = ["utils"]

try:  # pragma: no cover - best effort metadata lookup
    __version__ = version("python-web-tutorial")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"
