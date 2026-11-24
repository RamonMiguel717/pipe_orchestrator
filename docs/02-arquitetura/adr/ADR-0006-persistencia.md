# ADR-0006 — Persistência

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente |

## Contexto

Local-first exige zero configuração de banco. Servidor compartilhado (Fase 2) pede banco externo. Logs de tarefas podem ser volumosos. Artefatos são arquivos.

## Opções consideradas

| Aspecto | Opções | Escolha |
|---|---|---|
| Banco local | **SQLite**; arquivo JSON; DuckDB | SQLite em modo WAL |
| Acesso | **SQLAlchemy 2 + Alembic**; SQL direto; ORM leve (SQLModel) | SQLAlchemy 2 (caminho conhecido para Postgres) |
| Logs | linhas no banco; **arquivos por tentativa + índice no banco** | arquivos |
| Artefatos | blobs no banco; **sistema de arquivos com referência no banco** | arquivos |

## Decisão

1. **SQLite** (WAL, `busy_timeout`) como padrão, arquivo em `<dados>/pipeorc.db`. **Postgres** como opção na Fase 2; por isso só recursos SQL suportados pelos dois.
2. **SQLAlchemy 2** (estilo declarativo, sessões assíncronas onde fizer sentido) e **Alembic** para migrações desde a primeira versão. `pipeorc server start` aplica migrações pendentes automaticamente, com backup prévio do arquivo SQLite.
3. **Logs** de cada tentativa de tarefa em arquivo texto append-only `<dados>/runs/<run>/<tarefa>/attempt-<n>/log.txt`; o banco guarda caminho, tamanho e contadores. Streaming lê o arquivo (tail) e serve por SSE.
4. **Artefatos** em `<dados>/runs/<run>/<tarefa>/attempt-<n>/artifacts/`; `outputs.json` guarda valores pequenos e referências a artefatos.
5. **Retenção** configurável (dias e/ou número de runs) com `pipeorc runs prune`, apagando arquivos e linhas.
6. **Diretório de dados** por sistema: Windows `%LOCALAPPDATA%\pipeorc\`; Linux `$XDG_DATA_HOME/pipeorc` (padrão `~/.local/share/pipeorc`). Sobrescrevível por `PIPEORC_HOME`.
7. `pipeorc backup` compacta banco + diretórios; `pipeorc restore` o inverso (Sprint 5).

## Consequências

- Positivas: instala e funciona sem configurar nada; logs grandes não incham o banco; migração para Postgres sem reescrever repositórios.
- Negativas: SQLite limita concorrência de escrita — adequado a um servidor local; servidor compartilhado usa Postgres.
- Riscos: OneDrive/sincronizadores em cima do diretório de dados corrompem SQLite — o diretório padrão fica **fora** de pastas sincronizadas e o `doctor` avisa se detectar.

## Relacionados

ADR-0001, ADR-0010; bloco B11.
