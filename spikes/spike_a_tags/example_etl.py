"""Spike A — código de usuário anotado com tags (como ficaria para quem usa o produto)."""
from pipeorc_sdk import Pipeline

etl = Pipeline(
    "etl_vendas",
    description="Extrai vendas do dia, valida, transforma e carrega no banco.",
    schedule="0 6 * * *",
)


@etl.task("extract", retries=2, timeout_s=300)
def extrair() -> list[dict]:
    print("buscando vendas...")
    return [{"id": 1, "valor": 100.0}, {"id": 2, "valor": 250.5}]


@etl.task("test", inputs=["extrair"])
def validar(extrair: list[dict]) -> bool:
    assert all(v["valor"] >= 0 for v in extrair), "valor negativo"
    return True


@etl.task("transform", inputs={"vendas": "extrair"})
def transformar(vendas: list[dict]) -> dict:
    return {"total": sum(v["valor"] for v in vendas), "qtd": len(vendas)}


@etl.task(
    "load",
    inputs=["transformar"],
    after=["validar"],
    executor={"kind": "docker", "image": "python:3.12-slim", "env": {"DB_URL": "${secret:DB_URL}"}},
)
def carregar(transformar: dict) -> None:
    print(f"gravando resumo {transformar}")


@etl.task("notify", after=["carregar"], params={"canal": "email"})
def notificar() -> None:
    print("pipeline concluída")
