# Registro de decisões de arquitetura (ADRs)

Cada decisão relevante fica em um arquivo curto: contexto, opções, decisão, consequências. O PO aprova ADR por ADR (ajuste P3). Status possíveis: `Proposto` → `Aceito` | `Rejeitado`; um ADR aceito só muda por outro ADR que o declare `Superado`.

| ADR | Título | Status | Decisão em uma linha |
|---|---|---|---|
| [0001](ADR-0001-linguagem-e-framework.md) | Linguagem e framework do servidor | `Aceito` | Python 3.12+ com FastAPI; Java avaliado e descartado para este time/escopo |
| [0002](ADR-0002-topologia.md) | Topologia e fronteira da API | `Aceito` | Um processo servidor local no MVP; app e CLI só pela API HTTP; remoto = trocar endereço |
| [0003](ADR-0003-tags-decorators.md) | Forma das tags e descoberta | **`Aceito`** v1.0 | Tags nuas em inglês (`@pipeline`, `@step`, `@test`, …), kwargs para opções; **só dados ordenam**, `@test` como portão e `wait_for=` para ordem sem dados (T1–T4 e C1–C2 decididos pelo PO); descoberta em subprocesso |
| [0004](ADR-0004-taxonomia-tipos-de-acao.md) | Taxonomia única de tipos de ação | `Aceito` v1.0 | 9 tipos = nomes das tags (`step`, `test`, `extract`, …), iguais para tags e blocos, extensíveis por plugin |
| [0005](ADR-0005-formato-da-ir.md) | Formato e versionamento da IR | `Aceito` | JSON canônico com `ir_version`; modelos Pydantic geram o schema; YAML para import/export; versões imutáveis por hash |
| [0006](ADR-0006-persistencia.md) | Persistência | `Aceito` | SQLite (WAL) + SQLAlchemy 2 + Alembic; logs e artefatos em arquivos; Postgres na Fase 2 |
| [0007](ADR-0007-interface-web.md) | Interface web | `Aceito` | React + TypeScript + Vite, React Flow para grafo/blocos, Monaco para código; servida pelo servidor |
| [0008](ADR-0008-protocolo-da-api.md) | Protocolo da API | `Aceito` | REST JSON `/api/v1` + OpenAPI; eventos e logs por SSE; token Bearer |
| [0009](ADR-0009-runner-e-executores.md) | Runner e executores | `Aceito` | Runner único sem dependências (`module`/`inline`); Local por subprocesso; Docker com runner montado em qualquer imagem Python |
| [0010](ADR-0010-engine-e-agendador.md) | Engine e agendador | `Aceito` | Engine assíncrono no processo do servidor; agendador próprio com `croniter` e política de disparos perdidos |
| [0011](ADR-0011-cli-e-distribuicao.md) | CLI e distribuição | `Aceito` | CLI `pipeorc` com Typer; pip/pipx no MVP; instalador Windows e imagem Docker do servidor na Fase 2 |
| [0012](ADR-0012-direcoes-comerciais.md) | Direções comerciais que afetam a arquitetura (P6) | `Aceito` | Open-core; fronteira de plugins por entry points; sem telemetria no MVP; dados prontos para multiusuário |

## Modelo de ADR

```
# ADR-XXXX — Título
Status · Data · Decisores
## Contexto
## Opções consideradas
## Decisão
## Consequências (positivas, negativas, riscos)
## Relacionados
```
