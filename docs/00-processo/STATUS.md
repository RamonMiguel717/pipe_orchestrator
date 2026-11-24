# STATUS — acompanhamento do projeto

Atualizado em: **2026-11-22**

## Visão geral

| Etapa | Documentos de saída | Status | Gate |
|---|---|---|---|
| 0. Processo | [metodologia.md](metodologia.md) v1.0, [glossario.md](glossario.md) v1.1 | `Aprovado` | Fechado nos Gates 1 e 2 |
| 1. Planejamento | [01-visao-e-escopo.md](../01-planejamento/01-visao-e-escopo.md) v1.0, [02-blocos-funcionais.md](../01-planejamento/02-blocos-funcionais.md) v1.0, [03-perguntas-para-validacao.md](../01-planejamento/03-perguntas-para-validacao.md) v1.0 | `Aprovado` | **Gate 1 aprovado em 2026-11-22** |
| 2. Arquitetura | [00-plano-da-etapa.md](../02-arquitetura/00-plano-da-etapa.md), [relatorio-spikes.md](../02-arquitetura/relatorio-spikes.md), [adr/ (12 ADRs `Aceito`)](../02-arquitetura/adr/README.md), [01-arquitetura.md](../02-arquitetura/01-arquitetura.md), [02-plano-de-sprints.md](../02-arquitetura/02-plano-de-sprints.md) | `Aprovado` | **Gate 2 aprovado em 2026-11-22** |
| 3. Critérios de aceite | [00-plano-da-etapa.md](../03-criterios-aceite/00-plano-da-etapa.md), [01-definition-of-ready.md](../03-criterios-aceite/01-definition-of-ready.md), [02-definition-of-done.md](../03-criterios-aceite/02-definition-of-done.md), [sprint-0](../03-criterios-aceite/sprint-0.md) a [sprint-5](../03-criterios-aceite/sprint-5.md) | `Em validação` | **Gate 3 pendente** |
| 4–6. Sprints | — | Não iniciadas | Sprint 0 começa após o Gate 3 |
| 7. Entrega final | — | Não iniciada | — |

## Spikes (P2)

| Spike | Estado | Observação |
|---|---|---|
| A — Tags (forma explícita) | Concluído, superado | Forma considerada pesada pelo PO; conclusões sobre descoberta mantidas |
| A2 — Tags simples com inferência | Concluído, OK (v0.3) | `@step`/`@test`/`@pipeline`, só dados ordenam, `@test` portão, `wait_for=`, 8 erros claros, modo dev. T1–T4 e C1/C2 decididos pelo PO → ADR-0003 `Aceito` |
| B — Docker | B.1 concluído; **B.2 bloqueado** | Docker Desktop não instalado nesta máquina (WSL2 presente). Pendência A1 do PO antes da Sprint 1 |
| C — IR unificada | Concluído, OK | Equivalência tags ≡ blocos provada; schema válido |

## Próxima ação

**Product Owner:** validar o Gate 3 — DoR, DoD e os critérios das Sprints 0 a 5 (em bloco, com ajustes pontuais ou movendo critérios entre sprints).
**Agente:** após o Gate 3, iniciar a Sprint 0 (Etapa 4) com `git init` e o esqueleto andante.

## Pendências abertas

| # | Pendência | Responsável | Necessária para |
|---|---|---|---|
| A1 | Instalar Docker Desktop e rodar `spikes/spike_b_docker/run_task_in_docker.py` | PO | Sprint 1 (pré-condição dura; fecha risco K3) |
| A2 | Repositório com remoto no GitHub? | PO | Não bloqueia; Sprint 0 começa com git local |

## Decisões recentes

| Data | Decisão |
|---|---|
| 2026-11-22 | Gate 2 aprovado em bloco: 11 ADRs restantes, arquitetura, plano de sprints, glossário v1.1 |
| 2026-11-22 | A3: interface e CLI em pt-BR com catálogo de textos; código, API e identificadores em inglês (recomendação aceita) |
| 2026-11-22 | Tags: T1–T4 e C1–C2 (ver ADR-0003) |

## Histórico de gates

| Data | Gate | Decisão | Ressalvas aceitas |
|---|---|---|---|
| 2026-11-22 | Gate 1 (Planejamento) | **Aprovado.** Q1–Q10 respondidas; P1–P8 aceitos. | Nome do produto adiado para o final (Q8); identificador técnico `pipeorc` no código. Servidor remoto fora do MVP (Q1). |
| 2026-11-22 | Gate 2 (Arquitetura) | **Aprovado.** 12 ADRs `Aceito`; arquitetura e plano de sprints v1.0. | Spike B.2 pendente de Docker (A1) até a Sprint 1; remoto GitHub (A2) em aberto sem bloquear. |
| — | Gate 3 (Critérios de aceite) | Pendente | — |

## Registro de mudanças deste arquivo

| Data | Mudança |
|---|---|
| 2026-11-22 | Criação; Etapa 0 e Etapa 1 em rascunho |
| 2026-11-22 | Gate 1 aprovado; Etapa 2 iniciada |
| 2026-11-22 | Spikes executados; ADRs, arquitetura e plano de sprints entregues para o Gate 2 |
| 2026-11-22 | Feedback do PO sobre as tags; spike A2; ADR-0003/0004 v0.2; glossário v1.1 em validação |
| 2026-11-22 | T1–T4 respondidas (só dados ordenam); spike A2 v0.3; ADR-0003 v0.3 |
| 2026-11-22 | C1/C2 confirmados pelo PO; ADR-0003 `Aceito` v1.0 |
| 2026-11-22 | Gate 2 aprovado; Etapa 3 entregue para o Gate 3 |
