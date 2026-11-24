"""Spike B.1 — diagnóstico do ambiente Docker, como o app faria (B06/B14).

Responde: existe Docker nesta máquina? Está rodando? Dá para falar com ele via SDK?
Produz uma mensagem compreensível para o usuário final, em vez de um traceback.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess


def check() -> dict:
    info: dict = {"os": platform.system(), "cli_on_path": shutil.which("docker")}

    if platform.system() == "Windows":
        info["engine_pipe"] = os.path.exists(r"\\.\pipe\docker_engine")
        try:
            r = subprocess.run(["wsl", "--status"], capture_output=True, timeout=10)
            info["wsl"] = r.returncode == 0
        except Exception:
            info["wsl"] = False
        info["desktop_installed"] = any(
            os.path.exists(p) for p in (
                r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Docker\Docker Desktop.exe"),
            )
        )
    else:
        info["engine_socket"] = os.path.exists("/var/run/docker.sock")

    try:
        import docker  # type: ignore
        from docker.errors import DockerException  # type: ignore

        try:
            client = docker.from_env(timeout=5)
            client.ping()
            v = client.version()
            info["sdk"] = {"ok": True, "server_version": v.get("Version"), "os": v.get("Os"), "arch": v.get("Arch")}
        except DockerException as e:
            info["sdk"] = {"ok": False, "error": type(e).__name__, "detail": str(e)[:200]}
    except ImportError:
        info["sdk"] = {"ok": False, "error": "SDK 'docker' não instalado"}
    return info


def human_message(info: dict) -> tuple[str, str]:
    """(status, mensagem) — status em {ready, not_running, not_installed, unknown}."""
    if info.get("sdk", {}).get("ok"):
        return "ready", f"Docker disponível (servidor {info['sdk']['server_version']}, {info['sdk']['os']}/{info['sdk']['arch']})."
    if info["os"] == "Windows":
        if not info.get("cli_on_path") and not info.get("desktop_installed"):
            extra = " O WSL2 está presente, que é o pré-requisito do Docker Desktop." if info.get("wsl") else " O WSL2 não foi detectado; o Docker Desktop precisa dele."
            return "not_installed", "Docker não está instalado nesta máquina. O executor Docker ficará indisponível até instalar o Docker Desktop." + extra
        if not info.get("engine_pipe"):
            return "not_running", "Docker Desktop está instalado mas não está em execução. Abra o Docker Desktop e tente de novo."
    else:
        if not info.get("cli_on_path"):
            return "not_installed", "Docker não está instalado. Instale o Docker Engine para habilitar o executor Docker."
        if not info.get("engine_socket"):
            return "not_running", "O serviço do Docker não está em execução (socket ausente)."
    return "unknown", f"Não foi possível falar com o Docker: {info.get('sdk', {}).get('detail', 'motivo desconhecido')}"


if __name__ == "__main__":
    info = check()
    status, msg = human_message(info)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    print(f"\nSTATUS: {status}\nMENSAGEM AO USUÁRIO: {msg}")
