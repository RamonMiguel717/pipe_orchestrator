"""Spike A2 — descobre @pipeline em um arquivo, constrói o grafo e mostra o que o sistema 'enxerga'."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import pipeorc_tags as pt  # noqa: E402


def discover(path: pathlib.Path) -> list[dict]:
    pt.reset()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    return [pt.build(p, module_name=path.stem, module_path=path.name) for p in pt.registered_pipelines()]


def render(ir: dict) -> None:
    p = ir["pipeline"]
    print(f"pipeline {p['name']}  schedule={p['schedule']}  — {p['description']}")
    for t in ir["tasks"]:
        data = ", ".join(f"{k}←{v}" for k, v in t["inputs"].items()) or "-"
        order = ", ".join(t["after"]) or "-"
        extras = []
        if t["retries"]: extras.append(f"retries={t['retries']}")
        if t["timeout_s"]: extras.append(f"timeout={t['timeout_s']}s")
        if t["executor"]["kind"] == "docker": extras.append(f"docker={t['executor']['image']}")
        if t["params"]: extras.append(f"params={t['params']}")
        print(f"  @{t['type']:<9} {t['id']:<17} dados: {data:<35} ordem: {order:<22} {' '.join(extras)}")


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "example_etl.py").resolve()
    t0 = time.perf_counter()
    try:
        irs = discover(path)
    except pt.TagError as e:
        print(f"ERRO DE TAG: {e}")
        raise SystemExit(1)
    ms = (time.perf_counter() - t0) * 1000
    print(f"== {len(irs)} pipeline(s) em {ms:.1f} ms ==")
    for ir in irs:
        render(ir)
    out = HERE / "ir_tags_simples.json"
    out.write_text(json.dumps(irs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"IR escrita em {out.name}")

    # valida contra o schema do spike C
    import jsonschema
    schema = json.loads((HERE.parent / "spike_c_ir" / "ir_schema.json").read_text(encoding="utf-8"))
    for ir in irs:
        errs = list(jsonschema.Draft202012Validator(schema).iter_errors(ir))
        print(f"[schema] {ir['pipeline']['name']}: {'válida' if not errs else errs[0].message}")
