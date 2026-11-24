# ADR-0003 — Forma das tags e descoberta

| Status | Data | Decisores |
|---|---|---|
| `Aceito` (v1.0) — todos os pontos decididos pelo PO: Q2, Q4, feedback "tags simples", T1–T4 e C1–C2 | 2026-11-22 | PO (decisões); agente (detalhes validados pelo spike A2) |

## Contexto

A v0.1 propunha um objeto `Pipeline` explícito e `@etl.task("extract", inputs=..., after=...)`. O PO avaliou como pesado demais e pediu tags simples (`@step`, `@test`, `@executor`): **a tag é o próprio nome do decorator**, marca a progressão do fluxo e só recebe características quando necessário; o foco é ser **simples para o usuário e completo na visualização do sistema**. A v0.2 prototipou isso (spike A2) e levou quatro perguntas ao PO, respondidas em 2026-11-22:

| # | Pergunta | Decisão do PO |
|---|---|---|
| T1 | `@executor` = função que executa o fluxo? | Sim. Nome adotado: **`@pipeline`** |
| T2 | Tags em inglês ou português? | **Inglês** (os nomes em português eram só exemplos) |
| T3 | Características por kwargs ou tags empilhadas? | **kwargs** |
| T4 | Ordem padrão sequencial ou só dados ordenam? | **Só dados ordenam.** A interface vai mostrar a execução do fluxo, então o comportamento é acompanhado visualmente |

## Opções consideradas (histórico)

| Opção | Avaliação |
|---|---|
| v0.1 — explícita (`Pipeline` + `inputs=`/`after=`) | Rejeitada pelo PO: verbosa; o usuário declara o que o sistema pode inferir |
| v0.2 — sequencial por padrão + `with parallel()` | Rejeitada em T4: esconde o paralelismo; a visualização resolve a previsibilidade |
| **v0.3 — só dados ordenam** (escolhida) | Paralelismo máximo por padrão; grafo = fluxo de dados; `@test` como única exceção de ordem; `wait_for=` para o raro caso de ordem sem dados |
| Tags empilhadas para opções | Rejeitada em T3 |

## Decisão

### 1. Vocabulário (a tag é o nome do decorator, em inglês)

```python
from pipeorc import pipeline, step, test, extract, transform, load, notify
```

| Tag | Papel | Obrigatória? |
|---|---|---|
| `@pipeline` | A função que **descreve o fluxo** chamando os passos como funções normais. Nome da pipeline = nome da função; opções `name=`, `schedule=`, `description=` (padrão: docstring). | Uma por pipeline |
| `@step` | Passo genérico. É o padrão para tudo. | O "cavalo de batalha" |
| `@test` | Verificação. Se falhar (exceção/assert), **nada que vem depois dela no corpo roda**. | Opcional |
| `@extract` `@transform` `@load` `@notify` | O mesmo que `@step`, com tipo para a visualização (cor, ícone, modelo de código, relatórios). | Opcional |
| `@branch` `@wait` | Aceitas desde já; semântica no Engine na Sprint 4 (ADR-0004). | Opcional |
| `@container` | Passo que roda imagem + comando, sem código Python (Sprint 1). | Opcional |

### 2. Como fica o código do usuário

```python
@extract(retries=2)
def extrair_vendas(): ...

@extract
def extrair_clientes(): ...

@test
def validar(vendas): assert all(v["valor"] >= 0 for v in vendas)

@step
def transformar(vendas, clientes): ...

@load(docker="python:3.12-slim", timeout=300)
def carregar(resumo, tabela="vendas_resumo"): ...

@notify
def notificar(canal="email"): ...

@pipeline(schedule="0 6 * * *")
def etl_vendas():
    """Extrai vendas e clientes, valida, transforma e carrega o resumo."""
    vendas = extrair_vendas()           # sem ligação entre si: rodam em paralelo
    clientes = extrair_clientes()
    validar(vendas)                     # @test: tudo abaixo espera por ela
    resumo = transformar(vendas, clientes)
    gravado = carregar(resumo, tabela="vendas_resumo_diario")
    notificar(wait_for=gravado)         # ordem sem dados, dita explicitamente
```

`python etl.py` com `etl_vendas()` no `__main__` **roda tudo em processo, sem servidor** (modo de desenvolvimento).

### 3. Regras de inferência (o sistema deduz; o usuário não declara)

| # | Regra | Vira na IR |
|---|---|---|
| I1 | **Dados ordenam:** o resultado de um passo passado como argumento a outro cria a dependência. Passos sem ligação de dados **rodam em paralelo**. | `inputs: {parâmetro: passo}` |
| I2 | **`@test` é portão** (única exceção a I1): todo passo chamado **depois** de um `@test` no corpo da pipeline espera por ele; passos chamados antes não. Vários testes em sequência encadeiam. | `after: [teste]` (reduzido quando já implícito) |
| I3 | **`wait_for=`** na chamada do passo impõe ordem sem dados: `notificar(wait_for=gravado)` ou `wait_for=[a, b]`. É nome reservado; uma função com parâmetro `wait_for` recebe erro ao ser decorada. | `after: [...]` |
| I4 | Literais passados na chamada viram parâmetros do passo; parâmetros da função `@pipeline` (com valor padrão) viram parâmetros da pipeline. | `params` |
| I5 | O mesmo passo chamado duas vezes gera ids `nome`, `nome_2`, … | `id` |
| I6 | `after` redundante com o que os dados já implicam é removido (redução transitiva), para o grafo ficar limpo. | — |

Na interface, arestas de **dados** são sólidas e arestas de **ordem** (`@test`, `wait_for`) tracejadas. Como a execução é acompanhada visualmente (T4), o usuário vê o paralelismo e corrige com `wait_for=` onde quiser ordem.

### 4. Características só quando necessário (kwargs da tag, T3)

`name=`, `retries=`, `timeout=` (segundos), `docker="imagem"` (atalho), `executor={...}` (forma completa), `params={...}`. Opção desconhecida gera erro listando as aceitas.

### 5. Descoberta e registro

`pipeorc register <arquivo|pasta>`: importa o módulo em **subprocesso isolado**, localiza as funções `@pipeline`, executa cada uma em **modo de construção** (os passos não executam; devolvem referências e registram as chamadas), gera a IR, valida e envia à API. Um aviso (por AST) aponta chamadas, no corpo da pipeline, a funções **sem tag** — elas rodariam no registro, não na execução.

### 6. Limitações explícitas (com mensagem de erro clara)

- O resultado de um passo não pode ser usado em `if`, `for`, `len()`, índice, atributo, comparação ou aritmética no corpo da pipeline: ele só existe na execução. A mensagem orienta a mover a lógica para dentro de um passo ou usar `@branch`.
- Argumentos literais precisam ser serializáveis (texto, número, lista, dicionário).
- Um passo sem dados nem `wait_for` (ex.: `notificar()` solto) roda **no início**, em paralelo com tudo. A interface mostra isso; o aviso de registro destaca passos "soltos" para o usuário decidir.

### 7. O que **não** muda

A IR (ADR-0005) é a mesma: `type` recebe o nome da tag; `inputs`/`after`/`params`/`executor` são preenchidos pela inferência. O construtor de blocos (Fluxo B) continua produzindo a mesma IR — uma ligação de dados entre blocos equivale a I1, uma ligação de ordem equivale a `wait_for` — e, na Fase 2, poderá **exportar** uma pipeline de blocos neste formato de código.

## Consequências

- Positivas: o usuário escreve um script com decorators nus e ganha grafo, tipos e paralelismo máximo sem declarar nada; erros cedo e em linguagem de usuário; modo de desenvolvimento sem servidor; o grafo é literalmente o fluxo de dados, o que torna a visualização fiel.
- Negativas: passos de efeito colateral sem dados exigem `wait_for=`; lógica condicional no corpo só com `@branch` (Sprint 4).
- Riscos: usuário surpreso com um passo rodando "cedo demais" — mitigado pela visualização (T4) e pelo aviso de passos soltos no registro.

## Consequências de T4 — confirmadas pelo PO em 2026-11-22

| # | Ponto | Decisão |
|---|---|---|
| C1 | `@test` como portão de tudo que vem depois no corpo | **Confirmado.** Sem isso, `@test` não protege nada sob "só dados ordenam" |
| C2 | `wait_for=` reservado na chamada para ordem sem dados | **Confirmado.** Válvula de escape mínima para passos de efeito colateral |

## Relacionados

ADR-0004 (tipos = tags), ADR-0005 (IR inalterada), ADR-0009; spike A2 ([relatório](../relatorio-spikes.md)); bloco B03.
