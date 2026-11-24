"""Spike C — simulação do caminho dos BLOCOS (Fluxo B).

O construtor do app produziria exatamente estas chamadas a partir da interface:
um bloco por tarefa, com tipo de ação (a tag do bloco), código inline e ligações.
"""
from __future__ import annotations

from typing import Any


class PipelineBuilder:
    def __init__(self, name: str, *, description: str = "", schedule: str | None = None):
        self.name, self.description, self.schedule = name, description, schedule
        self.blocks: list[dict[str, Any]] = []

    def add_block(
        self,
        block_id: str,
        type: str,
        source: str,
        *,
        inputs: dict[str, str] | None = None,
        after: list[str] | None = None,
        retries: int = 0,
        timeout_s: int | None = None,
        executor: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> "PipelineBuilder":
        self.blocks.append({
            "id": block_id,
            "type": type,
            "inputs": dict(inputs or {}),
            "after": list(after or []),
            "retries": retries,
            "timeout_s": timeout_s,
            "executor": executor or {"kind": "local"},
            "params": dict(params or {}),
            "code": {"kind": "inline", "language": "python", "source": source, "entrypoint": block_id},
        })
        return self

    def to_ir(self) -> dict[str, Any]:
        return {
            "ir_version": "0.1",
            "pipeline": {
                "name": self.name,
                "description": self.description,
                "version": None,
                "schedule": {"cron": self.schedule} if self.schedule else None,
                "source": {"kind": "builder"},
            },
            "tasks": sorted(self.blocks, key=lambda b: b["id"]),
        }


def build_same_pipeline_as_tags() -> dict[str, Any]:
    """Monta, por blocos, a mesma pipeline 'etl_vendas' do spike A."""
    b = PipelineBuilder(
        "etl_vendas",
        description="Extrai vendas do dia, valida, transforma e carrega no banco.",
        schedule="0 6 * * *",
    )
    b.add_block("extrair", "extract", "def extrair():\n    return [{'id': 1, 'valor': 100.0}]\n", retries=2, timeout_s=300)
    b.add_block("validar", "test", "def validar(extrair):\n    return True\n", inputs={"extrair": "extrair"})
    b.add_block("transformar", "transform", "def transformar(vendas):\n    return {'total': 1}\n", inputs={"vendas": "extrair"})
    b.add_block(
        "carregar", "load", "def carregar(transformar):\n    print(transformar)\n",
        inputs={"transformar": "transformar"}, after=["validar"],
        executor={"kind": "docker", "image": "python:3.12-slim", "env": {"DB_URL": "${secret:DB_URL}"}},
    )
    b.add_block("notificar", "notify", "def notificar():\n    print('ok')\n", after=["carregar"], params={"canal": "email"})
    return b.to_ir()
