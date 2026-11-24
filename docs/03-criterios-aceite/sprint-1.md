# Critérios de aceite — Sprint 1: executor Docker

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | M |
| Blocos | B05, B06, B14 (doctor), B01 |

## Objetivo

Qualquer passo com `docker="imagem"` roda em contêiner com logs em tempo real; sem Docker, o sistema explica o que falta.

## Pré-condições (DoR da sprint) — **duras**

- Sprint 0 aprovada.
- **A1:** Docker Desktop instalado na máquina de referência; `pipeorc doctor` reporta `ready`; `spikes/spike_b_docker/run_task_in_docker.py` executado com sucesso e resultado (tempos) registrado no relatório dos spikes. Fecha o risco K3.

## Critérios

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S1-01 | B06 | Pré-condição A1 cumprida e registrada | Inspeção do relatório de spikes | Pendente |
| S1-02 | B06 | Passo com `executor.kind = docker` roda em contêiner da imagem indicada com: diretório da tentativa em `/work` (rw), pacote `pipeorc.runner` em `/opt/pipeorc` (ro) com `PYTHONPATH`, projeto do usuário em `/work/project` (ro) quando `code.kind = module`; `outputs.json` lido ao fim | `tests/docker/test_docker_executor.py` | Pendente |
| S1-03 | B06 | O runner funciona em imagem Python **sem nada do produto instalado** (`python:3.12-slim`), provando o "runner montado" | `tests/docker/test_plain_image.py` | Pendente |
| S1-04 | B06 | Imagem ausente: `pull` automático com progresso publicado como eventos (SSE) e visível no `run --watch` e na interface | `tests/docker/test_pull.py` + Demo | Pendente |
| S1-05 | B06 | Logs do contêiner em streaming: primeira linha disponível antes do fim do passo; timestamps preservados | `tests/docker/test_logs_stream.py` | Pendente |
| S1-06 | B06 | `env` da IR chega ao contêiner; variáveis do sistema do servidor **não** vazam para o contêiner | `tests/docker/test_env.py` | Pendente |
| S1-07 | B06 | Timeout do passo mata o contêiner e marca `FAILED` com motivo `timeout`; contêiner removido ao fim em qualquer resultado; opção de configuração para manter contêiner em falha (para depuração) | `tests/docker/test_timeout_cleanup.py` | Pendente |
| S1-08 | B06 | Limites de CPU e memória da configuração aplicados ao contêiner (verificar por `inspect`) | `tests/docker/test_limits.py` | Pendente |
| S1-09 | B06 | Rótulos `pipeorc.run` e `pipeorc.task` nos contêineres; `pipeorc doctor` lista contêineres órfãos do produto e oferece limpeza | `tests/docker/test_labels.py` + Comando | Pendente |
| S1-10 | B01 | Tipo `container`: passo sem código Python roda `params.command` na imagem; código de saída → estado | `tests/docker/test_container_type.py` | Pendente |
| S1-11 | B01 | Executor indisponível (Docker ausente/parado): run falha **antes** de iniciar, com a mensagem do `doctor`; passos Local do mesmo run não são iniciados | `tests/integration/test_executor_unavailable.py` | Pendente |
| S1-12 | B08 | `/api/v1/info` expõe o estado dos executores; interface mostra no cabeçalho um indicador (Docker pronto / indisponível com motivo); `doctor` idem | `tests/integration/test_info.py` + Demo | Pendente |
| S1-13 | B06 | Caminhos Windows ↔ contêiner: projeto em pasta com espaços e acentos funciona; caminho absoluto Windows traduzido corretamente | `tests/docker/test_paths_windows.py` (roda em Windows) | Pendente |
| S1-14 | — | Testes `docker` pulam com motivo claro quando Docker está ausente e o `check` continua verde; na máquina de referência eles rodam | Comando (`check` com e sem Docker) | Pendente |
| S1-15 | B05 | Teste de contrato do `Executor` (Protocol): Local e Docker passam no mesmo conjunto de testes de comportamento (run, cancel, health, logs) | `tests/integration/test_executor_contract.py` | Pendente |

## Fora do escopo

Build de imagem a partir de Dockerfile do projeto (Fase 2), `compose` como unidade (Futuro), segredos em `env` (Sprint 2: aqui só variáveis literais).

## Roteiro de demonstração do gate (G1)

1. `pipeorc doctor` com Docker `ready`.
2. Rodar `etl_vendas`: o passo `carregar` em `python:3.12-slim`, com pull ao vivo na primeira vez, logs em tempo real na interface e no `--watch`.
3. Mostrar `docker ps` durante a execução (rótulos) e após (contêiner removido).
4. Parar o Docker Desktop; disparar o run; ver a falha antes de iniciar, com a mensagem; indicador na interface.
5. Um passo do tipo `container` rodando um comando simples em `alpine`.
6. `scripts/check` com os testes `docker` executando.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
