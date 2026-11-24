"""Spike A — casos negativos: as mensagens de erro são claras para o usuário?"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pipeorc_sdk import Pipeline, TagError  # noqa: E402


def expect_error(label: str, build) -> None:
    Pipeline.reset_registry()
    try:
        build()
    except TagError as e:
        print(f"[ok] {label}\n     -> {e}")
        return
    print(f"[FALHOU] {label}: nenhum erro levantado")
    raise SystemExit(1)


def caso_tipo_invalido():
    p = Pipeline("p")

    @p.task("extrair")  # tipo não existe na taxonomia
    def a(): ...


def caso_input_nao_e_parametro():
    p = Pipeline("p")

    @p.task("extract")
    def a(): ...

    @p.task("transform", inputs=["a"])
    def b(dados): ...  # parâmetro chama 'dados', não 'a'


def caso_dependencia_inexistente():
    p = Pipeline("p")

    @p.task("load", after=["nao_existe"])
    def a(): ...

    p.to_ir()


def caso_ciclo():
    p = Pipeline("p")

    @p.task("transform", after=["b"])
    def a(): ...

    @p.task("transform", after=["a"])
    def b(): ...

    p.to_ir()


def caso_docker_sem_imagem():
    p = Pipeline("p")

    @p.task("load", executor="docker")
    def a(): ...


def caso_nome_duplicado():
    p = Pipeline("p")

    @p.task("extract", name="x")
    def a(): ...

    @p.task("extract", name="x")
    def b(): ...


if __name__ == "__main__":
    expect_error("tipo de ação inválido", caso_tipo_invalido)
    expect_error("input que não é parâmetro da função", caso_input_nao_e_parametro)
    expect_error("dependência inexistente", caso_dependencia_inexistente)
    expect_error("ciclo de dependências", caso_ciclo)
    expect_error("executor docker sem imagem", caso_docker_sem_imagem)
    expect_error("nome de tarefa duplicado", caso_nome_duplicado)
    print("todos os casos negativos produziram erro claro")
