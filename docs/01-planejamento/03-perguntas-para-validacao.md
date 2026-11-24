# Etapa 1 — Perguntas para validação (Gate 1)

| Campo | Valor |
|---|---|
| Status | `Aprovado` — respostas do Product Owner registradas em 2026-11-22 |
| Versão | 1.0 |
| Data | 2026-11-22 |

Cada pergunta traz contexto, opções, a recomendação do agente e a **decisão do PO**. As decisões foram refletidas nos demais documentos da Etapa 1 e servem de entrada para a Etapa 2 (onde as que são técnicas viram ADR).

---

## Q1 — Topologia: o que é "aplicativo local com conexão nativa a servidor"?

**Opções.** A. só local; B. só cliente de servidor; C. ambos com um código só (servidor roda local por padrão ou remoto; app sempre cliente da API).

**Recomendação:** C.

**Decisão do PO:** **Servidor único local para a primeira etapa do MVP.**
**Leitura aplicada:** o servidor é um componente único, instalado e executado na máquina do usuário no MVP. O app local e a CLI falam com ele **apenas pela API aberta**, sem atalhos, para que a conexão a um servidor remoto (Fase 2) seja uma mudança de endereço, não de arquitetura. → ADR-0002.

---

## Q2 — Linguagem primária do Fluxo A (código com tags)

**Recomendação:** Python primeiro para tags; Shell/SQL via blocos na Fase 2.

**Decisão do PO:** **Python primeiro.** → ADR-0003.

---

## Q3 — Direção de stack

**Recomendação:** Python no servidor, SDK e CLI; interface web.

**Decisão do PO:** **A escolha é do agente, entre Python ou Java, com interface web.**
**Escolha do agente:** **Python** (servidor, SDK, CLI e runner de tarefas) com interface web em React. Justificativa completa e alternativa Java avaliada no ADR-0001.

---

## Q4 — Forma concreta das tags no código

**Recomendação:** decorators no MVP; comentários estruturados na Fase 2.

**Decisão do PO:** **Decorators.** → ADR-0003.
**Refinamento (2026-11-22):** após ver a primeira forma, o PO pediu tags simples (`@step`, `@test`, …) com o resto inferido pelo sistema e, em seguida, decidiu T1–T4 (nome `@pipeline`, inglês, kwargs, só dados ordenam). Registrado no ADR-0003 v0.3.

---

## Q5 — Tipos de ação: taxonomia única para tags e blocos?

**Recomendação:** taxonomia única, fixa no núcleo, extensível por plugin.

**Decisão do PO:** **Seguir a recomendação.** → ADR-0004.

---

## Q6 — Ordem do MVP

**Recomendação:** tags primeiro; construtor de blocos consome a IR pronta; MVP visualiza pipelines como blocos.

**Decisão do PO:** **Seguir a recomendação.** → plano de sprints.

---

## Q7 — Ajustes de processo P1 a P8

**Decisão do PO:** **Seguir a recomendação — todos aceitos.**

| Ajuste | Decisão |
|---|---|
| P1 — Etapas 4–6 em ciclo por sprint | Aceito |
| P2 — Spikes técnicos na Etapa 2 | Aceito |
| P3 — ADRs | Aceito |
| P4 — Sprint 0 esqueleto andante | Aceito |
| P5 — DoR / DoD | Aceito |
| P6 — Direções comerciais que afetam arquitetura na Etapa 2 | Aceito |
| P7 — STATUS.md e CHANGELOG | Aceito |
| P8 — Glossário fixado | Aceito |

---

## Q8 — Nome do projeto

**Decisão do PO:** **Nome fica para o final; o foco é funcionalidade.**
**Consequência técnica:** o código precisa de um identificador para pacote, CLI e namespaces. Será usado o identificador técnico provisório `pipeorc`, escolhido para ser curto e fácil de substituir por busca-e-troca quando o nome for definido. Ele **não** é proposta de nome.

---

## Q9 — Direção de licença e abertura

**Recomendação:** núcleo aberto + extensões/serviços comerciais (open-core), como direção.

**Decisão do PO:** **Seguir a recomendação.** → ADR-0012 (direções comerciais).

---

## Q10 — Sistemas operacionais alvo

**Recomendação:** Windows + Linux na v1; macOS na Fase 2.

**Decisão do PO:** **Seguir a recomendação.**

---

## Registro de respostas

| Data | Pergunta | Decisão do PO | Reflexo nos documentos |
|---|---|---|---|
| 2026-11-22 | Q1 | Servidor único local no MVP | visão R4; blocos B07/B08; ADR-0002 |
| 2026-11-22 | Q2 | Python primeiro | blocos B03; ADR-0003 |
| 2026-11-22 | Q3 | Agente escolhe (Python ou Java) + web → Python | ADR-0001 |
| 2026-11-22 | Q4 | Decorators | glossário "Tag"; ADR-0003 |
| 2026-11-22 | Q5 | Taxonomia única | glossário "Tipo de ação"; ADR-0004 |
| 2026-11-22 | Q6 | Tags primeiro | plano de sprints |
| 2026-11-22 | Q7 | P1–P8 aceitos | metodologia v1.0 |
| 2026-11-22 | Q8 | Nome no final | identificador técnico `pipeorc` |
| 2026-11-22 | Q9 | Open-core como direção | ADR-0012 |
| 2026-11-22 | Q10 | Windows + Linux; macOS Fase 2 | visão R1 |
