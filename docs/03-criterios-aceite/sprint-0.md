# Critérios de aceite — Sprint 0: esqueleto andante

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | G |
| Blocos | B01, B02, B03, B05 (Local), B07, B08, B11, B14 (pipx) |

## Objetivo

Uma fatia fina de ponta a ponta: código com tags → registrado por subprocesso → executado localmente na ordem do grafo → visível na interface com logs. Nenhuma funcionalidade além disso.

## Pré-condições (DoR da sprint)

- Gate 3 aprovado.
- Decisão A3 aplicada (pt-BR na interface e CLI).
- Fixture de referência: `exemplos/etl_vendas.py` (o exemplo do spike A2 v0.3, em definitivo).

## Critérios

### Repositório e qualidade

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-01 | — | Repositório git inicializado; estrutura do monorepo igual à seção 3 da arquitetura; `pyproject.toml` com `requires-python >= 3.12`; lockfile; `.gitignore` | Inspeção | Pendente |
| S0-02 | — | `scripts/check.ps1` e `scripts/check.sh` rodam ruff, mypy, pytest com cobertura, tsc, vitest e build da interface, e terminam com código 0 | Comando | Pendente |
| S0-03 | — | Teste de fronteira de pacotes: `runner` não importa nada do produto nem de terceiros; `cli` e `web` não importam `server`; falha do teste quebra o `check` | `tests/unit/test_boundaries.py` | Pendente |
| S0-04 | B14 | `pipx install .` em venv limpo instala `pipeorc`; `pipeorc --version` responde; tempo e tamanho registrados na nota de implementação (risco K5) | Comando | Pendente |
| S0-05 | — | `CHANGELOG.md` criado com a seção da Sprint 0 | Inspeção | Pendente |

### Definição de pipeline — IR (B02)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-06 | B02 | Modelos Pydantic da IR v0.1 conforme ADR-0005; `pipeorc ir schema` emite o JSON Schema gerado dos modelos; as IRs dos spikes A2 e C validam | `tests/unit/ir/test_schema.py` | Pendente |
| S0-07 | B02 | IR inválida é rejeitada com mensagem que cita o campo (tipo inexistente, Docker sem imagem, dependência inexistente, ciclo, id duplicado) | `tests/unit/ir/test_validation.py` | Pendente |
| S0-08 | B02 | Canonicalização determinística: mesma pipeline com chaves/tarefas em ordens diferentes produz o mesmo JSON canônico e o mesmo hash SHA-256 | `tests/unit/ir/test_canonical.py` | Pendente |
| S0-09 | B02 | `pipeorc export --format yaml` e `pipeorc import` fazem ida e volta sem perda | `tests/unit/ir/test_yaml.py` | Pendente |
| S0-10 | B02 | Equivalência tags ≡ blocos: a pipeline de referência construída pelas tags e por um construtor programático (simulando o Fluxo B) gera IR semanticamente idêntica, diferindo só em `code` e `source` | `tests/equivalence/test_tags_vs_builder.py` | Pendente |

### SDK de tags (B03)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-11 | B03 | `from pipeorc import pipeline, step, test, extract, transform, load, notify` funciona; cada tag aceita uso sem parênteses e com kwargs (`name`, `retries`, `timeout`, `docker`, `executor`, `params`); kwarg desconhecido gera erro listando os aceitos | `tests/unit/sdk/test_tags.py` | Pendente |
| S0-12 | B03 | Inferência conforme ADR-0003: só dados ordenam; `@test` é portão do que vem depois; `wait_for=` cria ordem sem dados; literais viram `params`; chamadas repetidas geram `nome_2`; redução transitiva de `after` | `tests/unit/sdk/test_inference.py` (os 11 casos de borda do spike A2) | Pendente |
| S0-13 | B03 | Os 8 casos negativos do spike A2 produzem `TagError` com mensagem citando pipeline/passo, problema e correção; mais: nome de pipeline inválido e parâmetro de `@pipeline` sem valor padrão | `tests/unit/sdk/test_errors.py` | Pendente |
| S0-14 | B03 | Modo de desenvolvimento: chamar a função `@pipeline` fora do registro executa os passos em processo e ignora `wait_for` | `tests/unit/sdk/test_dev_mode.py` | Pendente |
| S0-15 | B03 | Parâmetros da função `@pipeline` com valor padrão viram parâmetros da pipeline na IR e `pipeorc run --param chave=valor` os sobrescreve no run | `tests/integration/test_params.py` | Pendente |
| S0-16 | B03 | `pipeorc register <arquivo>` importa o módulo em **subprocesso**; o processo do servidor nunca importa o módulo do usuário (teste: módulo que grava o PID ao importar); módulo com erro ou tag errada → código de saída ≠ 0 e mensagem clara | `tests/integration/test_register.py` | Pendente |
| S0-17 | B03 | Avisos no registro: chamada no corpo da pipeline a função sem tag; passo solto (sem dados e sem `wait_for`) | `tests/unit/sdk/test_warnings.py` | Pendente |

### Servidor, API e persistência (B07, B11)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-18 | B11 | `pipeorc init` cria o diretório de dados (ADR-0006), `config.toml` com token e permissões restritas ao usuário; segunda execução não sobrescreve; aviso se o diretório estiver em pasta sincronizada | `tests/integration/test_init.py` | Pendente |
| S0-19 | B07 | `pipeorc server start` escuta só em `127.0.0.1` na porta configurada; aplica migrações Alembic na partida; `GET /api/v1/health` responde sem token; qualquer outra rota sem token → 401 no formato único de erro | `tests/integration/test_server.py` | Pendente |
| S0-20 | B07 | OpenAPI 3.1 em `/api/openapi.json` e documentação em `/api/docs`; toda rota implementada aparece nela | `tests/integration/test_openapi.py` | Pendente |
| S0-21 | B07 | `POST /api/v1/pipelines:register`: cria pipeline e versão 1; mesma IR → mesma versão (sem duplicar); IR diferente → versão 2; resposta traz resumo das tarefas | `tests/integration/test_pipelines.py` | Pendente |
| S0-22 | B07 | Rotas de leitura: listar pipelines, obter pipeline, listar versões, obter IR de uma versão, exportar YAML | `tests/integration/test_pipelines.py` | Pendente |
| S0-23 | B07 | Rotas de runs: criar (`POST /runs`), listar com filtros (pipeline, estado) e paginação por cursor, obter run, listar tarefas do run, obter log de uma tentativa como texto | `tests/integration/test_runs_api.py` | Pendente |
| S0-24 | B07 | SSE: `GET /api/v1/events` publica transições de run e tarefa com `id` incremental; `GET .../logs/stream` entrega linhas de log antes de o passo terminar | `tests/integration/test_sse.py` | Pendente |
| S0-25 | B07 | Erros da API seguem `{ "error": { "code", "message", "details" } }` com mensagem em pt-BR | `tests/integration/test_errors.py` | Pendente |
| S0-26 | B11 | Banco SQLite em modo WAL; entidades Principal, ApiToken, Project, Pipeline, PipelineVersion, Run, TaskRun, Attempt com migração inicial Alembic; um principal e um projeto padrão criados no `init` | `tests/unit/storage/test_models.py` | Pendente |

### Engine, runner e executor Local (B01, B05)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-27 | B05 | Protocolo do runner (ADR-0009): lê `task.json` e `inputs.json`, executa `code.kind = module` e `code.kind = inline`, grava `outputs.json`, escreve logs em stdout, sai com 0 em sucesso, 1 em exceção (traceback no log) e 2 em erro de protocolo | `tests/unit/runner/test_runner.py` | Pendente |
| S0-28 | B05 | Executor Local roda o runner em subprocesso com o interpretador configurado para o projeto; logs chegam em streaming (primeira linha disponível antes do fim do passo); timeout básico mata o processo | `tests/integration/test_local_executor.py` | Pendente |
| S0-29 | B01 | Um run da pipeline de referência respeita o grafo: passos sem dependência executam concorrentemente (janelas de tempo sobrepostas); dependentes só começam após `SUCCESS` dos anteriores; `after` de `@test` e `wait_for` respeitados | `tests/integration/test_engine_dag.py` | Pendente |
| S0-30 | B01 | Falha de um passo: run `FAILED`; dependentes (por dados ou ordem) `SKIPPED`; passos independentes terminam normalmente | `tests/integration/test_engine_failure.py` | Pendente |
| S0-31 | B01 | Código do usuário nunca roda no processo do servidor: passo que registra `os.getpid()` difere do PID do servidor; passo que chama `sys.exit()` ou consome memória não derruba o servidor | `tests/integration/test_isolation.py` | Pendente |
| S0-32 | B01 | Estados e timestamps persistidos: Run `PENDING → RUNNING → SUCCESS/FAILED`; Attempt `PENDING → QUEUED → RUNNING → SUCCESS/FAILED/SKIPPED`; `outputs_json` e `log_path` gravados por tentativa | `tests/integration/test_states.py` | Pendente |
| S0-33 | B01 | Diretório da tentativa criado conforme ADR-0009 (`task.json`, `inputs.json`, `outputs.json`, `log.txt`, `artifacts/`); `inputs.json` contém as saídas das tarefas a montante mapeadas por parâmetro | `tests/integration/test_workdir.py` | Pendente |

### CLI (B08)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-34 | B08 | Comandos disponíveis e documentados (`--help` em pt-BR): `init`, `server start/stop/status`, `doctor`, `register`, `pipelines`, `show`, `run [--watch] [--param]`, `runs`, `logs [--follow]`, `ui`, `ir schema`, `export`, `import`; `--json` em todos os comandos de consulta | `tests/integration/test_cli.py` | Pendente |
| S0-35 | B08 | `pipeorc doctor` reporta Python, diretório de dados (com aviso de pasta sincronizada), porta e Docker com status `ready / not_running / not_installed / unknown` e mensagem do spike B.1 | `tests/unit/cli/test_doctor.py` + Comando | Pendente |
| S0-36 | B08 | `pipeorc run <pipeline> --watch` acompanha por SSE, imprime transições e logs, e termina com código 0 em sucesso e 1 em falha | `tests/integration/test_cli_watch.py` | Pendente |
| S0-37 | B08 | A CLI fala com o servidor **apenas** pela API (teste de fronteira S0-03) e usa o token do `config.toml` | `tests/unit/test_boundaries.py` | Pendente |

### Interface (B08)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S0-38 | B08 | Interface servida pelo servidor em `/`; API em `/api/v1`; textos em catálogo pt-BR | Inspeção + `tests/e2e/test_smoke.py` | Pendente |
| S0-39 | B08 | Página de pipelines lista nome, descrição, versão atual e último run | `tests/e2e/test_pipelines.py` | Pendente |
| S0-40 | B08 | Detalhe da pipeline mostra o grafo (React Flow, somente leitura): nós coloridos por tipo de ação, arestas de dados sólidas, arestas de ordem (`@test`, `wait_for`) tracejadas, parâmetros visíveis no nó | `tests/e2e/test_graph.py` + Demo | Pendente |
| S0-41 | B08 | Lista de runs com estado, gatilho, início e duração; detalhe do run com estado por passo atualizado por SSE e visualizador de logs em tempo real por passo | `tests/e2e/test_runs.py` + Demo | Pendente |
| S0-42 | B08 | Botão "Executar" na pipeline cria um run e leva ao detalhe | `tests/e2e/test_runs.py` | Pendente |

## Fora do escopo desta sprint

Executor Docker, agendamento, retries com backoff, segredos, cancelamento, edição de blocos, métricas, instalador. Um critério que precisar de um desses itens está no arquivo da sprint correspondente.

## Roteiro de demonstração do gate (G0)

1. Em um terminal limpo: `pipeorc init` → `pipeorc server start`.
2. `pipeorc doctor` (mostrar o status do Docker e do diretório de dados).
3. `pipeorc register exemplos/etl_vendas.py` → `pipeorc show etl_vendas` (tarefas, tipos, dependências inferidas).
4. `pipeorc run etl_vendas --watch`: ver os dois extratores em paralelo, o teste, a transformação, a carga e a notificação.
5. Abrir `pipeorc ui`: grafo com cores e arestas, lista de runs, logs em tempo real de um novo run disparado pela interface.
6. Alterar o exemplo para o teste falhar; registrar de novo (nova versão); rodar; ver `FAILED` no teste e `SKIPPED` nos dependentes na interface.
7. Rodar `scripts/check` e mostrar cobertura.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
