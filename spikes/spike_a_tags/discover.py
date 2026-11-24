"""Spike A — descoberta de tags em um arquivo e emissão da IR.

Compara duas estratégias:
  1. IMPORTAÇÃO: executa o módulo e lê o registro (metadados completos e validados).
  2. AST: só lê o código-fonte, sem executar (seguro, mas limitado a valores literais).
"""
from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pipeorc_sdk import Pipeline, TagError  # noqa: E402


def discover_by_import(path: pathlib.Path) -> list[dict]:
    Pipeline.reset_registry()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)  # executa o código do usuário (apenas definições)
    return [p.to_ir(module_name=path.stem, module_path=path.name) for p in Pipeline.registered()]


def discover_by_ast(path: pathlib.Path) -> list[dict]:
    """Lista tarefas sem executar o módulo. Só enxerga o que for literal no código."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "task":
                entry: dict = {"callable": node.name, "pipeline_var": getattr(dec.func.value, "id", "?")}
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    entry["type"] = dec.args[0].value
                for kw in dec.keywords:
                    try:
                        entry[kw.arg] = ast.literal_eval(kw.value)
                    except Exception:
                        entry[kw.arg] = "<não literal>"
                found.append(entry)
    return found


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: discover.py <arquivo.py>")
        return 2
    path = pathlib.Path(sys.argv[1]).resolve()

    t0 = time.perf_counter()
    try:
        irs = discover_by_import(path)
    except TagError as e:
        print(f"ERRO DE TAG: {e}")
        return 1
    t_import = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    listing = discover_by_ast(path)
    t_ast = (time.perf_counter() - t0) * 1000

    out = pathlib.Path(__file__).parent / "ir_tags.json"
    out.write_text(json.dumps(irs, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"== IMPORTAÇÃO ({t_import:.1f} ms): {len(irs)} pipeline(s) ==")
    for ir in irs:
        p = ir["pipeline"]
        print(f"  pipeline {p['name']} schedule={p['schedule']} tarefas={len(ir['tasks'])}")
        for t in ir["tasks"]:
            deps = sorted(set(t["inputs"].values()) | set(t["after"]))
            print(f"    - {t['id']:<12} type={t['type']:<10} executor={t['executor']['kind']:<7} deps={deps}")
    print(f"  IR escrita em {out.name}")
    print(f"== AST ({t_ast:.1f} ms): {len(listing)} tarefa(s) (sem executar) ==")
    for e in listing:
        print(f"    - {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
