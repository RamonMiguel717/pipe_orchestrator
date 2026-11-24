"""Spike A2 (v0.3) — casos de borda e negativos da inferência com 'só dados ordenam'."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pipeorc_tags as pt  # noqa: E402
from pipeorc_tags import TagError, pipeline, step, test  # noqa: E402


def expect_error(label, fn):
    pt.reset()
    try:
        fn()
    except TagError as e:
        print(f"[ok] {label}\n     -> {e}")
        return
    print(f"[FALHOU] {label}: nenhum erro")
    raise SystemExit(1)


def expect(label, cond):
    print(f"[{'ok' if cond else 'FALHOU'}] {label}")
    if not cond:
        raise SystemExit(1)


# --- casos negativos -------------------------------------------------------
def caso_if_sobre_resultado():
    @step
    def a(): return True
    @step
    def b(): ...
    @pipeline
    def p():
        if a():
            b()
    pt.build(p)


def caso_len_sobre_resultado():
    @step
    def a(): return [1]
    @step
    def b(n): ...
    @pipeline
    def p():
        b(len(a()))
    pt.build(p)


def caso_opcao_desconhecida():
    @step(retry=2)
    def a(): ...


def caso_argumento_nao_serializavel():
    @step
    def a(x): ...
    @pipeline
    def p():
        a(object())
    pt.build(p)


def caso_pipeline_vazia():
    @pipeline
    def p():
        pass
    pt.build(p)


def caso_chamada_errada():
    @step
    def a(x): ...
    @pipeline
    def p():
        a(1, 2)
    pt.build(p)


def caso_wait_for_invalido():
    @step
    def a(): ...
    @pipeline
    def p():
        a(wait_for="outro")
    pt.build(p)


def caso_parametro_reservado():
    @step
    def a(wait_for): ...


expect_error("if sobre resultado de passo", caso_if_sobre_resultado)
expect_error("len() sobre resultado de passo", caso_len_sobre_resultado)
expect_error("opção desconhecida na tag", caso_opcao_desconhecida)
expect_error("argumento não serializável", caso_argumento_nao_serializavel)
expect_error("pipeline sem passos", caso_pipeline_vazia)
expect_error("chamada com argumentos errados", caso_chamada_errada)
expect_error("wait_for com algo que não é passo", caso_wait_for_invalido)
expect_error("função com parâmetro reservado wait_for", caso_parametro_reservado)

# --- só dados ordenam -----------------------------------------------------------
pt.reset()
chamadas = []

@step
def gerar(n=1):
    chamadas.append(n)
    return n

@step
def somar(a, b):
    return a + b

@step
def avisar():
    return "ok"

@pipeline(name="dados")
def dados():
    x = gerar(1)
    y = gerar(2)           # sem dados entre x e y -> paralelos
    s = somar(x, y)
    avisar()               # sem dados -> independente (rodaria no início)
    return s

ir = pt.build(dados)
byid = {t["id"]: t for t in ir["tasks"]}
expect("passo chamado duas vezes ganha ids distintos", sorted(byid) == ["avisar", "gerar", "gerar_2", "somar"])
expect("literal vira param", byid["gerar"]["params"] == {"n": 1} and byid["gerar_2"]["params"] == {"n": 2})
expect("sem dados entre si -> sem ordem (paralelos)", byid["gerar_2"]["after"] == [] and byid["gerar"]["after"] == [])
expect("dados criam dependência", byid["somar"]["inputs"] == {"a": "gerar", "b": "gerar_2"} and byid["somar"]["after"] == [])
expect("passo sem dados é independente", byid["avisar"]["inputs"] == {} and byid["avisar"]["after"] == [])
expect("modo de desenvolvimento executa de verdade", dados() == 3 and chamadas == [1, 2])

# --- @test como portão + wait_for --------------------------------------------------
pt.reset()

@step
def a(): return 1
@step
def b(): return 2
@test
def checar(x): return x > 0
@test
def checar2(y): return y > 0
@step
def usar(x, y): return x + y
@step
def fim(): ...

@pipeline
def portao():
    x = a()
    y = b()
    checar(x)              # portão 1
    checar2(y)             # portão 2 (espera o portão 1)
    r = usar(x, y)         # espera os portões (só o 2, que já implica o 1)
    fim(wait_for=r)        # ordem explícita sem dados

ir = pt.build(portao)
byid = {t["id"]: t for t in ir["tasks"]}
expect("passos antes do teste não esperam por ele", byid["a"]["after"] == [] and byid["b"]["after"] == [])
expect("teste depende do seu dado", byid["checar"]["inputs"] == {"x": "a"} and byid["checar"]["after"] == [])
expect("segundo teste espera o primeiro (portão)", byid["checar2"]["after"] == ["checar"])
expect("passo após os testes espera só o último portão (redução transitiva)", byid["usar"]["after"] == ["checar2"])
expect("wait_for cria ordem sem dados", byid["fim"]["after"] == ["usar"] and byid["fim"]["inputs"] == {})
print("todos os casos passaram")
