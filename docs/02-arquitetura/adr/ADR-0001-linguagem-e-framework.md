# ADR-0001 — Linguagem e framework do servidor

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | PO delegou a escolha ao agente (Q3: Python ou Java, com interface web) |

## Contexto

O servidor concentra Engine, agendador, executores, persistência e API (B01, B05–B07, B09–B12). O SDK de tags é Python (Q2). A interface é web (Q3). O produto é local-first em Windows e Linux (Q10), com distribuição para máquina de usuário final (B14). O time de desenvolvimento é pequeno e a iteração rápida com validação frequente do PO (P1) é prioridade.

## Opções consideradas

| Opção | Prós | Contras |
|---|---|---|
| **A. Python 3.12+ (FastAPI + Uvicorn, Pydantic v2, SQLAlchemy 2)** | Uma linguagem para servidor, SDK, runner e CLI; FastAPI gera OpenAPI nativamente (B07); SDK Docker para Python maduro; asyncio adequado a streaming de logs; mesmo ecossistema do público-alvo (dados) | Distribuição em Windows exige empacotar o interpretador (PyInstaller) ou pipx; desempenho bruto menor (irrelevante aqui: o trabalho pesado roda nas tarefas, não no servidor) |
| **B. Java 17+ (Spring Boot)** | Um `.jar` único facilita distribuição; ecossistema robusto para serviços de longa duração; forte em agendamento (Quartz) | Divide o produto em duas linguagens (SDK Python + servidor Java), duplicando modelos da IR e validações; iteração mais lenta; JVM pesada para um app local; SDK Docker para Java menos ergonômico; a equipe e o público são Python |
| C. Go/Rust | Binário único, leve | Fora das opções dadas pelo PO; três linguagens no total |

## Decisão

**Python 3.12 ou superior** no servidor, SDK, runner e CLI, com:

- **FastAPI + Uvicorn** para a API e a entrega da interface estática.
- **Pydantic v2** como fonte de verdade dos modelos da IR e dos contratos da API (gera o JSON Schema e o OpenAPI).
- **SQLAlchemy 2 + Alembic** para persistência e migrações (ADR-0006).
- Desenvolvimento e testes na versão instalada na máquina do PO (3.14) e na mínima suportada (3.12).

A interface web é tratada no ADR-0007.

## Consequências

- Positivas: um único repositório e uma linguagem; a IR é definida uma vez (Pydantic) e usada por SDK, servidor e validação; OpenAPI de graça; desenvolvimento rápido.
- Negativas: empacotamento para usuário final em Windows é um trabalho explícito (ADR-0011, Sprint 5); o risco K5 permanece e é testado cedo (pipx na Sprint 0).
- Riscos: bibliotecas sem roda binária para Python 3.14 — mitigação: suportar 3.12 como mínimo e fixar versões.

## Relacionados

ADR-0006, ADR-0007, ADR-0011; visão R6; risco K5.
