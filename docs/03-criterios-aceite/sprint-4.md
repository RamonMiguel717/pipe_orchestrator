# Critérios de aceite — Sprint 4: observabilidade, alertas, extensibilidade e semântica de `branch`/`wait`

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | M |
| Blocos | B10, B13, B01, B09, B04 |

## Objetivo

O sistema conta o que acontece (métricas), avisa quando falha (alertas), aceita extensões (plugins) e executa `branch` e `wait` com semântica própria.

## Pré-condições (DoR da sprint)

- Sprints 2 e 3 aprovadas.
- Lista fechada de itens de usabilidade vindos das retrospectivas das Sprints 0–3 (S4-12).

## Critérios

### Observabilidade e alertas (B10)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S4-01 | B10 | Métricas por pipeline na API (`/pipelines/{id}/metrics`): taxa de sucesso, duração p50/p95 dos últimos N runs, runs na fila; página "Visão geral" na interface com essas métricas e os últimos runs com falha | `tests/integration/test_metrics.py`, `tests/e2e/test_overview.py` | Pendente |
| S4-02 | B10 | Entry point `pipeorc.alerts` com contrato `AlertChannel`; canais de fábrica **e-mail (SMTP)** e **webhook**; regra por pipeline "alertar em falha" (API, CLI, interface) | `tests/integration/test_alerts.py` (SMTP e HTTP falsos) | Pendente |
| S4-03 | B10 | Alerta contém pipeline, run, passo que falhou, trecho final do log e link para a interface; falha no envio do alerta é registrada e não afeta o run | `tests/integration/test_alert_content.py` | Pendente |

### Extensibilidade (B13)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S4-04 | B13 | Carregamento por entry points nos quatro grupos (`action_types`, `executors`, `connectors`, `alerts`); plugin com erro na importação é isolado, registrado em `/info` e no `doctor`, e o servidor sobe | `tests/integration/test_plugins_loading.py` | Pendente |
| S4-05 | B13 | Contratos (`ActionType`, `Executor`, `Connector`, `AlertChannel`) publicados como `Protocol` com documentação e **teste de conformidade** reutilizável por autores de plugin | `tests/unit/plugins/test_contracts.py` | Pendente |
| S4-06 | B13 | Plugin de exemplo (pacote separado em `examples/plugin-exemplo/`) adiciona um tipo de ação com prefixo (`exemplo.sql`): aparece na paleta do construtor e como tag importável; executa; documentado passo a passo | `tests/integration/test_example_plugin.py` + Demo | Pendente |
| S4-07 | B13 | Plugin declara versão mínima do núcleo; versão incompatível é recusada com mensagem | `tests/unit/plugins/test_compat.py` | Pendente |

### Semântica de `branch` e `wait` (B01, B04)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S4-08 | B01 | `branch`: o retorno do passo (nome ou lista de nomes de passos, ou booleano para dois ramos) define quais dependentes seguem; os demais ficam `SKIPPED` (e seus dependentes também); na interface os ramos pulados aparecem esmaecidos | `tests/integration/test_branch.py` + Demo | Pendente |
| S4-09 | B01 | `wait`: reexecução periódica (intervalo e timeout configuráveis pela tag) até o passo retornar verdadeiro; timeout → `FAILED`; cada verificação registrada sem criar tentativas infinitas no histórico | `tests/integration/test_wait.py` | Pendente |
| S4-10 | B04 | No construtor e no SDK, `branch` e `wait` perdem o aviso "semântica na Sprint 4" e ganham propriedades próprias | `tests/e2e/test_branch_wait_builder.py` | Pendente |

### Gatilhos (B09)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S4-11 | B09 | Webhook de entrada (`POST /api/v1/hooks/{pipeline}/{token}`) dispara run com parâmetros do corpo; gatilho "ao concluir outra pipeline" (sucesso ou qualquer término) configurável por API/CLI/interface | `tests/integration/test_triggers.py` | Pendente |

### Refino

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S4-12 | B08 | Itens de usabilidade das retrospectivas das Sprints 0–3 (lista fechada na DoR) tratados ou explicitamente adiados com justificativa | Inspeção da lista | Pendente |

## Fora do escopo

Marketplace de plugins, SSO, métricas exportadas para sistemas externos (Futuro).

## Roteiro de demonstração do gate (G4)

1. Visão geral com métricas após uma série de runs com sucessos e falhas.
2. Pipeline com falha disparando alerta por webhook (receptor local) e por e-mail (servidor SMTP local).
3. Instalar o plugin de exemplo; ver o tipo novo na paleta; usar como tag num arquivo; executar.
4. Pipeline com `branch` escolhendo um ramo e pulando o outro; pipeline com `wait` esperando um arquivo aparecer.
5. Disparar um run por webhook com `curl`.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
