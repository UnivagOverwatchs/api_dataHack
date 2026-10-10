import json
import os
from urllib import error, request

API_URL = os.getenv("API_URL", "localhost:8000")
DEFAULT_TABLE = os.getenv("TABLE_NAME", "analytics.p5_curso")


def get_json(url: str):
    try:
        with request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} em {url}: {body}") from exc
    except Exception as exc:  # pragma: no cover - utility script
        raise RuntimeError(f"Erro ao acessar {url}: {exc}") from exc


def main() -> None:
    table_name = os.getenv("TABLE_NAME", DEFAULT_TABLE)
    print(f"Tabela usada para teste: {table_name}")

    payload = get_json(f"{API_URL}/api/data?table_name={table_name}&limit=5")
    rows = payload.get("rows") or []

    print(f"Quantidade retornada: {len(rows)}")
    print(json.dumps(rows[:3], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
