# Etapa 2 — Plano de sprints

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 2 em 2026-11-22 |
| Versão | 1.0 |
| Data | 2026-11-22 |

Cada sprint segue o ciclo Desenvolvimento → Testes → Refinamento e termina em gate próprio (P1), com critérios de aceite definidos na Etapa 3. **Tamanho** é relativo (P/M/G), não compromisso de calendário. A ordem respeita Q6 (tags primeiro) e as dependências entre blocos.

## Visão geral

```
MVP ───────────────────────────────┐   Fase 2 (ainda v1) ─────────────────────────────────┐
Sprint 0        Sprint 1   Sprint 2│   Sprint 3        Sprint 4            Sprint 5        │
Esqueleto       Docker     Agenda, │   Construtor      Observabilidade,    Distribuição,   │──► Etapa 7
andante                    segredos│   de blocos       alertas, plugins    remoto          │    Entrega final
```

| Sprint | Objetivo | Blocos | Tamanho | Pré-condições |
|---|---|---|---|---|
| 0 | Esqueleto andante: código com tags → registrado → executado localmente → visível na interface | B01 B02 B03 B05(local) B07 B08 B11 B14(pipx) | G | Gate 3; decisões A2/A3 |
| 1 | Executor Docker completo | B05 B06 B14(doctor) | M | **Docker Desktop instalado** (A1); spike B.2 executado |
| 2 | Agendamento, confiabilidade e segredos | B09 B10 B12 B01 | G | Sprint 0 |
| 3 | Construtor de blocos v1 | B04 B08 B02 | G | Sprint 0 (IR e API estáveis) |
| 4 | Observabilidade, alertas, extensibilidade, `branch`/`wait` | B10 B13 B01 B09 | M | Sprints 2 e 3 |
| 5 | Distribuição, operação e preparação para servidor remoto | B14 B08 B11 B12 | G | Sprint 4 |

## Sprint 0 — Esqueleto andante (P4)

**Resultado demonstrável:** `pipeorc register exemplos/etl.py` seguido de `pipeorc run etl_vendas --watch` executa as tarefas localmente na ordem do grafo, com logs; a interface mostra a pipeline como blocos coloridos por tipo, a lista de runs e os logs de cada tarefa.

| Área | Escopo |
|---|---|
| Repositório | `git init`, estrutura do monorepo (arquitetura §3), `pyproject.toml`, ruff + mypy + pytest, Vite, `CHANGELOG.md`, `scripts/check`, README de desenvolvimento |
| IR (B02) | Modelos Pydantic v0.1, canonicalização, hash, geração do JSON Schema, validações do spike C em testes; YAML import/export básico |
| SDK (B03) | Tags nuas (`@pipeline`, `@step`, `@test`, `@extract`, `@transform`, `@load`, `@notify`) com modo de construção; só dados ordenam, `@test` como portão, `wait_for=`; parâmetros de pipeline; mensagens dos spikes A/A2; aviso de código solto e de passos soltos no corpo; descoberta em subprocesso; cliente HTTP |
| Servidor/API (B07, B11) | FastAPI, config, SQLite + Alembic (migração inicial), token no `init`, endpoints: health/info, pipelines (register/list/get/versions/export), runs (create/list/get/tasks/logs), SSE de eventos e de logs |
| Engine (B01) | Run manager, DAG scheduler, estados, falha → `SKIPPED` dependentes, concorrência simples; **sem** retries/timeouts avançados (Sprint 2) |
| Executor Local + runner (B05) | Protocolo do ADR-0009 completo (`module` e `inline`), logs em streaming, código de saída, interpretador configurável |
| CLI (B08) | `init`, `server start/stop/status`, `doctor` (Python, diretório, porta, Docker via spike B.1), `register`, `pipelines`, `show`, `run --watch`, `runs`, `logs --follow`, `ui`, `ir schema`, `--json` |
| Interface (B08) | Lista de pipelines; detalhe com grafo React Flow somente leitura (cor/ícone por tipo); lista de runs; detalhe do run com estados por tarefa e visualizador de logs em tempo real |
| Distribuição (B14) | Instalação por `pipx` testada em Windows limpo (K5) |
| Testes | Unitários (IR, SDK, engine), integração (API + engine + executor local), equivalência tags ≡ blocos (IR construída programaticamente), e2e do fluxo da demo |

**Fora do escopo:** Docker, agendamento, retries, segredos, edição de blocos.

## Sprint 1 — Executor Docker

**Resultado demonstrável:** a tarefa `carregar` do exemplo roda em `python:3.12-slim` com logs em tempo real na interface; sem Docker, a interface e o `doctor` explicam o que falta.

| Área | Escopo |
|---|---|
| Executor Docker (B06) | Conexão e diagnóstico (spike B.1 em definitivo), pull com progresso como evento, montagem do runner e do projeto, env, limites de recurso, logs em streaming, timeout/cancel, limpeza, opção de manter contêiner em falha |
| Tipo `container` (ADR-0004) | Executa imagem + comando sem runner |
| Engine | Seleção de executor por tarefa; executor indisponível → falha clara antes de iniciar o run |
| Interface/CLI | Estado dos executores em `/info`, no `doctor` e no cabeçalho da interface |
| Testes | Integração com Docker real (marcados; pulam sem Docker), caminhos Windows ↔ contêiner |

**Pré-condição dura:** Docker Desktop instalado na máquina do PO e spike B.2 executado com sucesso (fecha K3).

## Sprint 2 — Agendamento, confiabilidade e segredos

**Resultado demonstrável:** pipeline agendada por cron dispara sozinha; servidor desligado e religado aplica a política de disparos perdidos; tarefa com falha intermitente é reexecutada; segredo usado em `${secret:DB_URL}` chega à tarefa e não aparece nos logs.

| Área | Escopo |
|---|---|
| Agendador (B09) | Laço + croniter, fuso, políticas `skip`/`run_once`/`run_all`, sem sobreposição, CRUD de agendamentos (API, CLI, interface) |
| Engine (B01) | Retries com backoff, timeout por tarefa e por run, cancelamento, limites de concorrência global/por pipeline, recuperação após queda |
| Segredos (B12) | Cofre Fernet, `secrets set/list/rm`, resolução no despacho, mascaramento em logs |
| Autenticação (B12) | Token Bearer obrigatório, `token create/revoke`, hash no banco |
| Observabilidade (B10) | Filtros e busca no histórico; duração por tarefa; retenção + `runs prune` |
| Testes | Agendador com relógio simulado; políticas de perdidos; retries; segredos nunca em `task.json`/logs |

## Sprint 3 — Construtor de blocos v1 (Fluxo B)

**Resultado demonstrável:** criar na interface uma pipeline com blocos tipados, escrever o código de cada bloco no editor, ligar entradas e saídas, salvar e executar; a IR salva é validada pelos mesmos testes de equivalência; uma pipeline vinda de tags é exibida como blocos somente leitura com botão de exportar IR/YAML.

| Área | Escopo |
|---|---|
| Interface (B04) | Paleta de tipos de ação; adicionar/remover blocos; Monaco com modelo de código por tipo; portas de entrada/saída e ligação (`inputs`) e dependência de ordem (`after`); propriedades do bloco (retries, timeout, executor, params); validação do grafo no cliente e no servidor; salvar como nova versão; executar; histórico de versões com diferenças |
| API (B07) | Mesmo endpoint de registro; endpoint de validação sem salvar; diff entre versões |
| Runner | `inline` já suportado desde a Sprint 0; reforçar limites de tamanho e mensagens de erro de sintaxe |
| Testes | Equivalência tags ≡ blocos ampliada (fixtures de pipelines reais); e2e do construtor |

## Sprint 4 — Observabilidade, alertas, extensibilidade e semântica de `branch`/`wait`

**Resultado demonstrável:** painel de métricas por pipeline; falha dispara alerta por e-mail/webhook; um plugin de exemplo adiciona um tipo de ação e aparece na paleta; `branch` pula ramos e `wait` espera um arquivo existir.

| Área | Escopo |
|---|---|
| Observabilidade (B10) | Métricas agregadas (taxa de sucesso, p50/p95, fila), página de visão geral |
| Alertas (B10, B13) | Entry point `pipeorc.alerts`; canais e-mail (SMTP) e webhook; regras por pipeline |
| Plugins (B13) | Contratos estabilizados (arquitetura §11); carregamento, isolamento de falhas, listagem; plugin de exemplo documentado |
| Engine (B01, B04) | Semântica de `branch` (saída decide `SKIPPED`) e `wait` (reexecução até condição/timeout) |
| Gatilhos (B09) | Webhook de entrada e "ao concluir outra pipeline" |
| Interface | Refino geral de usabilidade com base nas retrospectivas |

## Sprint 5 — Distribuição, operação e preparação para servidor remoto

**Resultado demonstrável:** instalador Windows instala em máquina limpa, registra o servidor para iniciar com o sistema, e a atualização preserva dados; `pipeorc backup/restore` funciona; a imagem Docker do servidor sobe em Linux e o app aponta para ela trocando o endereço.

| Área | Escopo |
|---|---|
| Distribuição (B14) | Instalador Windows (PyInstaller + Inno Setup), pacote Linux (pipx/.deb), serviço de sistema (Windows/systemd), atualização com migração e backup prévio |
| Operação (B11, B14) | `backup`/`restore`, diagnóstico completo, logs do servidor rotacionados |
| Servidor remoto (B07, B08, B12) | Imagem Docker do servidor; `config set server.url` + token no app/CLI; escuta em rede com aviso e TLS/proxy documentado; Postgres como opção (SQLAlchemy) |
| Documentação de uso | Guia de instalação, primeiro uso, tags, construtor, Docker, agendamento, segredos, API |
| Endurecimento | Varredura de dependências, revisão de segurança (§8), testes de carga leves |

**Observação:** o item "servidor remoto" é de baixo custo graças ao princípio A2, mas pode ser movido para depois da v1 por decisão do PO sem afetar os demais.

## Depois da Sprint 5

Etapa 7 — Entrega final: checklist de entrega, empacotamento assinado pelo PO, congelamento dos contratos (API v1, IR, plugins), escolha da licença (ADR-0012) e passagem para o projeto de comercialização.

## O que a Etapa 3 precisa produzir a partir deste plano

- Critérios de aceite **por sprint** (verificáveis: comando, resultado esperado, teste automatizado associado).
- DoR (item pronto para entrar: ADR relacionado aprovado, interface/contrato definido, dados de teste disponíveis).
- DoD (pronto: testes passando no `check`, documentação atualizada, CHANGELOG, demonstração executada diante do PO).
