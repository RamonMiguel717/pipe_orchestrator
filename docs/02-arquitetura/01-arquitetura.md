# Etapa 2 — Arquitetura do sistema

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 2 em 2026-11-22 |
| Versão | 1.0 |
| Data | 2026-11-22 |
| Base | Etapa 1 aprovada; ADR-0001 a ADR-0012 (`Aceito`); spikes A, A2, B.1, C |

Este documento consolida as decisões dos ADRs em uma visão única. Em caso de conflito, o ADR prevalece e este documento é corrigido.

## 1. Princípios de arquitetura

| # | Princípio | Origem |
|---|---|---|
| A1 | **A IR é a coluna vertebral.** Tags e blocos produzem IR; todo o resto só conhece IR. | D2, ADR-0005 |
| A2 | **A API é a única porta do servidor.** CLI e interface são clientes HTTP; não há atalho. | R5, ADR-0002 |
| A3 | **Código do usuário nunca roda no processo do servidor.** Sempre em subprocesso ou contêiner, pelo runner. | ADR-0003, ADR-0009 |
| A4 | **Um protocolo de execução para todos os executores.** Diretório de trabalho + JSON + stdout + código de saída. | ADR-0009 |
| A5 | **Local por padrão, nada sai da máquina.** SQLite, arquivos locais, `127.0.0.1`, sem telemetria. | Q1, ADR-0006, ADR-0012 |
| A6 | **Extensão por fronteira explícita.** Tipos de ação, executores, conectores e alertas por entry points. | ADR-0012 |
| A7 | **Tudo que decide é registrado.** ADRs, versões imutáveis de IR, eventos de estado. | P3, ADR-0005, ADR-0010 |

## 2. Visão de componentes e processos

```
┌───────────────────────────────── máquina do usuário ─────────────────────────────────┐
│                                                                                      │
│  Navegador ──── interface web (React) ────┐                                          │
│                                            │ HTTP/SSE  127.0.0.1:<porta>              │
│  Terminal ───── CLI `pipeorc` (Typer) ─────┤                                          │
│                                            │                                          │
│  Código do ─── SDK (Pipeline/@task) ───────┤   (register: subprocesso isolado)        │
│  usuário                                   ▼                                          │
│  ┌──────────────────────── processo SERVIDOR (FastAPI + asyncio) ───────────────────┐ │
│  │  API v1 (REST + SSE) ── OpenAPI ── auth por token ── arquivos estáticos da UI    │ │
│  │        │                                                                         │ │
│  │  Serviços de aplicação (projetos, pipelines/versões, runs, agendamentos, segredos)│ │
│  │        │                     ▲                                                   │ │
│  │  Engine (run manager + DAG) ─┤ bus de eventos ─► SSE / persistência              │ │
│  │        │                     │                                                   │ │
│  │  Agendador (croniter) ───────┘                                                   │ │
│  │        │ despacha tentativas                                                     │ │
│  │  Executores: Local ──────────────┐   Docker ─────────────────┐                   │ │
│  │                                   │                            │                   │ │
│  │  Storage: SQLAlchemy/SQLite ── arquivos (runs/, artifacts/, logs) ── cofre        │ │
│  └───────────────────────────────────┼────────────────────────────┼───────────────────┘ │
│                                      ▼                            ▼                     │
│                     subprocesso `python -m pipeorc.runner`   contêiner (imagem do    │
│                     (interpretador do projeto)                usuário + runner montado)│
└──────────────────────────────────────────────────────────────────────────────────────┘
```

| Componente | Bloco(s) | Processo | Tecnologia (ADR) |
|---|---|---|---|
| Interface web | B04, B08 | navegador | React + TS + Vite, React Flow, Monaco (0007) |
| CLI | B08 | próprio, efêmero | Typer (0011) |
| SDK | B03 | código do usuário / subprocesso de registro | Tags nuas + modo de construção, só dados ordenam; Python puro + Pydantic + httpx (0003 v0.3) |
| API | B07 | servidor | FastAPI, OpenAPI, SSE, token (0008) |
| Serviços de aplicação | B01, B09, B12 | servidor | Python |
| Engine + agendador | B01, B09 | servidor (asyncio) | próprio + croniter (0010) |
| Executores | B05, B06 | servidor despacha; execução fora | subprocess / docker SDK (0009) |
| Runner | B05 | subprocesso ou contêiner | Python stdlib, zero dependências (0009) |
| Storage | B11 | servidor | SQLAlchemy 2 + Alembic + SQLite; arquivos (0006) |
| Cofre de segredos | B12 | servidor | cryptography (Fernet), chave em arquivo do usuário (0006/0009) |
| Plugins | B13 | servidor | entry points (0012) |
| Empacotamento | B14 | — | pip/pipx → instalador (0011) |

## 3. Estrutura do repositório (monorepo)

```
pipeorc/                    # distribuição Python única "pipeorc" (nome técnico provisório, Q8)
  ir/                       # modelos Pydantic da IR, canonicalização, hash, schema, migradores de ir_version
  sdk/                      # Pipeline, task, validação, descoberta (subprocesso), cliente HTTP
  runner/                   # executa UMA tentativa a partir de task.json — SEM dependências de terceiros
  server/
    main.py                 # app FastAPI, ciclo de vida (migrações, engine, agendador), estáticos
    api/v1/                 # routers: projects, pipelines, runs, schedules, secrets, tokens, events, health
    services/               # casos de uso; única camada que fala com storage e engine
    engine/                 # run_manager, dag_scheduler, estados, retries, cancelamento
    scheduler/              # laço cron, políticas de disparo perdido
    executors/              # base (Protocol), local, docker, registry (entry points)
    events/                 # bus interno, adaptador SSE
    storage/                # modelos SQLAlchemy, repositórios, alembic/
    secrets/                # cofre Fernet, resolução de ${secret:}
    config.py               # precedência: flags > env PIPEORC_* > config.toml > padrões
    static/                 # build da interface (gerado; não versionado)
  cli/                      # Typer: comandos do ADR-0011
  plugins/                  # contratos (Protocols) e carregamento por entry points
web/                        # React + TypeScript + Vite (build -> pipeorc/server/static/)
tests/
  unit/  integration/  e2e/  equivalence/   # equivalence: tags ≡ blocos (spike C em definitivo)
docs/                       # esta documentação
spikes/                     # descartável
scripts/                    # check.ps1 / check.sh (lint + tipos + testes + build web)
pyproject.toml  CHANGELOG.md  README.md
```

Regras de dependência entre pacotes (verificadas por teste de import):

```
runner  ← (nada do produto)             sdk ← ir
server  ← ir, runner (só para montar), plugins, sdk (só o cliente, opcional)
cli     ← sdk (cliente HTTP), ir        web ← API (OpenAPI)
```

## 4. Modelo de domínio

```
Principal 1──n ApiToken
Project   1──n Pipeline 1──n PipelineVersion 1──n Run 1──n TaskRun (1 por tarefa) 1──n Attempt
Project   1──n Secret
Pipeline  1──n Schedule
```

| Entidade | Campos principais | Observações |
|---|---|---|
| **Principal** | id, nome, tipo (`user`/`service`) | Um padrão no MVP (ADR-0012) |
| **ApiToken** | id, principal_id, hash, criado_em, último_uso, revogado_em | Valor só exibido na criação |
| **Project** | id, nome | Um padrão (`default`) no MVP |
| **Pipeline** | id, project_id, nome (único no projeto), descrição, origem (`tags`/`builder`), criado/atualizado | Metadado estável entre versões |
| **PipelineVersion** | id, pipeline_id, número, ir_json (canônico), ir_hash, criado_em | Imutável; hash dedup (ADR-0005) |
| **Schedule** | id, pipeline_id, cron, fuso, habilitado, política_perdidos, próximo_disparo, último_disparo | ADR-0010 |
| **Run** | id, pipeline_version_id, estado, gatilho (`manual`/`schedule`/`api`), params_json, criado/iniciado/terminado, erro | |
| **TaskRun** | id, run_id, task_id (da IR), estado, tentativa_atual, máx_tentativas | Espelha a tarefa dentro do run |
| **Attempt** | id, task_run_id, número, estado, executor, iniciado/terminado, código_saída, erro, dir_trabalho, log_path, outputs_json | Uma linha por tentativa (retries) |
| **Secret** | id, project_id, nome (único), ciphertext, criado/atualizado | Nunca devolvido pela API |

### Máquinas de estado (ADR-0010)

```
Run:      PENDING ─► RUNNING ─► SUCCESS
                          └───► FAILED
                          └───► CANCELLED
Attempt:  PENDING ─► QUEUED ─► RUNNING ─► SUCCESS
                                   ├────► FAILED ──(retries restantes)──► RETRY_WAIT ─► QUEUED (nova Attempt)
                                   └────► CANCELLED
TaskRun:  estado = estado da última Attempt; SKIPPED quando uma dependência termina FAILED/SKIPPED/CANCELLED
```

## 5. Definição de pipeline (IR) — resumo

Detalhe e regras no ADR-0005; schema v0.1 validado no spike C ([ir_schema.json](../../spikes/spike_c_ir/ir_schema.json)).

- `pipeline`: nome, descrição, `schedule.cron` opcional, `source` (`tags` | `builder`).
- `tasks[]`: `id`, `type` (ADR-0004), `inputs` (parâmetro → tarefa), `after` (ordem), `retries`, `timeout_s`, `params`, `executor` (`local` | `docker{image, env}`), `code` (`module{path, callable}` | `inline{source, entrypoint}`).
- Arestas são derivadas: `deps(t) = valores(inputs) ∪ after`. Na interface, arestas de dados (`inputs`) são sólidas e arestas de ordem (`after`) tracejadas.
- Canônico em JSON, hash SHA-256, YAML só para import/export.

## 6. Fluxos principais

### 6.1 Registrar pipeline a partir de código (Fluxo A)

1. `pipeorc register etl.py` abre um **subprocesso** com o SDK, importa `etl.py`, localiza as funções `@pipeline`, executa cada uma em **modo de construção** (os passos `@step`/`@test`/… não rodam; devolvem referências e registram as chamadas), infere o grafo (só dados ordenam: dependências pelos argumentos; `@test` como portão do que vem depois; `wait_for=` para ordem sem dados), valida e gera IR (`source.kind = tags`, `code.kind = module`, `path` absoluto normalizado). Detalhe no ADR-0003 v0.3.
2. CLI envia `POST /api/v1/pipelines:register` com a IR.
3. Servidor valida contra os modelos Pydantic, canonicaliza, calcula hash; cria `Pipeline` se não existir; cria `PipelineVersion` se hash novo; devolve versão e um resumo (tarefas, diferenças em relação à anterior).

### 6.2 Salvar pipeline pelo construtor (Fluxo B) — Sprint 3

1. Interface monta blocos (tipo, código inline, ligações) e chama o **mesmo** endpoint de registro com `source.kind = builder`, `code.kind = inline`.
2. Servidor segue 6.1 passo 3. Não há caminho especial para blocos.

### 6.3 Disparar e executar um run

1. `POST /api/v1/runs {pipeline, version?, params}` (ou agendador, ou CLI) cria `Run PENDING` e `TaskRun PENDING` para cada tarefa; publica evento.
2. Run manager admite o run respeitando limites; `Run RUNNING`.
3. DAG scheduler marca `QUEUED` as tarefas sem dependências pendentes e as despacha ao executor da tarefa.
4. Para cada tentativa o Engine: cria o diretório da tentativa; grava `task.json` (tarefa + params resolvidos, com `${secret:}` **só nas variáveis de ambiente entregues ao executor**, nunca no arquivo) e `inputs.json` (saídas das dependências); chama `Executor.run`.
5. O executor inicia o runner (subprocesso ou contêiner), repassa cada linha de log ao bus (→ arquivo `log.txt` e SSE), espera o término, lê `outputs.json`, devolve `AttemptResult`.
6. Engine persiste estado; em falha com retries, agenda nova tentativa com backoff; em falha definitiva, marca dependentes `SKIPPED`; libera tarefas cujas dependências concluíram.
7. Quando não restam tarefas ativas, o run termina `SUCCESS` ou `FAILED`; eventos publicados; interface e `pipeorc run --watch` refletem via SSE.

### 6.4 Executor Local vs Docker (ADR-0009)

| Passo | Local | Docker |
|---|---|---|
| Ambiente | interpretador configurado do projeto | `executor.image` (pull se ausente, com progresso) |
| Código | `path` acessível no disco | projeto montado em `/work/project`; runner montado em `/opt/pipeorc` |
| Troca de dados | diretório da tentativa | mesmo diretório montado em `/work` |
| Logs | pipe stdout/stderr | `container.logs(stream=True)` |
| Timeout/cancel | mata árvore de processos | `container.kill` + remove |
| Diagnóstico | versão do Python | `doctor`: instalado / rodando / permissões (spike B.1) |

### 6.5 Agendamento

Laço a cada 15 s: agendamentos habilitados com `próximo_disparo <= agora` geram runs (gatilho `schedule`), aplicam política de perdidos e recalculam com `croniter`. Ao iniciar o servidor, agendamentos com disparos no passado são tratados pela política (`skip` padrão).

### 6.6 Cancelamento

`POST /api/v1/runs/{id}:cancel` → run manager marca `CANCELLED` as tentativas `QUEUED`, chama `Executor.cancel` nas `RUNNING`, não despacha mais nada; o run termina `CANCELLED`.

## 7. API v1 — superfície

| Recurso | Operações (MVP salvo indicação) |
|---|---|
| `/health`, `/info` | estado do servidor, versão, executores disponíveis (saída do `doctor`) |
| `/projects` | listar, obter (criar/editar: Fase 2) |
| `/pipelines` | listar, obter, `:register` (IR), excluir, `/{id}/versions`, `/{id}/versions/{n}` (IR), `/{id}/export?format=yaml` |
| `/runs` | criar, listar (filtros: pipeline, estado, período, cursor), obter, `:cancel`, `/{id}/tasks`, `/{id}/tasks/{task}/attempts/{n}/logs` (texto), `.../logs/stream` (SSE), `/{id}/events` (SSE) |
| `/events` | SSE global (filtros por pipeline/run) |
| `/schedules` | CRUD, habilitar/desabilitar (Sprint 2) |
| `/secrets` | criar/atualizar, listar nomes, excluir — nunca lê valor (Sprint 2) |
| `/tokens` | criar, listar, revogar (Sprint 2) |
| `/ir/schema` | JSON Schema da IR na versão corrente |
| `/openapi.json`, `/docs` | especificação e documentação interativa |

Autenticação: `Authorization: Bearer <token>` em tudo exceto `/health`. Erros no formato único do ADR-0008.

## 8. Segurança (MVP)

- Servidor escuta só em `127.0.0.1`; porta configurável; CORS restrito à origem da interface.
- Token gerado no `init`, salvo em `config.toml` com permissões restritas ao usuário; só o hash no banco.
- Segredos cifrados com Fernet; chave em `<dados>/secret.key` com permissão restrita; entregues às tarefas só por variável de ambiente; mascarados nos logs quando o valor for conhecido.
- Código do usuário nunca roda no servidor (A3). Executor Docker roda sem privilégios extras e com limites de recurso configuráveis.
- Dependências fixadas (lockfile) e verificadas por ferramenta de vulnerabilidades no `check`.

## 9. Configuração e diretórios

```
<dados>/                         Windows: %LOCALAPPDATA%\pipeorc   Linux: ~/.local/share/pipeorc   (PIPEORC_HOME sobrescreve)
  config.toml                    servidor (host, porta), executores, limites, retenção, token da CLI
  secret.key                     chave do cofre
  pipeorc.db (+ -wal, -shm)      SQLite
  runs/<run>/<tarefa>/attempt-<n>/{task.json, inputs.json, outputs.json, log.txt, artifacts/}
  server.pid, server.log         operação do servidor
```

Precedência de configuração: flags da CLI > variáveis `PIPEORC_*` > `config.toml` > padrões. O `doctor` avisa se `<dados>` estiver em pasta sincronizada (OneDrive, Dropbox).

## 10. Observabilidade (MVP → Fase 2)

- MVP: histórico de runs/tentativas com duração e estado; logs por tentativa (arquivo + stream); eventos de transição por SSE; log do próprio servidor em `server.log` com nível configurável.
- Sprint 4: métricas agregadas por pipeline (taxa de sucesso, duração p50/p95, fila) expostas na API e na interface; alertas em falha por entry point `pipeorc.alerts`.

## 11. Extensibilidade (B13) — contratos a estabilizar na Sprint 4

```python
class ActionType(Protocol):   name, label, icon, code_template, on_before_dispatch(attempt) -> None | optional
class Executor(Protocol):     kind, run(attempt, on_log), cancel(attempt_id), health()
class Connector(Protocol):    name, config_schema, open(config) -> client
class AlertChannel(Protocol): name, config_schema, send(event, config)
```

Carregamento por `importlib.metadata.entry_points(group="pipeorc.<grupo>")`; falha isolada por plugin; lista exibida em `/info` e no `doctor`.

## 12. O que fica explicitamente para a Fase 2 e como a arquitetura já prevê

| Item | Preparação já feita |
|---|---|
| Servidor remoto / equipe | A2 (só API), token por principal, `project_id` em tudo, imagem Docker do servidor (Sprint 5) |
| Postgres | SQLAlchemy + Alembic, sem recursos exclusivos do SQLite |
| Tags por comentário / outras linguagens | IR independe da origem; `code.language` já existe |
| Inferência de dependências no SDK | açúcar sobre `inputs`/`after`, sem mudar IR |
| Worker separado | Engine conversa com a API só por serviços e bus |
| Envelope desktop | interface é estática, servida por HTTP |
| `branch`/`wait` com semântica | tipos já aceitos na IR (ADR-0004) |

## 13. Riscos de arquitetura e mitigação

| Risco | Mitigação |
|---|---|
| K3 Docker no Windows não validado | Pré-condição A1; spike B.2 na máquina do PO antes da Sprint 1; caminho "Docker ausente" já pronto |
| K5 Empacotamento Windows | pipx testado na Sprint 0; instalador na Sprint 5; alternativa PyInstaller já prevista |
| Interpretador do projeto ≠ interpretador do servidor (dependências do usuário) | Executor Local com interpretador configurável por projeto; `doctor` valida |
| Saídas grandes entre tarefas via JSON | Artefatos em arquivo com referência; documentar limite |
| SQLite sob sincronizador de arquivos | Diretório de dados fora de pastas sincronizadas; aviso no `doctor` |
| Crescimento de logs | Retenção e `runs prune` |
