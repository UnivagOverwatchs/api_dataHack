from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import fetch_table, list_tables, test_connection

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para expor tabelas do banco para integração com Power BI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, Any]:
    return {
        "message": "API conectada ao banco",
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return test_connection()


@app.get("/tables")
def get_tables() -> dict[str, Any]:
    try:
        return {"tables": list_tables()}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao listar tabelas: {exc}") from exc


@app.get("/api/tables")
def api_get_tables() -> dict[str, Any]:
    return get_tables()


@app.get("/table/{table_name}")
def get_table_data(
    table_name: str,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    try:
        rows = fetch_table(table_name=table_name, limit=limit, offset=offset)
        return {
            "table": table_name,
            "limit": limit,
            "offset": offset,
            "count": len(rows),
            "rows": rows,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a tabela: {exc}") from exc


@app.get("/api/data")
def get_api_data(
    table_name: str = Query(default="", description="Nome da tabela a ser consultada, ex.: analytics.p5_curso"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    if not table_name:
        raise HTTPException(status_code=400, detail="Parâmetro table_name é obrigatório. Exemplo: analytics.p5_curso")

    return get_table_data(table_name=table_name, limit=limit, offset=offset)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
