# ADR-0010 — Engine e agendador

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente |

## Contexto

O Engine resolve o grafo, despacha tarefas, aplica retries/timeouts/concorrência e mantém estados (B01). O agendador dispara runs por cron (B09), inclusive tratando disparos perdidos com o servidor desligado — situação comum em máquina pessoal.

## Opções consideradas

| Aspecto | Opções | Escolha |
|---|---|---|
| Onde roda | **no processo do servidor (asyncio)**; processo worker separado | no servidor (ADR-0002), com interfaces que permitem separar |
| Agendador | APScheduler; Celery beat; **laço próprio + `croniter`** | laço próprio: controle total de persistência e de disparos perdidos |
| Política de falha | parar tudo; **pular dependentes, continuar ramos independentes** | pular dependentes (padrão), configurável depois |

## Decisão

### Engine

1. **Run manager** assíncrono: fila de runs; limite global de runs simultâneos e de tarefas simultâneas (configuração); limite por pipeline (`max_parallel_runs`, padrão 1, evita sobreposição).
2. **Escalonador de DAG por run**: tarefa fica `QUEUED` quando todas as dependências (`inputs` ∪ `after`) estão `SUCCESS`; é despachada ao executor indicado; ao terminar, libera dependentes.
3. **Máquinas de estado**
   - Run: `PENDING → RUNNING → SUCCESS | FAILED | CANCELLED`.
   - Tentativa de tarefa: `PENDING → QUEUED → RUNNING → SUCCESS | FAILED | CANCELLED`; falha com retries restantes gera `RETRY_WAIT → QUEUED` (nova tentativa, backoff exponencial com teto); dependentes de uma tarefa `FAILED` ficam `SKIPPED`; run termina `FAILED` se qualquer tarefa falhar, `SUCCESS` se todas terminarem bem.
4. **Timeout** por tarefa (IR) e por run (configuração); cancelamento propaga ao executor.
5. **Eventos**: toda transição publica no bus interno → persistência + SSE (ADR-0008).
6. **Recuperação**: ao iniciar, runs `RUNNING` órfãos de uma queda viram `FAILED` com motivo `server_restart` (MVP); retomada de run na Fase 2.

### Agendador

1. Laço assíncrono que, a cada tique (padrão 15 s), busca agendamentos com `next_fire_at <= agora`, cria runs e recalcula `next_fire_at` com **`croniter`** no fuso do agendamento (padrão: fuso do servidor).
2. **Disparos perdidos** (servidor desligado): política por agendamento — `skip` (padrão: ignora e recalcula), `run_once` (um run de recuperação), `run_all` (um run por disparo perdido, com teto).
3. Sem sobreposição por padrão: se o run anterior ainda roda, o novo é `skip` ou enfileirado conforme `max_parallel_runs`.
4. Gatilhos além de cron: manual e API no MVP; webhook e "ao concluir outra pipeline" na Sprint 4.

## Consequências

- Positivas: comportamento previsível e testável sem dependências mágicas; disparos perdidos tratados explicitamente; separação futura em worker sem mudar contratos.
- Negativas: implementar retries/backoff/concorrência à mão; `croniter` cobre cron padrão, não calendários complexos.
- Riscos: laço no mesmo processo da API — tarefas rodam fora (ADR-0009), então o custo é só coordenação.

## Relacionados

ADR-0002, ADR-0006, ADR-0008, ADR-0009; blocos B01, B09, B10.
