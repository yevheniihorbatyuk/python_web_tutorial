"""CLI утиліта для ініціалізації навчальної бази даних."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from psycopg2 import sql

from python_web_tutorial.utils.db import DatabaseConfig, get_cursor, table_exists

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INIT_SQL = DATA_DIR / "init.sql"
SAMPLE_DATA_SQL = DATA_DIR / "sample_data.sql"
DEFAULT_TABLES = [
    "customers",
    "orders",
    "order_items",
    "products",
]


def _read_statements(path: Path) -> Iterable[str]:
    raw = path.read_text(encoding="utf-8")
    for statement in raw.split(";"):
        cleaned = statement.strip()
        if cleaned:
            yield cleaned


def _apply_sql_file(path: Path, *, config: DatabaseConfig) -> None:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    with get_cursor(config) as cursor:
        for statement in _read_statements(path):
            cursor.execute(statement)


def _count_rows(table: str, *, config: DatabaseConfig) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(table))
    with get_cursor(config) as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
        return int(result[0]) if result else 0


def _table_status(*, config: DatabaseConfig, tables: Iterable[str]) -> dict[str, int]:
    status: dict[str, int] = {}
    for table in tables:
        if table_exists(table, config=config):
            status[table] = _count_rows(table, config=config)
        else:
            status[table] = -1
    return status


def bootstrap(*, force: bool, config: DatabaseConfig) -> None:
    print("🛠️  Applying schema from init.sql ...")
    _apply_sql_file(INIT_SQL, config=config)

    existing_rows = _table_status(config=config, tables=["customers"])['customers']
    if existing_rows > 0 and not force:
        print("ℹ️  Sample data already present — skipping sample_data.sql")
        return

    print("🪄 Loading sample_data.sql ...")
    _apply_sql_file(SAMPLE_DATA_SQL, config=config)
    print("✅ Sample data loaded")


def check_status(*, config: DatabaseConfig, tables: Iterable[str]) -> None:
    status = _table_status(config=config, tables=tables)
    for table, count in status.items():
        if count == -1:
            print(f"❌ {table}: table is missing")
        else:
            print(f"✅ {table}: {count} rows")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Лише перевірити стан таблиць, не виконуючи SQL скрипти.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Повторно завантажити демонстраційні дані навіть якщо вони вже існують.",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        default=DEFAULT_TABLES,
        help="Список таблиць для перевірки стану.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = DatabaseConfig()

    try:
        if args.check:
            check_status(config=config, tables=args.tables)
            return 0

        bootstrap(force=args.force, config=config)
        check_status(config=config, tables=args.tables)
        return 0
    except Exception as exc:  # pragma: no cover - CLI surface for learners
        print(f"❌ Bootstrap failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
