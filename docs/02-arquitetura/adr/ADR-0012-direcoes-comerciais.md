# ADR-0012 — Direções comerciais que afetam a arquitetura (P6)

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | PO deu a direção open-core em Q9; demais direções propostas pelo agente |

## Contexto

O planejamento comercial é o projeto seguinte à Entrega final. Mas quatro decisões, se tomadas tarde, obrigam a reescrever partes centrais. Este ADR fixa **direções**, não um plano de negócio.

## Decisões

### 1. Modelo de abertura: open-core (Q9)

- O **núcleo** (IR, SDK, runner, Engine, executores Local e Docker, API, CLI, interface básica e construtor de blocos) é projetado para ser publicável como código aberto.
- Funcionalidades candidatas a comercial ficam **fora do núcleo e atrás da fronteira de plugins**: conectores corporativos, executores remotos/Kubernetes, controle de acesso avançado, alertas avançados, suporte.
- A licença exata do núcleo é escolhida na Entrega final (candidata: Apache-2.0). Até lá o código é privado.

### 2. Fronteira de plugins: entry points Python

| Entry point | O que registra | Núcleo usa em |
|---|---|---|
| `pipeorc.action_types` | tipos de ação (nome, ícone, modelo de código, gancho opcional) | ADR-0004 |
| `pipeorc.executors` | executores adicionais (`Executor` do ADR-0009) | ADR-0009 |
| `pipeorc.connectors` | integrações prontas usadas por blocos/SDK | Sprint 4 |
| `pipeorc.alerts` | canais de notificação (e-mail, webhook, chat) | Sprint 4 |

Regras: o núcleo **nunca** importa um plugin diretamente; plugins declaram versão mínima do núcleo; falha ao carregar um plugin não derruba o servidor (registrada no `doctor`). As interfaces são estabilizadas na Sprint 4 e congeladas na Entrega final.

### 3. Telemetria: nenhuma no MVP

Nenhum dado sai da máquina do usuário. Qualquer coleta futura é **opt-in**, com consentimento explícito na interface, conteúdo documentado e desligável por configuração. A arquitetura reserva apenas um ponto único de emissão (`events` internos) para isso.

### 4. Identidade e multiusuário: um usuário no MVP, dados prontos para vários

- Todo token pertence a um `principal` (usuário ou serviço) e todo recurso tem `project_id`. No MVP existe um `principal` padrão e um projeto padrão.
- Controle de acesso (papéis por projeto) entra com o servidor compartilhado na Fase 2 sem alterar o esquema; SSO fica para depois da v1.

## Consequências

- Positivas: evita reescrita na fase comercial; a fronteira de plugins é boa engenharia de qualquer forma; confiança do usuário (sem telemetria).
- Negativas: alguma disciplina extra (entry points, `project_id` em tudo) desde o MVP.
- Riscos: open-core exige clareza do que é núcleo; este ADR é a referência e é revisado na Entrega final.

## Relacionados

ADR-0004, ADR-0008, ADR-0009; metodologia P6; visão N3.
