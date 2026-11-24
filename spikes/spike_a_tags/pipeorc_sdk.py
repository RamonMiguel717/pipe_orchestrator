"""Spike A — SDK mínimo de tags por decorators. CÓDIGO DESCARTÁVEL.

Objetivo: provar que decorators Python descrevem tarefa, tipo de ação,
dependências (dados e ordem), retries e executor, e que isso vira a IR.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable

IR_VERSION = "0.1"

# Taxonomia única (Q5) — mesma para tags e blocos
ACTION_TYPES = {
    "step", "test", "extract", "transform", "load",
    "notify", "branch", "wait", "container",
}


class TagError(Exception):
    """Erro de uso das tags, com mensagem pensada para o usuário final."""


@dataclass
class ExecutorSpec:
    kind: str = "local"
    image: str | None = None
    env: dict[str, str] = field(default_factory=dict)

    @classmethod
    def parse(cls, raw: Any, *, where: str) -> "ExecutorSpec":
        if raw is None or raw == "local":
            return cls(kind="local")
        if raw == "docker":
            raise TagError(f"{where}: executor 'docker' exige imagem; use executor={{'kind': 'docker', 'image': '...'}}")
        if isinstance(raw, dict):
            kind = raw.get("kind")
            if kind == "local":
                return cls(kind="local")
            if kind == "docker":
                if not raw.get("image"):
                    raise TagError(f"{where}: executor docker sem 'image'")
                return cls(kind="docker", image=raw["image"], env=dict(raw.get("env", {})))
            raise TagError(f"{where}: executor desconhecido '{kind}' (use 'local' ou 'docker')")
        raise TagError(f"{where}: executor inválido {raw!r}")

    def to_ir(self) -> dict[str, Any]:
        if self.kind == "docker":
            return {"kind": "docker", "image": self.image, "env": dict(self.env)}
        return {"kind": "local"}


@dataclass
class TaskSpec:
    id: str
    type: str
    fn: Callable[..., Any]
    inputs: dict[str, str]          # parâmetro -> id da tarefa a montante
    after: list[str]                # dependências só de ordem
    retries: int
    timeout_s: int | None
    executor: ExecutorSpec
    params: dict[str, Any]

    def to_ir(self, module_name: str, module_path: str) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "inputs": dict(self.inputs),
            "after": list(self.after),
            "retries": self.retries,
            "timeout_s": self.timeout_s,
            "executor": self.executor.to_ir(),
            "params": dict(self.params),
            "code": {
                "kind": "module",
                "language": "python",
                "module": module_name,
                "callable": self.fn.__name__,
                "path": module_path,
            },
        }


class Pipeline:
    """Agrupador explícito de tarefas. Um módulo pode declarar várias."""

    _registry: list["Pipeline"] = []

    def __init__(self, name: str, *, description: str = "", schedule: str | None = None, version: str | None = None):
        if not name or not name.replace("_", "").replace("-", "").isalnum():
            raise TagError(f"Nome de pipeline inválido: {name!r} (use letras, números, '_' ou '-')")
        self.name = name
        self.description = description
        self.schedule = schedule
        self.version = version
        self.tasks: dict[str, TaskSpec] = {}
        Pipeline._registry.append(self)

    # ---- a tag -------------------------------------------------------
    def task(
        self,
        type: str,
        *,
        name: str | None = None,
        inputs: list[str] | dict[str, str] | None = None,
        after: list[str] | None = None,
        retries: int = 0,
        timeout_s: int | None = None,
        executor: Any = "local",
        params: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            tid = name or fn.__name__
            where = f"pipeline '{self.name}', tarefa '{tid}'"
            if type not in ACTION_TYPES:
                raise TagError(f"{where}: tipo de ação '{type}' não existe. Válidos: {sorted(ACTION_TYPES)}")
            if tid in self.tasks:
                raise TagError(f"{where}: nome de tarefa duplicado")

            # inputs: lista -> parâmetro com o mesmo nome da tarefa a montante
            if inputs is None:
                norm_inputs: dict[str, str] = {}
            elif isinstance(inputs, dict):
                norm_inputs = dict(inputs)
            else:
                norm_inputs = {t: t for t in inputs}

            sig_params = set(inspect.signature(fn).parameters)
            missing = [p for p in norm_inputs if p not in sig_params]
            if missing:
                raise TagError(
                    f"{where}: inputs {missing} não são parâmetros da função "
                    f"(parâmetros encontrados: {sorted(sig_params)})"
                )

            spec = TaskSpec(
                id=tid, type=type, fn=fn, inputs=norm_inputs, after=list(after or []),
                retries=int(retries), timeout_s=timeout_s,
                executor=ExecutorSpec.parse(executor, where=where), params=dict(params or {}),
            )
            self.tasks[tid] = spec
            fn.__pipeorc_task__ = spec  # type: ignore[attr-defined]
            return fn

        return deco

    # ---- validação do grafo -----------------------------------------
    def dependencies(self, tid: str) -> set[str]:
        t = self.tasks[tid]
        return set(t.inputs.values()) | set(t.after)

    def validate(self) -> None:
        for tid in self.tasks:
            for dep in self.dependencies(tid):
                if dep not in self.tasks:
                    raise TagError(f"pipeline '{self.name}': tarefa '{tid}' depende de '{dep}', que não existe")
                if dep == tid:
                    raise TagError(f"pipeline '{self.name}': tarefa '{tid}' depende dela mesma")
        self.topological_order()

    def topological_order(self) -> list[str]:
        indeg = {tid: len(self.dependencies(tid)) for tid in self.tasks}
        ready = sorted(t for t, d in indeg.items() if d == 0)
        order: list[str] = []
        while ready:
            cur = ready.pop(0)
            order.append(cur)
            for tid in sorted(self.tasks):
                if cur in self.dependencies(tid):
                    indeg[tid] -= 1
                    if indeg[tid] == 0:
                        ready.append(tid)
        if len(order) != len(self.tasks):
            stuck = sorted(t for t, d in indeg.items() if d > 0)
            raise TagError(f"pipeline '{self.name}': ciclo de dependências envolvendo {stuck}")
        return order

    # ---- IR ----------------------------------------------------------
    def to_ir(self, *, module_name: str = "", module_path: str = "") -> dict[str, Any]:
        self.validate()
        return {
            "ir_version": IR_VERSION,
            "pipeline": {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "schedule": {"cron": self.schedule} if self.schedule else None,
                "source": {"kind": "tags", "module": module_name, "path": module_path},
            },
            "tasks": [self.tasks[t].to_ir(module_name, module_path) for t in sorted(self.tasks)],
        }

    @classmethod
    def registered(cls) -> list["Pipeline"]:
        return list(cls._registry)

    @classmethod
    def reset_registry(cls) -> None:
        cls._registry.clear()
