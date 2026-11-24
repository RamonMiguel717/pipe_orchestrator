# Critérios de aceite — Sprint 5: distribuição, operação e preparação para servidor remoto

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | G |
| Blocos | B14, B11, B08, B07, B12 |

## Objetivo

Um usuário final instala em máquina limpa, o servidor sobe com o sistema, atualizações preservam dados, e o mesmo servidor roda em Linux via Docker para ser apontado pelo app. Última sprint antes da Entrega final.

## Pré-condições (DoR da sprint)

- Sprint 4 aprovada.
- Máquina virtual Windows limpa e Linux limpo disponíveis para os testes de instalação.
- Decisão do PO sobre manter ou adiar o item "servidor remoto" (S5-08 a S5-10); por padrão, mantido.

## Critérios

### Instalação e atualização (B14)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S5-01 | B14 | Instalador Windows (PyInstaller + Inno Setup) instala em máquina limpa **sem Python prévio**: `pipeorc` no PATH, atalho para a interface, opção de iniciar o servidor com o sistema; desinstalação remove o programa e pergunta sobre os dados | Demo em VM + lista de verificação | Pendente |
| S5-02 | B14 | Linux: instalação por `pipx` documentada e pacote `.deb` com unidade `systemd`; `systemctl status pipeorc` ativo após instalar | Demo em VM/contêiner Linux | Pendente |
| S5-03 | B14 | Atualização de versão N para N+1 preserva pipelines, runs, segredos e agendamentos; migrações aplicadas automaticamente com backup prévio do banco; procedimento de retorno à versão anterior documentado e testado | `tests/integration/test_upgrade.py` + Demo | Pendente |
| S5-04 | B14 | Tamanho do instalador e tempo de instalação registrados; executável sem alertas bloqueantes do SmartScreen **ou** plano de assinatura de código registrado para a Entrega final | Inspeção | Pendente |

### Operação (B11, B14)

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S5-05 | B11 | `pipeorc backup` gera um arquivo com banco, diretórios de runs, configuração e chave do cofre; `pipeorc restore` recompõe tudo em instalação limpa e os runs/segredos ficam acessíveis | `tests/integration/test_backup_restore.py` | Pendente |
| S5-06 | B14 | Logs do próprio servidor em `server.log` com rotação por tamanho; nível configurável; `doctor` completo (Python, dados, porta, Docker, plugins, espaço em disco, versão e atualização disponível quando houver índice) | Comando + Inspeção | Pendente |
| S5-07 | B14 | Servidor em segundo plano: `server start --detach` com arquivo PID e `server stop` confiáveis em Windows e Linux | `tests/integration/test_daemon.py` | Pendente |

### Servidor remoto e banco externo (B07, B08, B12) — mantido salvo decisão do PO

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S5-08 | B07 | Imagem Docker do servidor publicada localmente (`Dockerfile` no repositório); sobe em Linux com volume de dados; `compose` de exemplo com Postgres | Demo | Pendente |
| S5-09 | B11 | Postgres como banco opcional via configuração; o conjunto de testes de integração roda contra Postgres além de SQLite | `tests/integration` com marcador `postgres` | Pendente |
| S5-10 | B08 | `pipeorc config set server.url <url>` e token: CLI e interface passam a operar contra o servidor remoto sem outra mudança; escuta em rede exige flag explícita e exibe aviso; guia de TLS/proxy reverso documentado | `tests/integration/test_remote_client.py` + Demo | Pendente |

### Documentação e endurecimento

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S5-11 | — | Documentação de uso completa em pt-BR: instalação (Windows, Linux), primeiro uso, tags (com os exemplos do ADR-0003), construtor, Docker, agendamento, segredos, API (com exemplos `curl`), plugins, operação (backup, atualização); revisada pelo PO | Inspeção pelo PO | Pendente |
| S5-12 | B12 | Varredura de dependências sem vulnerabilidades críticas ou altas sem justificativa; lista de verificação de segurança (arquitetura §8) marcada item a item | Relatório no `check` + Inspeção | Pendente |
| S5-13 | B01 | Carga leve: 50 runs concorrentes de uma pipeline trivial com limite de concorrência configurado terminam sem erro e sem vazamento de processos/contêineres; tempos registrados | `tests/integration/test_load_light.py` | Pendente |
| S5-14 | — | Contratos congelados para a Entrega final: API v1, IR v0.1 → v1.0 (sem mudanças incompatíveis) e Protocols de plugin; registrado em ADR de congelamento | ADR novo `Aceito` | Pendente |

## Fora do escopo

macOS, SSO, telemetria, marketplace, execução distribuída em várias máquinas.

## Roteiro de demonstração do gate (G5)

1. Instalar em VM Windows limpa pelo instalador; abrir a interface pelo atalho; registrar e rodar `etl_vendas`.
2. Instalar a versão seguinte por cima; mostrar dados preservados e backup gerado.
3. `backup` → instalação limpa → `restore` → histórico presente.
4. Subir a imagem Docker do servidor em Linux com Postgres; apontar a CLI do Windows para ela; registrar e rodar.
5. Mostrar a documentação de uso navegável.
6. `scripts/check` completo com varredura de dependências.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
