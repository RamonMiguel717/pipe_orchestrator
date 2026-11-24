# Pipe Orchestrator (nome provisório)

Orquestrador de pipelines **local-first**: instalado na máquina, com **API aberta** para conexão com servidor e **Docker** como executor de primeira classe.

Duas portas de entrada para definir uma pipeline, que convergem para a mesma definição interna:

1. **Código com tags** — o desenvolvedor anota o próprio código com tags; o sistema interpreta e monta a pipeline.
2. **Construtor de blocos** — dentro do app, o usuário cria blocos de ação (cada um com a tag do tipo de ação) e compartimenta o código em cada bloco.

## Estado atual

| Etapa | Situação |
|---|---|
| 1. Planejamento | **Aprovada** (Gate 1 em 2026-11-22) |
| 2. Arquitetura | **Aprovada** (Gate 2 em 2026-11-22): 12 ADRs, arquitetura, plano de 6 sprints |
| 3. Critérios de aceite | Em validação: DoR, DoD e critérios das Sprints 0 a 5 aguardam o Gate 3 |
| 4 a 7 | Não iniciadas; a Sprint 0 começa após o Gate 3 |

Decisões já tomadas: servidor único local no MVP; stack Python (FastAPI) + interface web React; tags como decorators nus em inglês (`@pipeline`, `@step`, `@test`, `@extract`, …) com o grafo inferido pelo fluxo de dados; taxonomia única de tipos de ação para tags e blocos; MVP tags-first; Windows e Linux na v1; direção open-core; interface em pt-BR. O nome do produto fica para o final; `pipeorc` é só o identificador técnico do código.

Acompanhamento detalhado em [docs/00-processo/STATUS.md](docs/00-processo/STATUS.md).

## Documentação

Toda a documentação de planejamento, arquitetura, critérios de aceite e acompanhamento fica em [docs/](docs/README.md). Nenhuma etapa avança sem o documento de saída aprovado pelo Product Owner.
