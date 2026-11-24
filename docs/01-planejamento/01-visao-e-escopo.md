# Etapa 1 — Visão e escopo

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 1 em 2026-11-22 (decisões Q1–Q10 aplicadas) |
| Versão | 1.0 |
| Data | 2026-11-22 |

## 1. Visão

> Um orquestrador de pipelines **local-first**, instalado na máquina do usuário, que entende pipelines escritas como **código anotado com tags** ou montadas no próprio app a partir de **blocos de ação**, executa cada tarefa em processo local ou em **contêiner Docker**, e expõe uma **API aberta** para se conectar a um servidor e a ferramentas externas.

## 2. Problema que resolve

1. Orquestradores consolidados (Prefect, Airflow, Dagster) nasceram *server-first*: exigem infraestrutura, banco e, muitas vezes, conta em nuvem para funcionalidades centrais. Para um desenvolvedor ou equipe pequena, o custo de entrada é alto.
2. Ferramentas visuais (n8n, Node-RED) resolvem integrações, mas tratam código próprio como cidadão de segunda classe: difícil versionar, testar e reaproveitar.
3. Não existe ponte natural entre os dois mundos: quem começa no código não consegue visualizar e editar em blocos; quem começa em blocos não consegue levar para o código.

## 3. Proposta de valor (diferenciais)

| # | Diferencial | O que significa na prática |
|---|---|---|
| D1 | **Local-first** | Instala, roda e agenda pipelines na máquina sem servidor externo. O servidor remoto é opção, não pré-requisito. |
| D2 | **Duas portas de entrada, uma definição** | Tags no código e blocos no app geram a **mesma definição de pipeline**. Uma pipeline nascida em tags aparece como blocos no app; uma nascida em blocos pode ser exportada. |
| D3 | **Docker como executor de primeira classe** | Qualquer tarefa pode rodar em contêiner com imagem, variáveis e volumes declarados, com logs capturados no app. |
| D4 | **API aberta desde o início** | O app local é apenas um cliente da API. Tudo que o app faz, um sistema externo também faz. |

## 4. Público-alvo (personas iniciais — proposta)

| Persona | Situação | O que precisa |
|---|---|---|
| **Desenvolvedor / analista de dados** | Já tem scripts (Python, SQL, shell) espalhados e agendados por hora/Task Scheduler/cron. | Anotar o código que já existe e passar a ter agendamento, retries, histórico e logs, sem montar infra. |
| **Usuário técnico intermediário** | Sabe escrever trechos de código, mas prefere montar o fluxo visualmente. | Criar blocos, colar o código em cada um, ligar e executar. |
| **Equipe pequena** (Fase 2) | Precisa de um ponto central para pipelines compartilhadas. | Um servidor com API aberta, com cada membro usando o app local como cliente. Atendida quando a conexão a servidor remoto entrar (Q1). |

## 5. Referências de mercado (benchmark resumido)

Objetivo: saber **o que aproveitar** e **o que evitar**, não copiar.

| Ferramenta | Modelo de definição | Instalação local | O que aproveitar | O que evitar |
|---|---|---|---|---|
| **Prefect** | Decorators Python (`@flow`, `@task`) | Servidor self-hosted possível | Ergonomia dos decorators; máquina de estados dos runs; conceito de workers | Funcionalidades centrais dependentes da nuvem |
| **Airflow** | DAGs em Python | Pesada para uso individual | Maturidade de agendamento e de operadores | Complexidade de setup; acoplamento ao scheduler |
| **Dagster** | `@asset` / `@op` em Python | Modo dev local razoável | Tipagem de entradas/saídas; linhagem de dados | Curva de aprendizado alta; vocabulário próprio extenso |
| **Kestra** | YAML declarativo + plugins | Via Docker | Definição declarativa e serializável (próxima da nossa IR) | YAML como única interface de autoria |
| **Windmill** | Scripts como funções + construtor visual de fluxos | Self-host via Docker | É a referência mais próxima do Fluxo B: script como unidade, construtor em cima | Dependência total de banco/servidor para rodar qualquer coisa |
| **n8n / Node-RED** | Nós visuais | Sim | UX do construtor de blocos; catálogo de nós | Código como exceção, não como regra |

## 6. Escopo macro — o que entra

1. Motor de orquestração (DAG, estados, retries, dependências).
2. Definição de pipeline unificada (IR) serializável e versionável.
3. SDK com tags para o Fluxo A (código → sistema).
4. Construtor de blocos para o Fluxo B (sistema → pipeline).
5. Executores Local e Docker.
6. Servidor com API aberta (REST + eventos) documentada por OpenAPI.
7. App local (interface gráfica + CLI) que funciona contra servidor local ou remoto.
8. Agendamento e gatilhos.
9. Observabilidade: histórico de runs, logs, estado, alertas básicos.
10. Persistência local simples por padrão, com opção de banco externo.
11. Segredos e configuração por projeto.
12. Base de extensibilidade (plugins) e distribuição (instalador, atualização).

O detalhamento de cada item está em [02-blocos-funcionais.md](02-blocos-funcionais.md).

## 7. Não-objetivos da v1 (proposta — validar)

| # | Fora do escopo | Motivo |
|---|---|---|
| N1 | Orquestrar infraestrutura (substituir Kubernetes, Terraform) | Outro problema. O Docker aqui é executor de tarefas, não gerenciador de cluster. |
| N2 | BI / visualização de dados | O app mostra estado de pipelines, não dashboards de negócio. |
| N3 | SaaS multi-tenant | Comercialização é o projeto seguinte; só a **direção** entra na Etapa 2 (ajuste P6). |
| N4 | Suporte a todas as linguagens no Fluxo A | Python primeiro (Q2), com decorators (Q4). O Fluxo B pode aceitar mais linguagens cedo, porque o bloco já isola o código. |
| N5 | IDE completa embutida | O construtor terá um editor simples por bloco. O IDE do usuário continua sendo a ferramenta principal de código. |
| N6 | Execução distribuída em múltiplas máquinas | A abstração de executor deixa a porta aberta; a implementação fica para depois da v1. |

## 8. Premissas e restrições

| # | Premissa |
|---|---|
| R1 | Sistemas operacionais alvo da v1: **Windows** (ambiente do PO) e **Linux** (servidores). macOS na Fase 2 (Q10). |
| R2 | Docker Desktop ou Docker Engine instalado é pré-requisito **apenas** para o executor Docker. O executor Local funciona sem Docker. |
| R3 | A API aberta é REST com especificação OpenAPI publicada, mais um canal de eventos (WebSocket ou SSE) para logs e estado em tempo real. |
| R4 | O servidor é um só código. **No MVP roda localmente**, instalado junto com o app (Q1). Rodar em outra máquina é Fase 2 e exige apenas trocar o endereço no app, porque a API é a mesma. |
| R5 | Tudo o que o app faz passa pela API. Não existe atalho interno. É esta regra que garante R4. |
| R6 | Stack: **Python** no servidor, SDK, CLI e runner; interface **web** (Q3). Formalizado no ADR-0001. |
| R7 | O nome do produto fica para o final (Q8). O código usa o identificador técnico provisório `pipeorc`. |

## 9. Riscos iniciais e mitigação

| # | Risco | Mitigação prevista |
|---|---|---|
| K1 | Interpretar tags em código arbitrário de forma robusta | Spike (a) na Etapa 2; começar com uma forma de tag (decorator) e uma linguagem |
| K2 | Garantir que tags e blocos geram a mesma IR, sempre | IR definida **antes** dos dois fluxos; spike (c); testes de equivalência desde a Sprint 0 |
| K3 | Docker no Windows (Desktop/WSL2) tem variações de ambiente | Spike (b) rodando no ambiente real do PO; detectar e reportar ambiente no app |
| K4 | Escopo amplo — risco de construir "dois produtos" (orquestrador + construtor) | IR unificada como coluna vertebral; MVP tags-first (Q6, aprovado); construtor consome a IR pronta |
| K5 | Distribuição em Windows (instalador, antivírus, atualização) | Decidir empacotamento na Etapa 2 (ADR); testar instalador limpo na Sprint 0 |
