# Metodologia de planejamento e desenvolvimento

| Campo | Valor |
|---|---|
| Status | `Aprovado` — ajustes P1–P8 aceitos pelo Product Owner em 2026-11-22 |
| Versão | 1.0 |
| Data | 2026-11-22 |

## 1. Fluxo original (proposto pelo Product Owner)

1. **Planejamento** — definir funcionalidades e responsabilidades do sistema em blocos gerais, sem detalhes.
2. **Refinamento e planejamento da arquitetura** — detalhar, definir a arquitetura e as etapas de entrega por sprint.
3. **Critérios de aceite** — definir o que cada etapa deve conter e cumprir para liberar a próxima.
4. **Desenvolvimento**
5. **Testes**
6. **Refinamento (ciclo DevOps)**
7. **Entrega final** — com todas as etapas aprovadas, envelopar e seguir para o planejamento de comercialização e aplicação em larga escala (projeto seguinte).

Regra transversal definida pelo Product Owner: **toda proposta ou alteração feita pelo agente é validada antes de ser aplicada**, e o sistema é documentado para validação e acompanhamento.

## 2. Papéis

| Papel | Quem | Responsabilidades |
|---|---|---|
| **Product Owner (PO)** | Dono do projeto | Aprova documentos nos gates; decide entre alternativas; define prioridades; valida entregas. |
| **Agente de análise, arquitetura e desenvolvimento** | Claude | Produz documentos, propostas, código e testes; registra decisões; **nunca avança de etapa nem aplica alteração estrutural sem aprovação do PO**. |

## 3. Ciclo de vida de um documento

```
Rascunho ──► Em validação ──► Aprovado ──► (nova versão) ──► Em validação ...
                 │                               
                 └──► ajustes pedidos ──► Rascunho (vN+1)
```

Um documento `Aprovado` só muda por nova versão. A versão antiga passa a `Superado` e fica no histórico (git, a partir da Sprint 0).

## 4. Gates entre etapas

Um **gate** é o ponto de controle que libera a etapa seguinte. Regras:

- A etapa só é concluída quando **todos** os documentos de saída estão `Aprovado`.
- Cada gate é registrado em [STATUS.md](STATUS.md) com data, decisão e pendências aceitas.
- Pendências podem ser aceitas explicitamente pelo PO ("segue com ressalva X") e viram item rastreado na etapa seguinte.
- Voltar uma etapa é permitido e registrado (ex.: um spike na Etapa 2 invalida uma premissa da Etapa 1).

## 5. Ajustes ao fluxo — ACEITOS em 2026-11-22 (Q7)

Os ajustes abaixo **não alteram as 7 etapas**; eles acrescentam mecanismos para que o fluxo funcione na prática e para que o PO consiga validar com segurança. Todos foram aceitos pelo PO e passam a fazer parte da metodologia.

### P1 — Etapas 4, 5 e 6 viram um ciclo por sprint, não fases globais

- **O que muda:** em vez de "desenvolver tudo, depois testar tudo, depois refinar tudo", cada sprint executa Desenvolvimento → Testes → Refinamento e termina com o seu próprio gate de aceite (definido na Etapa 3).
- **Por quê:** o fluxo original já aponta para isso ("quando todas as etapas tiverem passado pelo critério de aceite"); tornar explícito evita acumular risco até o fim e dá ao PO pontos de validação frequentes.
- **Se não adotar:** validação só no fim; erros de interpretação descobertos tarde custam retrabalho grande.

### P2 — Spikes técnicos (provas de conceito curtas) dentro da Etapa 2

- **O que muda:** antes de fechar a arquitetura, executar 3 provas de conceito descartáveis, com tempo limitado, para as apostas de maior risco: (a) interpretação de tags em código, (b) execução de uma etapa em contêiner Docker com captura de logs, (c) a definição de pipeline unificada que tags e blocos geram.
- **Por quê:** são as três ideias centrais do produto e as de maior incerteza técnica. Decidir arquitetura sem testá-las é decidir no escuro.
- **Se não adotar:** a arquitetura pode ser aprovada sobre premissas que não se sustentam.

### P3 — Registro de decisões de arquitetura (ADRs)

- **O que muda:** cada decisão relevante (linguagem, banco, formato da definição de pipeline, protocolo da API, etc.) vira um arquivo curto em `docs/02-arquitetura/adr/` com contexto, alternativas, decisão e consequências. O PO aprova ADR por ADR.
- **Por quê:** é a forma mais direta de cumprir "sempre valide comigo antes": a decisão fica escrita, comparável e rastreável.
- **Se não adotar:** decisões ficam espalhadas em conversas e se perdem.

### P4 — Sprint 0: "esqueleto andante"

- **O que muda:** a primeira sprint de desenvolvimento entrega uma fatia fina de ponta a ponta (um código com tag → interpretado → executado localmente → visível no app), sem funcionalidades extras.
- **Por quê:** valida a integração entre todos os blocos cedo e cria a base sobre a qual cada sprint acrescenta funcionalidade.
- **Se não adotar:** os blocos são construídos isolados e a integração vira o problema do fim.

### P5 — Definition of Ready (DoR) e Definition of Done (DoD) ao lado dos critérios de aceite

- **O que muda:** a Etapa 3 define, além dos critérios por sprint, duas listas fixas: o que um item precisa ter para **entrar** numa sprint (DoR) e o que precisa ter para ser considerado **pronto** (DoD: testes, documentação, revisão).
- **Por quê:** critérios de aceite dizem "o que" entregar; DoD diz "com que qualidade". Sem DoD, "pronto" vira opinião.

### P6 — Trazer para a Etapa 2 apenas as decisões comerciais que afetam a arquitetura

- **O que muda:** o planejamento comercial continua sendo o projeto seguinte, como definido. Mas quatro decisões influenciam a arquitetura e precisam de **direção** (não plano) já na Etapa 2: modelo de licença (aberto, open-core ou fechado), fronteira de plugins (o que terceiros poderão estender), telemetria/uso (coletar ou não), e multiusuário (um usuário por instalação ou vários).
- **Por quê:** mudar essas quatro depois de construído é caro. Decidir a direção agora custa uma conversa.
- **Se não adotar:** risco de reescrever partes centrais na fase de comercialização.

### P7 — Acompanhamento transversal: STATUS.md e CHANGELOG

- **O que muda:** `STATUS.md` é atualizado a cada gate; `CHANGELOG.md` é criado na Sprint 0 e registra cada entrega.
- **Por quê:** o PO consegue ver o estado do projeto sem reler conversas.

### P8 — Glossário fixado na Etapa 1

- **O que muda:** termos como *Tag*, *Bloco*, *Tipo de ação*, *Pipeline*, *Run*, *Executor*, *Servidor*, *App local* ganham definição única em [glossario.md](glossario.md) e passam a ser usados de forma consistente em todos os documentos e no código.
- **Por quê:** a proposta tem dois conceitos próximos (tags em código e tags de blocos) que precisam de vocabulário preciso para não se confundirem.

## 6. Fluxo resultante (com P1–P8)

```
Etapa 1  Planejamento (visão, escopo, blocos funcionais, glossário)
         └──► GATE 1
Etapa 2  Arquitetura: spikes (P2) ► ADRs (P3) ► desenho ► plano de sprints ► direções comerciais (P6)
         └──► GATE 2
Etapa 3  Critérios de aceite por sprint + DoR/DoD (P5)
         └──► GATE 3
Etapas   ┌─ Sprint 0 — esqueleto andante (P4) ──────────────┐
4–6      │   Desenvolvimento ► Testes ► Refinamento ► GATE   │
(ciclo,  ├─ Sprint 1 ─────────────────────────────────────── ┤
P1)      ├─ Sprint N ─────────────────────────────────────── ┤
         └─────────────────────────────────────────────────── ┘
Etapa 7  Entrega final: empacotamento, docs de uso, checklist
         └──► GATE FINAL ──► Projeto seguinte: planejamento comercial e escala
```

## 7. Artefatos de saída por etapa

| Etapa | Artefatos obrigatórios para o gate |
|---|---|
| 1 | Visão e escopo; blocos funcionais e responsabilidades; glossário; respostas às perguntas de validação |
| 2 | Relatórios dos spikes; ADRs aprovados; documento de arquitetura; plano de sprints; direções comerciais (P6) |
| 3 | Critérios de aceite por sprint; DoR; DoD |
| 4–6 (por sprint) | Código + testes; nota de implementação; relatório de testes; retrospectiva/ajustes; CHANGELOG atualizado |
| 7 | Pacote instalável; documentação de uso; checklist de entrega assinado pelo PO |

## 8. Como a validação acontece na prática

1. O agente entrega o documento como `Rascunho` e lista, no fim da mensagem, **as decisões que precisam do PO**.
2. O PO responde aprovando, recusando ou pedindo ajustes (pode ser item a item).
3. O agente aplica os ajustes, muda o status e registra o gate em `STATUS.md`.
4. Só então a etapa seguinte começa.
