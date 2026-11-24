# Critérios de aceite — Sprint 2: agendamento, confiabilidade e segredos

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | G |
| Blocos | B09, B01, B12, B10 |

## Objetivo

Pipelines disparam sozinhas por cron, sobrevivem a desligamentos da máquina com política clara, se recuperam de falhas transitórias, e usam segredos sem expô-los. Fecha o MVP.

## Pré-condições (DoR da sprint)

- Sprint 0 aprovada (a Sprint 1 pode estar em paralelo ou concluída; nada aqui depende de Docker).
- Relógio simulável nos testes (injeção de `clock` no agendador e no engine).

## Critérios

### Agendamento (B09)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S2-01 | B09 | CRUD de agendamentos via API (`/schedules`), CLI (`pipeorc schedules add/list/enable/disable/rm`) e interface; expressão cron validada com mensagem de erro em pt-BR; fuso configurável (padrão: fuso do servidor) | `tests/integration/test_schedules_api.py`, `tests/e2e/test_schedules.py` | Pendente |
| S2-02 | B09 | `schedule=` na tag `@pipeline` cria o agendamento no registro (desabilitado por padrão até o usuário habilitar, ou habilitado — decisão registrada na nota de implementação e refletida na interface) | `tests/integration/test_schedule_from_tag.py` | Pendente |
| S2-03 | B09 | Laço do agendador dispara o run no horário com tolerância de um tique (15 s), calcula `next_fire_at` com `croniter`, grava `last_fire_at`; gatilho do run = `schedule` | `tests/unit/scheduler/test_loop.py` (relógio simulado) | Pendente |
| S2-04 | B09 | Políticas de disparos perdidos após "desligamento": `skip` (padrão) ignora e recalcula; `run_once` cria um run; `run_all` cria um por disparo perdido até o teto configurado | `tests/unit/scheduler/test_missed.py` | Pendente |
| S2-05 | B09 | Sem sobreposição: com `max_parallel_runs = 1` (padrão) um disparo enquanto o anterior roda é pulado (evento registrado) ou enfileirado, conforme configuração da pipeline | `tests/integration/test_overlap.py` | Pendente |

### Confiabilidade do Engine (B01)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S2-06 | B01 | Retries: passo com `retries=N` falhando gera até N+1 tentativas (`Attempt` por tentativa), backoff exponencial com teto configurável, estado `RETRY_WAIT` entre elas; sucesso em tentativa posterior conclui normalmente | `tests/integration/test_retries.py` | Pendente |
| S2-07 | B01 | Timeout por passo (IR) e por run (configuração): processo/contêiner morto, `FAILED` com motivo `timeout`, dependentes `SKIPPED` | `tests/integration/test_timeouts.py` | Pendente |
| S2-08 | B01 | Cancelamento (`POST /runs/{id}:cancel`, `pipeorc runs cancel`, botão na interface): tentativas `QUEUED` → `CANCELLED`, `RUNNING` → `Executor.cancel`, run `CANCELLED`; nada mais é despachado | `tests/integration/test_cancel.py` + Demo | Pendente |
| S2-09 | B01 | Limites globais de concorrência (runs e tarefas simultâneas) respeitados sob carga (ex.: 20 runs com limite 3) | `tests/integration/test_concurrency_limits.py` | Pendente |
| S2-10 | B01 | Recuperação após queda: ao iniciar, runs/tentativas `RUNNING` órfãos viram `FAILED` com motivo `server_restart`; agendamentos recalculados | `tests/integration/test_recovery.py` | Pendente |

### Segredos e autenticação (B12)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S2-11 | B12 | `pipeorc secrets set/list/rm` e API (`/secrets`, só escrita e listagem de nomes); valor cifrado em repouso (Fernet; inspeção direta do banco não revela o valor); chave em `<dados>/secret.key` com permissão restrita | `tests/integration/test_secrets.py` + Inspeção | Pendente |
| S2-12 | B12 | `${secret:NOME}` em `executor.env` e `params` é resolvido só no despacho e entregue **apenas** por variável de ambiente ao executor (Local e Docker); nunca aparece em `task.json`, `inputs.json`, respostas da API ou IR | `tests/integration/test_secret_resolution.py` | Pendente |
| S2-13 | B12 | Mascaramento: valor de segredo conhecido impresso pelo passo aparece como `***` no log armazenado e no stream | `tests/integration/test_secret_masking.py` | Pendente |
| S2-14 | B12 | Segredo inexistente referenciado: run falha antes de iniciar com mensagem que nomeia o segredo | `tests/integration/test_secret_missing.py` | Pendente |
| S2-15 | B12 | Autenticação: token Bearer obrigatório em toda rota exceto `/health`; `pipeorc token create/list/revoke`; token revogado → 401; só o hash no banco; token exibido uma única vez na criação | `tests/integration/test_tokens.py` | Pendente |

### Histórico e retenção (B10)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S2-16 | B10 | Histórico de runs com filtros por pipeline, estado e período na API, CLI e interface; detalhe mostra duração por passo e número da tentativa | `tests/integration/test_history.py`, `tests/e2e/test_history.py` | Pendente |
| S2-17 | B10 | Retenção configurável (dias e/ou número de runs por pipeline); `pipeorc runs prune` remove linhas e diretórios de tentativas, com `--dry-run` | `tests/integration/test_prune.py` | Pendente |

## Fora do escopo

Webhook de entrada e encadeamento de pipelines (Sprint 4), métricas agregadas e alertas (Sprint 4), controle de acesso por papéis (Fase 2).

## Roteiro de demonstração do gate (G2)

1. Agendar `etl_vendas` a cada minuto pela interface; ver dois disparos automáticos.
2. Parar o servidor por 3 minutos; religar com política `run_once`; ver um run de recuperação; repetir com `skip`.
3. Passo com falha intermitente (falha nas 2 primeiras tentativas) concluindo por retry, com as tentativas visíveis na interface.
4. Cancelar um run em andamento pela interface.
5. `pipeorc secrets set DB_URL ...`; passo que usa `${secret:DB_URL}` e imprime o valor: `***` no log; inspecionar `task.json` sem o valor.
6. Revogar o token em uso e mostrar a CLI recebendo 401 com mensagem clara.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
