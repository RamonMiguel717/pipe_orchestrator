# ADR-0011 — CLI e distribuição

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente |

## Contexto

O produto é instalado na máquina do usuário (Windows e Linux). Precisa de CLI para registrar código, operar o servidor e consultar runs (B08), e de um caminho de instalação e atualização (B14). Risco K5 (empacotamento Windows) aberto.

## Decisão

### CLI (`pipeorc`, com Typer)

| Comando | Função |
|---|---|
| `pipeorc init` | Cria diretório de dados, config e token |
| `pipeorc server start [--foreground]` / `stop` / `status` | Opera o servidor local |
| `pipeorc doctor` | Diagnostica Python, Docker (spike B.1), diretório de dados, porta |
| `pipeorc register <arquivo\|pasta>` | Descobre tags em subprocesso e registra no servidor |
| `pipeorc pipelines` / `pipeorc show <pipeline>` | Lista e detalha (versões, tarefas) |
| `pipeorc run <pipeline> [--param k=v] [--watch]` | Dispara e, com `--watch`, acompanha com logs |
| `pipeorc runs [--pipeline] [--state]` / `pipeorc logs <run> [tarefa] [--follow]` | Histórico e logs |
| `pipeorc schedules ...` / `pipeorc secrets set\|list\|rm` / `pipeorc token create\|revoke` | Sprint 2 |
| `pipeorc import <arquivo.yaml>` / `export <pipeline>` / `ir schema` | IR |
| `pipeorc ui` | Abre a interface no navegador |
| `pipeorc backup` / `restore` / `runs prune` | Sprint 5 |

Saída legível por padrão; `--json` em todos os comandos de consulta. A CLI usa **somente a API** (ADR-0002), exceto `init`, `server start/stop` e `doctor`, que operam a máquina local.

### Empacotamento

| Fase | Forma | Observação |
|---|---|---|
| MVP (Sprint 0) | **`pip install pipeorc` / `pipx install pipeorc`** a partir de um índice privado ou do repositório | Testado em Windows limpo na Sprint 0 (K5) |
| Fase 2 (Sprint 5) | **Instalador Windows** (PyInstaller + Inno Setup) com Python embutido, atalho e serviço opcional; **Linux** via pipx e pacote `.deb` | Atualização com migração automática (ADR-0006) |
| Fase 2 (Sprint 5) | **Imagem Docker do servidor** | Base para servidor remoto |

Uma única distribuição Python `pipeorc` contém `ir`, `sdk`, `runner`, `server`, `cli` e a interface compilada. Os subpacotes `runner` (zero dependências) e `sdk` (dependências leves) são mantidos separáveis para publicar `pipeorc-sdk` na Fase 2, quando houver servidor remoto.

Servidor em segundo plano: no MVP `server start` roda em primeiro plano ou destacado (`--detach`, com arquivo PID); registro como serviço (Windows: tarefa de inicialização/serviço; Linux: unidade systemd) na Sprint 5.

## Consequências

- Positivas: CLI utilizável desde a Sprint 0; distribuição simples para desenvolvedores; caminho claro para usuário final.
- Negativas: pipx exige Python prévio na máquina (aceitável no MVP, resolvido pelo instalador na Sprint 5).
- Riscos: antivírus/SmartScreen em executáveis PyInstaller sem assinatura — assinatura de código avaliada na Entrega final.

## Relacionados

ADR-0001, ADR-0002, ADR-0006, ADR-0007; blocos B08, B14; risco K5.
