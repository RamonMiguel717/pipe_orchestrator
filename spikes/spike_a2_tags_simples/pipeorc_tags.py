"""Spike A2 (v0.3) — tags simples com inferência do grafo. CÓDIGO DESCARTÁVEL.

Regras (decisões T1–T4 do PO em 2026-11-22):
  1. Uma função vira passo com um decorator nu: @step, @test, @extract, @transform, @load, @notify.
  2. A pipeline é uma função com @pipeline que chama os passos como funções normais.
  3. No registro, a função da pipeline roda em MODO DE CONSTRUÇÃO: os passos não executam,
     devolvem uma referência; o grafo é inferido.
  4. SÓ DADOS ORDENAM (T4): se um passo recebe o resultado de outro, depende dele.
     Passos sem ligação de dados rodam em paralelo. A interface mostra isso.
  5. Única exceção: @test é PORTÃO — tudo que vem depois dele no corpo da pipeline espera por ele.
  6. Ordem sem dados, quando o usuário quiser: wait_for=<referência ou lista> na chamada do passo.
  7. Características só quando necessário (kwargs, T3): @step(retries=2, timeout=300, docker="img", name="x").
  8. Fora do registro (ex.: `python etl.py`), tudo roda direto em processo — modo de desenvolvimento.
"""
from __future__ import annotations

import contextvars
import functools
import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable

IR_VERSION = "0.1"
TAGS = ("step", "test", "extract", "transform", "load", "notify", "branch", "wait")
OPTIONS = {"name", "retries", "timeout", "docker", "executor", "params"}
RESERVED_CALL_KWARGS = {"wait_for"}

_builder: contextvars.ContextVar["GraphBuilder | None"] = contextvars.ContextVar("pipeorc_builder", default=None)


class TagError(Exception):
    """Erro de uso das tags, com mensagem para o usuário final."""


# ---------------------------------------------------------------- grafo
@dataclass
class Node:
    id: str
    type: str
    fn: Callable[..., Any]
    inputs: dict[str, str] = field(default_factory=dict)   # parâmetro -> passo a montante (DADOS)
    after: list[str] = field(default_factory=list)          # ordem sem dados (portão de @test ou wait_for)
    params: dict[str, Any] = field(default_factory=dict)    # literais passados na chamada
    options: dict[str, Any] = field(default_factory=dict)


class StepRef:
    """Referência ao resultado futuro de um passo. Opaca de propósito."""

    def __init__(self, node: Node):
        self.node = node

    def __repr__(self) -> str:
        return f"<resultado de {self.node.id}>"

    def _blocked(self, what: str):
        raise TagError(
            f"O resultado de '{self.node.id}' não pode ser usado com {what} no corpo da pipeline: "
            f"ele só existe quando a pipeline roda. Mova essa lógica para dentro de um passo, "
            f"ou use @branch (Fase 2) para decidir caminhos."
        )

    def __bool__(self): self._blocked("if/while/not")
    def __iter__(self): self._blocked("for/desempacotamento")
    def __len__(self): self._blocked("len()")
    def __getitem__(self, _): self._blocked("indexação [ ]")
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        self._blocked(f"acesso a atributo '.{name}'")
    def __eq__(self, _): self._blocked("comparação")
    def __add__(self, _): self._blocked("aritmética")
    __radd__ = __sub__ = __mul__ = __truediv__ = __add__
    __hash__ = object.__hash__


class GraphBuilder:
    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.counts: dict[str, int] = {}
        self.gates: list[str] = []            # @test já vistos, em ordem de código

    def _unique_id(self, base: str) -> str:
        n = self.counts.get(base, 0) + 1
        self.counts[base] = n
        return base if n == 1 else f"{base}_{n}"

    def ancestors(self, nid: str) -> set[str]:
        seen: set[str] = set()
        stack = [nid]
        while stack:
            cur = self.nodes[stack.pop()]
            for dep in set(cur.inputs.values()) | set(cur.after):
                if dep not in seen:
                    seen.add(dep)
                    stack.append(dep)
        return seen

    def add(self, tag: str, fn: Callable[..., Any], args: tuple, kwargs: dict, options: dict) -> StepRef:
        where = f"passo '{options.get('name') or fn.__name__}'"

        # wait_for= é reservado na chamada: ordem sem dados
        wait_for = kwargs.pop("wait_for", None)
        explicit_after: list[str] = []
        if wait_for is not None:
            refs = wait_for if isinstance(wait_for, (list, tuple)) else [wait_for]
            for r in refs:
                if not isinstance(r, StepRef):
                    raise TagError(f"{where}: wait_for= espera o resultado de outro passo, recebeu {type(r).__name__}")
                explicit_after.append(r.node.id)

        try:
            bound = inspect.signature(fn).bind_partial(*args, **kwargs)
        except TypeError as e:
            raise TagError(f"{where}: chamada não bate com a assinatura da função ({e})") from None

        inputs: dict[str, str] = {}
        params: dict[str, Any] = {}
        for pname, val in bound.arguments.items():
            if isinstance(val, StepRef):
                inputs[pname] = val.node.id
            else:
                try:
                    json.dumps(val)
                except TypeError:
                    raise TagError(
                        f"{where}: o argumento '{pname}' recebeu {type(val).__name__}, que não é serializável. "
                        f"Passe valores simples (texto, número, lista, dicionário) ou o resultado de outro passo."
                    ) from None
                params[pname] = val

        nid = self._unique_id(options.get("name") or fn.__name__)
        node = Node(nid, tag, fn, inputs, [], params, options)
        self.nodes[nid] = node

        # ORDEM sem dados = portões (@test anteriores) + wait_for, removendo o que já é ancestral pelos dados
        upstream = set(inputs.values())
        implied: set[str] = set(upstream)
        for u in upstream:
            implied |= self.ancestors(u)
        candidates = list(dict.fromkeys(self.gates + explicit_after))   # sem duplicatas, ordem estável
        node.after = [c for c in candidates if c not in implied]
        # redução transitiva entre os próprios 'after' (ex.: teste B já espera teste A)
        reduced = []
        for c in node.after:
            if not any(c in self.ancestors(o) for o in node.after if o != c):
                reduced.append(c)
        node.after = reduced

        if tag == "test":
            self.gates.append(nid)
        return StepRef(node)


# ---------------------------------------------------------------- tags
def _executor_from_options(options: dict, where: str) -> dict:
    if "executor" in options and "docker" in options:
        raise TagError(f"{where}: use 'docker=' OU 'executor=', não os dois")
    if "docker" in options:
        img = options["docker"]
        if not isinstance(img, str) or not img:
            raise TagError(f"{where}: docker= espera o nome de uma imagem, ex.: docker='python:3.12-slim'")
        return {"kind": "docker", "image": img, "env": {}}
    ex = options.get("executor")
    if ex is None or ex == "local":
        return {"kind": "local"}
    if isinstance(ex, dict) and ex.get("kind") in ("local", "docker"):
        if ex["kind"] == "docker" and not ex.get("image"):
            raise TagError(f"{where}: executor docker sem 'image'")
        return ex
    raise TagError(f"{where}: executor inválido {ex!r}")


def _make_tag(tag: str):
    def decorator(fn: Callable[..., Any] | None = None, /, **options):
        unknown = set(options) - OPTIONS
        if unknown:
            raise TagError(f"@{tag}: opção(ões) desconhecida(s) {sorted(unknown)}. Aceitas: {sorted(OPTIONS)}")

        def wrap(f: Callable[..., Any]):
            if RESERVED_CALL_KWARGS & set(inspect.signature(f).parameters):
                raise TagError(f"@{tag} {f.__name__}: o parâmetro 'wait_for' é reservado pelo sistema; renomeie-o")

            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                b = _builder.get()
                if b is None:                       # modo de desenvolvimento: executa de verdade
                    kwargs.pop("wait_for", None)
                    return f(*args, **kwargs)
                return b.add(tag, f, args, kwargs, options)

            wrapper.__pipeorc_tag__ = tag           # type: ignore[attr-defined]
            wrapper.__pipeorc_options__ = options   # type: ignore[attr-defined]
            wrapper.__pipeorc_fn__ = f              # type: ignore[attr-defined]
            return wrapper

        if fn is not None:                          # usado como @step (sem parênteses)
            return wrap(fn)
        return wrap                                 # usado como @step(...)

    decorator.__name__ = tag
    decorator.__doc__ = f"Marca uma função como passo do tipo '{tag}'."
    return decorator


step, test, extract, transform, load, notify, branch, wait = (_make_tag(t) for t in TAGS)

_pipelines: list[Callable[..., Any]] = []


def pipeline(fn: Callable[..., Any] | None = None, /, *, name: str | None = None, schedule: str | None = None, description: str = ""):
    def wrap(f: Callable[..., Any]):
        f.__pipeorc_pipeline__ = {                  # type: ignore[attr-defined]
            "name": name or f.__name__,
            "schedule": schedule,
            "description": description or (inspect.getdoc(f) or ""),
        }
        _pipelines.append(f)
        return f                                    # chamar direto = rodar tudo em processo (dev)

    return wrap(fn) if fn is not None else wrap


def registered_pipelines() -> list[Callable[..., Any]]:
    return list(_pipelines)


def reset() -> None:
    _pipelines.clear()


# ---------------------------------------------------------------- construção → IR
def build(pipeline_fn: Callable[..., Any], *, module_name: str = "", module_path: str = "") -> dict:
    meta = getattr(pipeline_fn, "__pipeorc_pipeline__", None)
    if meta is None:
        raise TagError(f"'{pipeline_fn.__name__}' não tem @pipeline")
    b = GraphBuilder(meta["name"])
    token = _builder.set(b)
    try:
        sig = inspect.signature(pipeline_fn)
        missing = [p.name for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
        if missing:
            raise TagError(f"pipeline '{meta['name']}': parâmetros {missing} precisam de valor padrão (viram parâmetros da pipeline)")
        pipeline_fn()
    finally:
        _builder.reset(token)
    if not b.nodes:
        raise TagError(f"pipeline '{meta['name']}' não chama nenhum passo com tag")

    tasks = []
    for nid in sorted(b.nodes):
        n = b.nodes[nid]
        where = f"pipeline '{meta['name']}', passo '{nid}'"
        tasks.append({
            "id": nid,
            "type": n.type,
            "inputs": dict(n.inputs),
            "after": list(n.after),
            "retries": int(n.options.get("retries", 0)),
            "timeout_s": n.options.get("timeout"),
            "executor": _executor_from_options(n.options, where),
            "params": {**n.params, **dict(n.options.get("params", {}))},
            "code": {"kind": "module", "language": "python", "module": module_name,
                     "callable": n.fn.__name__, "path": module_path},
        })
    return {
        "ir_version": IR_VERSION,
        "pipeline": {
            "name": meta["name"],
            "description": meta["description"],
            "version": None,
            "schedule": {"cron": meta["schedule"]} if meta["schedule"] else None,
            "source": {"kind": "tags", "module": module_name, "path": module_path},
        },
        "tasks": tasks,
    }
