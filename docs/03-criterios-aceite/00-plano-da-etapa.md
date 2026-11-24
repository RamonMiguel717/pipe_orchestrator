# Etapa 3 — Critérios de aceite, Definition of Ready e Definition of Done

| Campo | Valor |
|---|---|
| Status | `Em validação` — entregue ao PO para o Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |

## 1. Objetivo

Definir, **antes de escrever código**, o que cada sprint precisa conter e cumprir para que o PO possa aprová-la e liberar a seguinte (ajuste P1), e as duas listas fixas que valem para todas: o que um item precisa ter para entrar numa sprint (DoR) e para ser considerado pronto (DoD) (ajuste P5).

## 2. Entradas

- Etapa 2 aprovada (Gate 2, 2026-11-22): 12 ADRs `Aceito`, [arquitetura](../02-arquitetura/01-arquitetura.md) e [plano de sprints](../02-arquitetura/02-plano-de-sprints.md).
- Decisões A3 (interface e CLI em pt-BR com catálogo de textos; código, API e identificadores em inglês).

## 3. Saídas (artefatos do Gate 3)

| Artefato | Arquivo |
|---|---|
| Definition of Ready | [01-definition-of-ready.md](01-definition-of-ready.md) |
| Definition of Done | [02-definition-of-done.md](02-definition-of-done.md) |
| Critérios da Sprint 0 — esqueleto andante | [sprint-0.md](sprint-0.md) |
| Critérios da Sprint 1 — executor Docker | [sprint-1.md](sprint-1.md) |
| Critérios da Sprint 2 — agendamento, confiabilidade e segredos | [sprint-2.md](sprint-2.md) |
| Critérios da Sprint 3 — construtor de blocos | [sprint-3.md](sprint-3.md) |
| Critérios da Sprint 4 — observabilidade, alertas, plugins, `branch`/`wait` | [sprint-4.md](sprint-4.md) |
| Critérios da Sprint 5 — distribuição, operação e servidor remoto | [sprint-5.md](sprint-5.md) |

## 4. Como ler um critério

Cada critério tem um **ID** (`S0-07`), o **bloco funcional** que cobre, o **enunciado verificável** e a **verificação** (teste automatizado, comando, inspeção ou demonstração). O status de cada critério começa `Pendente` e, no gate da sprint, vira `Aceito`, `Ressalva` (aceito com pendência rastreada) ou `Reprovado`.

| Tipo de verificação | Significado |
|---|---|
| `tests/unit/...` | teste unitário automatizado, roda no `scripts/check` |
| `tests/integration/...` | teste que sobe servidor/executor de verdade; roda no `check` |
| `tests/equivalence/...` | teste de equivalência tags ≡ blocos |
| `tests/e2e/...` | teste de ponta a ponta na interface (Playwright) |
| `tests/docker/...` | teste que exige Docker; pula com motivo quando não há |
| Comando | execução manual de um comando com saída esperada |
| Inspeção | leitura de arquivo, banco ou tela |
| Demo | demonstração executada diante do PO no gate |

## 5. Como funciona o gate de cada sprint

1. Todos os critérios da sprint verificados; o agente preenche a coluna de status com evidência (caminho do teste, saída do comando).
2. Roteiro de demonstração executado diante do PO.
3. DoD cumprida para cada item; retrospectiva curta escrita em `docs/06-refinamento/`.
4. PO aprova, aprova com ressalvas (viram itens da sprint seguinte) ou reprova (sprint continua).
5. `STATUS.md` e `CHANGELOG.md` atualizados.

## 6. Como funciona o Gate 3 (esta etapa)

O PO lê a DoR, a DoD e os seis arquivos de sprint. Pode aprovar em bloco, pedir ajustes pontuais em critérios ou mover critérios entre sprints. Com o Gate 3 aprovado, a **Sprint 0 começa** (Etapa 4), com `git init` como primeiro ato.

## 7. Pendências herdadas

| # | Pendência | Necessária para |
|---|---|---|
| A1 | Docker Desktop instalado e spike B.2 executado | Sprint 1 (pré-condição dura) |
| A2 | Remoto no GitHub | Não bloqueia; CI em nuvem quando houver |
