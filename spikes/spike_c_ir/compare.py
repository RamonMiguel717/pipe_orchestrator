"""Spike C — a IR produzida por TAGS e por BLOCOS é a mesma?

1. Gera a IR pelo caminho das tags (spike A) e pelo caminho dos blocos (builder.py).
2. Valida as duas contra o JSON Schema.
3. Compara a parte semântica (grafo, tipos, executores, retries...). A referência de
   código ('code') e a origem ('source') DEVEM diferir: módulo vs inline, tags vs builder.
4. Faz ida e volta em YAML (formato de import/export) sem perda.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "spike_a_tags"))
sys.path.insert(0, str(HERE))

from discover import discover_by_import  # noqa: E402
from builder import build_same_pipeline_as_tags  # noqa: E402


def semantic_view(ir: dict) -> dict:
    """Remove o que legitimamente difere entre os dois caminhos."""
    v = copy.deepcopy(ir)
    v["pipeline"].pop("source", None)
    for t in v["tasks"]:
        t.pop("code", None)
    return v


def main() -> int:
    schema = json.loads((HERE / "ir_schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    ir_tags = discover_by_import(HERE.parent / "spike_a_tags" / "example_etl.py")[0]
    ir_blocks = build_same_pipeline_as_tags()

    ok = True
    for label, ir in (("tags", ir_tags), ("blocos", ir_blocks)):
        errors = sorted(validator.iter_errors(ir), key=lambda e: list(e.path))
        if errors:
            ok = False
            print(f"[schema] IR via {label}: {len(errors)} erro(s)")
            for e in errors:
                print(f"   - {'/'.join(map(str, e.path))}: {e.message}")
        else:
            print(f"[schema] IR via {label}: válida")

    a, b = semantic_view(ir_tags), semantic_view(ir_blocks)
    if a == b:
        print("[equivalência] grafo, tipos, dependências, executores e retries IDÊNTICOS entre tags e blocos")
    else:
        ok = False
        print("[equivalência] DIFERENÇAS encontradas:")
        print(json.dumps({"tags": a, "blocos": b}, indent=2, ensure_ascii=False))

    kinds = {t["code"]["kind"] for t in ir_tags["tasks"]}, {t["code"]["kind"] for t in ir_blocks["tasks"]}
    print(f"[code] tags -> {sorted(kinds[0])} | blocos -> {sorted(kinds[1])} (diferença esperada: o runner trata ambos)")

    # YAML como formato de import/export
    text = yaml.safe_dump(ir_tags, sort_keys=False, allow_unicode=True)
    back = yaml.safe_load(text)
    if back == ir_tags:
        print(f"[yaml] ida e volta sem perda ({len(text.splitlines())} linhas)")
    else:
        ok = False
        print("[yaml] PERDA na ida e volta")
    (HERE / "ir_tags.yaml").write_text(text, encoding="utf-8")
    (HERE / "ir_blocks.json").write_text(json.dumps(ir_blocks, indent=2, ensure_ascii=False), encoding="utf-8")

    # schema rejeita IR inválida?
    broken = copy.deepcopy(ir_tags)
    broken["tasks"][0]["type"] = "extrair"
    broken["tasks"][1]["executor"] = {"kind": "docker"}
    n = len(list(validator.iter_errors(broken)))
    print(f"[schema] IR propositalmente quebrada: {n} erro(s) detectado(s) (esperado >= 2)")
    ok = ok and n >= 2

    print("RESULTADO:", "OK" if ok else "FALHOU")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
