# Etapa 1 — Blocos funcionais e responsabilidades

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 1 em 2026-11-22 (decisões Q1–Q10 aplicadas) |
| Versão | 1.0 |
| Data | 2026-11-22 |

Este é o documento principal da Etapa 1: **o que** o sistema precisa ter e **de que** cada parte é responsável, em blocos gerais. Conforme combinado, **sem detalhes de implementação** (isso é Etapa 2).

Cada bloco tem: responsabilidade, o que **não** é responsabilidade dele (para evitar sobreposição), de quem depende, e a **prioridade proposta** — `MVP` (entra no esqueleto andante ou nas primeiras sprints), `Fase 2` (depois do MVP, ainda dentro da v1) ou `Futuro` (depois da v1).

## 1. Fluxos principais (visão macro)

```
FLUXO A — código com tags
  código do usuário ──[SDK: tags]──► descoberta ──► Definição (IR) ──► Servidor ──► Engine ──► Executor ──► Run/logs ──► App

FLUXO B — construtor de blocos
  usuário no App ──[blocos tipados + código]──► Definição (IR) ──► Servidor ──► Engine ──► Executor ──► Run/logs ──► App

FLUXO C — integração externa
  sistema externo ──[API aberta]──► dispara / consulta / recebe eventos ◄── Servidor
```

Ponto central: **tudo converge na Definição de pipeline (IR)**. Os fluxos A e B são formas de produzi-la; o restante do sistema só conhece a IR.

## 2. Mapa de dependências entre blocos

```
                 ┌──────────────────────┐
                 │ B08 App local (UI+CLI)│
                 └──────────┬───────────┘
                            │ usa
                 ┌──────────▼───────────┐
   B03 SDK Tags ─►  B07 API aberta      ◄─ sistemas externos (Fluxo C)
   B04 Blocos   ─►                      │
                 └──────────┬───────────┘
                            │
      ┌─────────────────────▼──────────────────────┐
      │ B01 Engine ─ B02 IR ─ B09 Agendamento      │  Servidor
      │ B10 Observabilidade ─ B11 Persistência      │
      │ B12 Segurança/Config ─ B13 Plugins          │
      └─────────────────────┬──────────────────────┘
                            │ despacha
                 ┌──────────▼───────────┐
                 │ B05 Executores        │
                 │   Local │ Docker(B06) │
                 └──────────────────────┘
                 B14 Distribuição/Operação (transversal: empacota tudo)
```

## 3. Blocos

### B01 — Motor de orquestração (Engine)

| | |
|---|---|
| **Responsabilidade** | Receber uma Definição (IR) e um gatilho; resolver a ordem de execução pelas dependências; criar o Run e os estados por tarefa; despachar cada tarefa ao executor indicado; aplicar retries, timeouts e limites de concorrência; propagar falhas conforme a política definida; registrar transições de estado. |
| **Não é responsável por** | Interpretar código do usuário (B03/B04); rodar código (B05); expor rede (B07); persistir diretamente (usa B11). |
| **Depende de** | B02, B05, B11 |
| **Prioridade** | `MVP` |

### B02 — Definição de pipeline (IR unificada)

| | |
|---|---|
| **Responsabilidade** | Definir o modelo canônico de uma pipeline: tarefas, tipo de ação de cada uma, dependências, parâmetros, entradas/saídas, executor e recursos de cada tarefa, metadados (nome, versão, projeto). Ser serializável (JSON/YAML), validável por esquema e versionável. Garantir que o que o Fluxo A e o Fluxo B produzem seja **indistinguível** para o restante do sistema. |
| **Não é responsável por** | Executar (B01), armazenar (B11), apresentar (B08). |
| **Depende de** | — (é a base) |
| **Prioridade** | `MVP` — primeiro item a ser desenhado na Etapa 2 |

### B03 — SDK de tags (Fluxo A: código → sistema)

| | |
|---|---|
| **Responsabilidade** | Oferecer as tags que o usuário coloca no código para marcar tarefas, tipo de ação, dependências, retries e executor; descobrir tags em um arquivo/pasta/projeto; traduzir para a IR; registrar no servidor via API; permitir executar localmente a partir do código (modo desenvolvimento). Validar e reportar tags malformadas com mensagens claras. |
| **Não é responsável por** | Rodar a pipeline (B01/B05); UI (B08). |
| **Depende de** | B02, B07 |
| **Prioridade** | `MVP` — Python com decorators (Q2, Q4). Outras linguagens e comentários estruturados na Fase 2. |

### B04 — Construtor de blocos (Fluxo B: sistema → pipeline)

| | |
|---|---|
| **Responsabilidade** | Permitir criar uma pipeline dentro do app: adicionar blocos escolhendo o tipo de ação (que vira a tag do bloco); escrever o código de cada bloco em editor simples; declarar entradas/saídas e ligar blocos; configurar executor e parâmetros por bloco; validar o grafo; salvar como IR; executar; exportar (IR e, futuramente, código anotado com tags equivalente). Mostrar uma pipeline vinda do Fluxo A como blocos (somente leitura no MVP). |
| **Não é responsável por** | Ser um IDE completo (não-objetivo N5); executar (B01/B05). |
| **Depende de** | B02, B07, B08 |
| **Prioridade** | `MVP` reduzido (visualização de pipelines como blocos) → `Fase 2` (criação e edição completas). Ordem aprovada em Q6. |

### B05 — Executores (Runtimes)

| | |
|---|---|
| **Responsabilidade** | Executar o código de **uma tarefa** em um ambiente isolado e devolver resultado, estado e logs ao Engine. Expor uma interface única para que o Engine não saiba qual executor está por trás. Executores previstos: **Local** (subprocesso na máquina, com ambiente/venv configurável) e **Docker** (B06). Passar parâmetros/segredos à tarefa e coletar artefatos. |
| **Não é responsável por** | Decidir ordem (B01); construir imagens de aplicação do usuário além do que B06 define. |
| **Depende de** | B02, B12 (segredos) |
| **Prioridade** | `MVP` — Local no esqueleto andante; Docker na sprint seguinte |

### B06 — Integração Docker

| | |
|---|---|
| **Responsabilidade** | Detectar e conectar ao Docker disponível na máquina (Desktop/Engine, Windows/Linux); gerenciar imagens (pull, build a partir de Dockerfile do projeto, cache); criar e executar contêineres por tarefa com variáveis, volumes, rede e limites de recurso declarados na IR; transmitir logs em tempo real; limpar contêineres ao fim; reportar erros de ambiente de forma compreensível. |
| **Não é responsável por** | Orquestrar clusters (não-objetivo N1); compose multi-serviço como unidade de pipeline (avaliar em `Futuro`). |
| **Depende de** | B05 |
| **Prioridade** | `MVP` |

### B07 — API aberta (Servidor)

| | |
|---|---|
| **Responsabilidade** | Expor toda a funcionalidade do servidor: CRUD de projetos e pipelines (IR), disparo e cancelamento de runs, consulta de estado e histórico, stream de logs/eventos, agendamentos, segredos (escrita), saúde do servidor. Publicar especificação OpenAPI. Autenticar chamadas (token/API key). Versionar a API. Ser o **único** caminho de entrada ao servidor, inclusive para o app local. |
| **Não é responsável por** | Lógica de orquestração (B01); UI (B08). |
| **Depende de** | B01, B02, B09, B10, B11, B12 |
| **Prioridade** | `MVP` |

### B08 — Aplicativo local (interface gráfica + CLI)

| | |
|---|---|
| **Responsabilidade** | Instalar na máquina do usuário. **CLI:** iniciar/parar servidor local, registrar código com tags, executar pipeline, consultar runs e logs. **Interface gráfica (web):** listar projetos e pipelines; ver pipelines como grafo/blocos; disparar e acompanhar runs com logs em tempo real; configurar agendamentos; hospedar o construtor de blocos (B04). No MVP fala com o servidor local (Q1); na Fase 2 ganha gerência de conexões e aponta para servidor remoto sem mudança de arquitetura. |
| **Não é responsável por** | Conter lógica de negócio do orquestrador (tudo via B07). |
| **Depende de** | B07 |
| **Prioridade** | `MVP` — CLI completa + interface gráfica mínima (lista, grafo, runs, logs) |

### B09 — Agendamento e gatilhos

| | |
|---|---|
| **Responsabilidade** | Disparar runs por: manual, cron/intervalo, chamada à API, webhook, conclusão de outra pipeline. Manter agendamentos ativos enquanto o servidor estiver de pé; registrar disparos perdidos quando o servidor estava desligado e aplicar a política configurada (ignorar / executar uma vez / executar todos). Evitar sobreposição de runs quando configurado. |
| **Não é responsável por** | Executar (B01). |
| **Depende de** | B01, B11 |
| **Prioridade** | `MVP` (manual, cron, API) → `Fase 2` (webhook, encadeamento) |

### B10 — Observabilidade

| | |
|---|---|
| **Responsabilidade** | Histórico de runs e tarefas com estados, duração e parâmetros; logs por tarefa (tempo real e histórico); métricas básicas (sucesso/falha, duração, fila); alertas/notificações em falha (e-mail, webhook, outros via plugin); retenção configurável. |
| **Não é responsável por** | BI (não-objetivo N2). |
| **Depende de** | B01, B05, B11 |
| **Prioridade** | `MVP` (histórico + logs) → `Fase 2` (métricas, alertas) |

### B11 — Persistência e estado

| | |
|---|---|
| **Responsabilidade** | Armazenar definições (IR), runs, estados, logs, agendamentos, segredos cifrados, configuração. Banco local embutido por padrão (zero configuração) com opção de banco externo para servidor compartilhado. Migrações de esquema; backup/restauração; armazenamento de artefatos (sistema de arquivos local por padrão, abstração para outros). |
| **Não é responsável por** | Regras de negócio. |
| **Depende de** | — |
| **Prioridade** | `MVP` |

### B12 — Segurança e configuração

| | |
|---|---|
| **Responsabilidade** | Cofre de segredos por projeto (cifrados em repouso, injetados na tarefa em execução, nunca expostos em logs); configuração por projeto e por ambiente (dev/prod); autenticação da API (token/API key); controle de acesso básico quando houver servidor compartilhado (ver P6, multiusuário). |
| **Não é responsável por** | Gestão de identidade corporativa (SSO) na v1 → `Futuro`. |
| **Depende de** | B11 |
| **Prioridade** | `MVP` (segredos + token da API) → `Fase 2` (controle de acesso) |

### B13 — Extensibilidade (plugins e conectores)

| | |
|---|---|
| **Responsabilidade** | Definir os pontos de extensão: novos **tipos de ação** (que viram tags e blocos), novos **executores**, novos **conectores** e **canais de alerta**. Descobrir, instalar, versionar e isolar plugins. Oferecer conectores básicos de fábrica (arquivos, HTTP, bancos SQL comuns). |
| **Não é responsável por** | Marketplace (projeto comercial). |
| **Depende de** | B02, B05, B10 |
| **Prioridade** | `Fase 2` — mas as **interfaces** de extensão são desenhadas na Etapa 2 para não travar o núcleo |

### B14 — Distribuição e operação

| | |
|---|---|
| **Responsabilidade** | Instalador para Windows e Linux (e macOS, se confirmado); imagem Docker do servidor para instalação remota; atualização do app e do servidor com migração de dados; diagnóstico de ambiente (Docker presente? versão? permissões?); desinstalação limpa; logs do próprio sistema. |
| **Não é responsável por** | Hospedagem gerenciada (projeto comercial). |
| **Depende de** | todos |
| **Prioridade** | `MVP` mínimo (instalador simples testado na Sprint 0) → `Fase 2` (atualização automática) |

## 4. Resumo de prioridades (aprovado em Q6)

| Bloco | MVP | Fase 2 | Futuro |
|---|---|---|---|
| B01 Engine | ✔ núcleo | políticas avançadas de falha | — |
| B02 IR | ✔ completa | versionamento com diff | — |
| B03 SDK tags | ✔ 1 linguagem, 1 forma de tag | outras formas/linguagens | — |
| B04 Construtor | visualização | criação/edição completas, exportar código | colaboração |
| B05 Executores | ✔ Local + Docker | — | remoto, k8s |
| B06 Docker | ✔ run por tarefa, logs | build/cache avançado | compose |
| B07 API | ✔ | webhooks de saída | — |
| B08 App | ✔ CLI + UI mínima (servidor local) | UI completa; conexão a servidor remoto | — |
| B09 Agendamento | ✔ manual, cron, API | webhook, encadeamento | — |
| B10 Observabilidade | ✔ histórico, logs | métricas, alertas | — |
| B11 Persistência | ✔ local embutido | banco externo | — |
| B12 Segurança | ✔ segredos, token | controle de acesso | SSO |
| B13 Plugins | interfaces desenhadas | implementação | marketplace |
| B14 Distribuição | ✔ instalador simples | atualização automática | — |

## 5. O que fica explicitamente para a Etapa 2

- Linguagens e frameworks de cada bloco.
- Formato exato da IR e das tags.
- Protocolos (REST/eventos), esquema do banco, estrutura de pastas.
- Divisão em sprints e estimativas.
- Resultado dos spikes (P2) e ADRs (P3).
