# Etapa 2 — Plano da etapa (refinamento e arquitetura)

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 2 em 2026-11-22 |
| Versão | 1.0 |
| Data | 2026-11-22 |

## 1. Objetivo

Transformar os blocos funcionais aprovados na Etapa 1 em uma arquitetura concreta, com decisões registradas (ADRs), riscos técnicos reduzidos por spikes e um plano de sprints que a Etapa 3 possa cobrir com critérios de aceite.

## 2. Entradas

- Etapa 1 aprovada (Gate 1, 2026-11-22): visão/escopo, blocos B01–B14, glossário.
- Decisões Q1–Q10: servidor único local no MVP; Python com decorators; stack Python + web; taxonomia única; MVP tags-first; Windows + Linux; direção open-core; nome adiado.
- Ajustes P2 (spikes), P3 (ADRs), P4 (Sprint 0), P6 (direções comerciais).

## 3. Saídas (artefatos do Gate 2)

| Artefato | Arquivo | Status |
|---|---|---|
| Relatório dos spikes | [relatorio-spikes.md](relatorio-spikes.md) | `Aprovado` |
| Registro de decisões (12 ADRs) | [adr/](adr/README.md) | Todos `Aceito` (ADR-0003 por decisões individuais; os demais no Gate 2) |
| Documento de arquitetura | [01-arquitetura.md](01-arquitetura.md) | `Aprovado` |
| Plano de sprints | [02-plano-de-sprints.md](02-plano-de-sprints.md) | `Aprovado` |
| Direções comerciais (P6) | [ADR-0012](adr/ADR-0012-direcoes-comerciais.md) | `Aceito` |

## 4. Spikes executados (P2)

| Spike | Pergunta | Resultado |
|---|---|---|
| A — Tags (v0.1) | Decorators descrevem tarefa, tipo, dependências e executor, e viram IR com erros claros? | **Sim**, mas a forma (`Pipeline` + `inputs=`/`after=`) foi considerada pesada pelo PO. Superado por A2. |
| A2 — Tags simples | Tags nuas (`@step`, `@test`, `@pipeline`) com o grafo **inferido** dão ao usuário simplicidade e ao sistema a visualização completa? | **Sim.** Só dados ordenam (T4), `@test` como portão, `wait_for=` para ordem sem dados, 8 erros claros, modo de desenvolvimento sem servidor. |
| B — Docker | Rodamos uma tarefa em contêiner com volume, env, logs em tempo real e código de saída? O que o usuário vê sem Docker? | **Parcial.** Diagnóstico validado (Docker ausente nesta máquina, WSL2 presente). Execução real bloqueada até instalar o Docker Desktop. |
| C — IR | Tags e blocos geram a mesma IR validável por esquema? | **Sim.** Equivalência semântica provada; única diferença é a referência de código (módulo vs inline), tratada pelo runner. |

Detalhes em [relatorio-spikes.md](relatorio-spikes.md).

## 5. Como funciona o Gate 2

1. O PO lê o relatório dos spikes e a arquitetura.
2. Aprova os ADRs **um a um** (ou em bloco, dizendo "aprovo todos"), podendo rejeitar ou pedir ajuste em qualquer um.
3. Aprova o plano de sprints (ordem e escopo; estimativas não são compromisso de calendário).
4. Com tudo aprovado, a Etapa 3 escreve os critérios de aceite por sprint, DoR e DoD.

## 6. Questões de desenho das tags — respondidas pelo PO em 2026-11-22

| # | Questão | Decisão |
|---|---|---|
| T1 | `@executor` = a função que executa o fluxo? | Sim; nome adotado `@pipeline` |
| T2 | Tags em inglês ou português | Inglês |
| T3 | Características por kwargs ou tags empilhadas | kwargs |
| T4 | Ordem padrão sequencial ou só dados ordenam | **Só dados ordenam** (a interface mostra a execução) |

Consequências de T4 **confirmadas pelo PO** em 2026-11-22 ([ADR-0003](adr/ADR-0003-tags-decorators.md)): C1 `@test` como portão do que vem depois; C2 `wait_for=` reservado para ordem sem dados. Com isso o ADR-0003 passou a `Aceito`; os demais ADRs seguem `Proposto` para o Gate 2.

## 7. Pendências que não dependem do agente

| # | Pendência | Responsável | Quando é necessária |
|---|---|---|---|
| A1 | Instalar o **Docker Desktop** nesta máquina (WSL2 já está presente) e executar `spikes/spike_b_docker/run_task_in_docker.py` para fechar o spike B | PO | Antes da Sprint 1 — **aberta** |
| A2 | Decidir se o repositório terá remoto no GitHub (necessário para CI em nuvem; opcional para CI local) | PO | Sprint 0 — **aberta, não bloqueia**: a Sprint 0 começa com git local e o remoto pode ser adicionado a qualquer momento |
| A3 | Idioma da interface e das mensagens da CLI | PO | **Decidido no Gate 2 (recomendação aceita):** pt-BR com catálogo de textos; código, API e identificadores em inglês |
