"""Spike B.2 — executar UMA tarefa em contêiner Docker, do jeito que o executor faria.

Protocolo do runner (proposta a validar no ADR-0009):
  - diretório de trabalho do run montado em /work
  - /work/task.py        código da tarefa
  - /work/inputs.json    saídas das tarefas a montante
  - /work/outputs.json   escrito pela tarefa
  - stdout/stderr        transmitidos em tempo real como logs
  - código de saída      0 = sucesso

Requer Docker em execução. Se não houver, imprime o diagnóstico e sai com código 3.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from diagnose import check, human_message  # noqa: E402

IMAGE = "python:3.12-slim"

TASK_CODE = r'''
import json, os, sys, time
inputs = json.load(open("/work/inputs.json"))
print(f"[task] iniciando com inputs={inputs} DB_URL={os.environ.get('DB_URL')}", flush=True)
total = 0
for i, v in enumerate(inputs["vendas"], 1):
    total += v["valor"]
    print(f"[task] linha {i}: acumulado={total}", flush=True)
    time.sleep(0.3)
json.dump({"total": total, "qtd": len(inputs["vendas"])}, open("/work/outputs.json", "w"))
print("[task] concluída", flush=True)
sys.exit(0)
'''


def main() -> int:
    info = check()
    status, msg = human_message(info)
    if status != "ready":
        print(f"BLOQUEADO: {msg}")
        return 3

    import docker  # type: ignore

    client = docker.from_env()
    workdir = pathlib.Path(tempfile.mkdtemp(prefix="pipeorc_spike_"))
    (workdir / "task.py").write_text(TASK_CODE, encoding="utf-8")
    (workdir / "inputs.json").write_text(json.dumps({"vendas": [{"valor": 100.0}, {"valor": 250.5}, {"valor": 9.5}]}), encoding="utf-8")

    t0 = time.perf_counter()
    try:
        client.images.get(IMAGE)
        print(f"[executor] imagem {IMAGE} já presente")
    except docker.errors.ImageNotFound:
        print(f"[executor] baixando {IMAGE}...")
        client.images.pull(IMAGE)
    t_image = time.perf_counter() - t0

    t0 = time.perf_counter()
    container = client.containers.run(
        IMAGE,
        command=["python", "-u", "/work/task.py"],
        volumes={str(workdir): {"bind": "/work", "mode": "rw"}},
        environment={"DB_URL": "postgres://exemplo"},
        working_dir="/work",
        detach=True,
        mem_limit="256m",
        labels={"pipeorc.spike": "b"},
    )
    print(f"[executor] contêiner {container.short_id} iniciado")
    first_log = None
    for raw in container.logs(stream=True, follow=True, timestamps=True):
        if first_log is None:
            first_log = time.perf_counter() - t0
        print("  ", raw.decode(errors="replace").rstrip())
    result = container.wait()
    t_total = time.perf_counter() - t0
    container.remove()

    outputs = json.loads((workdir / "outputs.json").read_text(encoding="utf-8"))
    print(f"[executor] exit={result['StatusCode']} outputs={outputs}")
    print(f"[medições] imagem={t_image:.2f}s | 1º log após {first_log:.2f}s | total={t_total:.2f}s")
    return 0 if result["StatusCode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
