"""Spike A2 (v0.3) — como o código do usuário fica com tags simples e 'só dados ordenam'."""
from pipeorc_tags import pipeline, step, test, extract, load, notify


@extract(retries=2)
def extrair_vendas():
    print("buscando vendas...")
    return [{"id": 1, "valor": 100.0}, {"id": 2, "valor": 250.5}]


@extract
def extrair_clientes():
    return {1: "Ana", 2: "Bruno"}


@test
def validar(vendas):
    assert all(v["valor"] >= 0 for v in vendas), "valor negativo"


@step
def transformar(vendas, clientes):
    return {"total": sum(v["valor"] for v in vendas), "clientes": len(clientes)}


@load(docker="python:3.12-slim", timeout=300)
def carregar(resumo, tabela="vendas_resumo"):
    print(f"gravando {resumo} em {tabela}")


@notify
def notificar(canal="email"):
    print(f"aviso por {canal}: pipeline concluída")


@pipeline(schedule="0 6 * * *")
def etl_vendas():
    """Extrai vendas e clientes, valida, transforma e carrega o resumo."""
    vendas = extrair_vendas()            # sem ligação entre si: rodam em paralelo
    clientes = extrair_clientes()
    validar(vendas)                      # @test: tudo abaixo espera por ele
    resumo = transformar(vendas, clientes)
    gravado = carregar(resumo, tabela="vendas_resumo_diario")
    notificar(wait_for=gravado)          # sem dados de 'carregar', mas deve vir depois


if __name__ == "__main__":
    etl_vendas()   # modo de desenvolvimento: roda tudo em processo, sem servidor
