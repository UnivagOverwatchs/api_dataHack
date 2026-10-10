from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from app.config import get_settings

settings = get_settings()
engine: Engine = create_engine(settings.database_url, pool_pre_ping=True)


def test_connection() -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": settings.db_name}
    except Exception as exc:  # pragma: no cover - depends on DB availability
        return {"status": "error", "database": settings.db_name, "message": str(exc)}


def list_tables() -> list[str]:
    with engine.connect() as conn:
        inspector = inspect(conn)
        tables: list[str] = []

        for schema in inspector.get_schema_names():
            if schema in {"pg_catalog", "information_schema"}:
                continue
            for table in inspector.get_table_names(schema=schema):
                tables.append(f"{schema}.{table}")

        if not tables:
            tables = inspector.get_table_names()

        return tables


def fetch_table(table_name: str, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
    normalized = table_name.strip()

    if not normalized:
        raise ValueError("Nome da tabela não informado.")

    list_of_tables = list_tables()
    table_names = {name.lower() for name in list_of_tables}
    bare_table_names = {name.lower().split(".")[-1] for name in list_of_tables}

    if normalized.lower() not in table_names and normalized.lower().split(".")[-1] not in bare_table_names:
        raise ValueError(f"Tabela '{table_name}' não encontrada.")

    if "." in normalized:
        schema_name, table_part = [part.strip() for part in normalized.split(".", 1)]
        safe_identifier = (
            '"' + schema_name.replace('"', '""') + '".'
            + '"' + table_part.replace('"', '""') + '"'
        )
    else:
        safe_identifier = '"' + normalized.replace('"', '""') + '"'

    query = text(f'SELECT * FROM {safe_identifier} LIMIT :limit OFFSET :offset')

    with engine.connect() as conn:
        rows = conn.execute(query, {"limit": limit, "offset": offset}).mappings().all()

    return [dict(row) for row in rows]
