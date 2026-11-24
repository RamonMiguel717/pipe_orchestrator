# Glossário

| Campo | Valor |
|---|---|
| Status | `Aprovado` — v1.1 (Gate 2) ajusta "Tag" e "Tipo de ação" ao ADR-0003; v1.0 aprovada no Gate 1 |
| Versão | 1.1 |
| Data | 2026-11-22 |

Vocabulário único do projeto. Todo documento e todo nome no código devem usar estes termos. Alterações geram nova versão e passam por validação do PO.

## Conceitos do produto

| Termo | Definição |
|---|---|
| **Pipeline** | Conjunto ordenado de tarefas com dependências entre si (um grafo acíclico dirigido, DAG). É a unidade que se agenda, executa e acompanha. |
| **Tarefa (Task)** | Menor unidade executável de uma pipeline. Tem entradas, saídas, um tipo de ação e um corpo de código. |
| **Tipo de ação** | Categoria que classifica o que uma tarefa faz. Taxonomia **única** (Q5), usada igualmente pelas tags no código e pelos blocos no construtor, fixa no núcleo e extensível por plugin. **Os nomes dos tipos são os nomes das tags:** `step` (genérico, padrão), `test`, `extract`, `transform`, `load`, `notify`, `container`, `branch`, `wait` (ADR-0004 v0.2). |
| **Tag** | Decorator Python **nu** colocado no código do usuário: `@step`, `@test`, `@extract`, … marcam uma função como passo e dizem o seu tipo; `@pipeline` marca a função que descreve o fluxo chamando os passos. Dependências e parâmetros são **inferidos** pelo sistema a partir do fluxo de dados (só dados ordenam; `@test` é portão; `wait_for=` impõe ordem sem dados); características (`retries=`, `timeout=`, `docker=`) só quando necessário (ADR-0003 v0.3). Comentários estruturados para outras linguagens ficam para a Fase 2. |
| **Bloco** | Tarefa criada **dentro do app**, pelo construtor. Recebe o tipo de ação como sua tag e contém o código compartimentado escrito pelo usuário. Um bloco e uma tarefa anotada por tag produzem a mesma coisa internamente. |
| **Construtor de blocos** | Área do app onde o usuário monta uma pipeline criando blocos, escrevendo o código de cada um e ligando entradas e saídas. |
| **Definição de pipeline (IR)** | Representação canônica, serializável (JSON/YAML), de uma pipeline: tarefas, tipos, dependências, parâmetros, executor de cada tarefa. É o **ponto de convergência** entre tags e blocos e o que o servidor armazena e executa. "IR" vem de *intermediate representation*. |
| **Fluxo A — código com tags** | Caminho em que o usuário escreve código anotado, o SDK descobre as tags e registra a definição no servidor. |
| **Fluxo B — construtor de blocos** | Caminho em que o usuário monta a pipeline no app e o próprio app gera a definição. |
| **Run (Execução)** | Uma ocorrência de execução de uma pipeline, com estado (agendada, em execução, sucesso, falha, cancelada), início, fim e logs. Cada tarefa dentro de um run tem o seu próprio estado. |
| **Executor (Runtime)** | Componente que efetivamente roda o código de uma tarefa. Tipos previstos: **Local** (processo/subprocesso na máquina) e **Docker** (contêiner). Abstração aberta para futuros (remoto, Kubernetes). |
| **Agendamento** | Regra que dispara runs automaticamente (cron, intervalo). |
| **Gatilho** | Evento que inicia um run: manual, agendamento, chamada à API, webhook, conclusão de outra pipeline. |
| **Artefato** | Saída persistida de uma tarefa (arquivo, tabela, objeto) que pode ser consumida por outra tarefa ou inspecionada depois. |
| **Conector** | Integração pronta com um sistema externo (banco, API, armazenamento) usada por blocos ou pelo SDK. |
| **Plugin** | Extensão instalável que adiciona tipos de ação, executores ou conectores. |
| **Projeto (Workspace)** | Agrupamento lógico de pipelines, segredos e configurações. |

## Componentes do sistema

| Termo | Definição |
|---|---|
| **Servidor** | Processo que contém o motor de orquestração, a persistência e a **API aberta**. No MVP roda na mesma máquina do app (Q1); rodar em outra máquina é Fase 2 e não muda a API. |
| **API aberta** | Interface pública, documentada (OpenAPI), pela qual o app local, o SDK e sistemas externos falam com o servidor. |
| **App local** | Aplicativo instalado na máquina do usuário: interface gráfica (web) + linha de comando (CLI). É um **cliente da API aberta**; no MVP conecta-se ao servidor local, na Fase 2 também a um servidor remoto. |
| **SDK** | Biblioteca que o usuário importa no código para usar as tags e para registrar/executar pipelines a partir do próprio código. |
| **Motor de orquestração (Engine)** | Parte do servidor que resolve dependências, agenda, despacha tarefas para executores e mantém o estado dos runs. |

## Termos de processo

| Termo | Definição |
|---|---|
| **Gate** | Ponto de validação pelo PO que libera a etapa seguinte. |
| **Sprint** | Ciclo de desenvolvimento com escopo fechado, que termina em gate próprio. |
| **Spike** | Prova de conceito curta e descartável para reduzir incerteza técnica antes de uma decisão. |
| **ADR** | *Architecture Decision Record*: registro curto de uma decisão de arquitetura (contexto, alternativas, decisão, consequências). |
| **DoR / DoD** | *Definition of Ready* / *Definition of Done*: critérios para um item entrar numa sprint e para ser considerado pronto. |
| **Esqueleto andante** | Primeira entrega: fatia fina de ponta a ponta que atravessa todos os componentes com funcionalidade mínima. |
