# ADR-0009 — Runner e executores

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente, sustentado pelos spikes A, B e C |

## Contexto

O Engine precisa rodar o código de uma tarefa (a) fora do processo do servidor, (b) tanto para código em módulo (tags) quanto inline (blocos), (c) em processo local ou em contêiner Docker, (d) com entradas, saídas, segredos, logs em tempo real, timeout e código de saída. O spike C mostrou que a única diferença entre os fluxos é `code.kind`; o spike B desenhou o protocolo por diretório montado.

## Decisão

### Protocolo do runner (igual para todos os executores)

Para cada tentativa de tarefa o Engine prepara um diretório de trabalho:

```
<dados>/runs/<run_id>/<task_id>/attempt-<n>/
  task.json      # tarefa da IR + parâmetros resolvidos + caminhos
  inputs.json    # {parâmetro: saída da tarefa a montante}
  outputs.json   # escrito pelo runner ao fim (valor JSON ou referência a artefato)
  artifacts/     # arquivos produzidos pela tarefa
  log.txt        # stdout+stderr capturados pelo executor
```

O **runner** (`python -m pipeorc.runner <diretório>`) é um módulo Python **sem dependências de terceiros**: lê `task.json`, carrega o código (`module`: importa `path` e chama `callable`; `inline`: executa `source` e chama `entrypoint`), injeta `inputs` como argumentos nomeados, grava o retorno em `outputs.json` (JSON; objetos não serializáveis viram artefato pickle com referência), imprime logs em stdout e sai com código 0 em sucesso, 1 em exceção (traceback no log), 2 em erro de protocolo.

### Executor Local

Subprocesso `python -m pipeorc.runner` usando o **interpretador configurado** para o projeto (padrão: o do servidor; configurável para um venv do usuário, para que as dependências do código dele estejam disponíveis). Variáveis de ambiente da tarefa + segredos resolvidos. Timeout mata a árvore de processos. Logs lidos por pipe linha a linha e repassados ao bus de eventos.

### Executor Docker

Contêiner a partir de `executor.image` com:

- o diretório da tentativa montado em `/work` (rw);
- o diretório do projeto do usuário (quando `code.kind = module`) montado em `/work/project` (ro no MVP);
- **o pacote `pipeorc.runner` montado em `/opt/pipeorc` (ro) e `PYTHONPATH=/opt/pipeorc`** — assim **qualquer imagem com Python** funciona sem instalar nada do produto (o runner não tem dependências);
- comando `python -m pipeorc.runner /work`; `env` da IR + segredos; limites de CPU/memória da configuração; rótulos `pipeorc.run`, `pipeorc.task` para limpeza;
- logs via API do Docker em streaming; `wait` para código de saída; remoção ao fim (configurável manter em falha para depuração).
- Imagem ausente: `pull` com progresso publicado como evento. Tipo `container` (ADR-0004): sem runner, roda o comando de `params.command` direto.

### Segredos

`${secret:NOME}` em `executor.env` e `params` é resolvido pelo Engine no despacho, a partir do cofre (ADR-0006/B12), e entregue **apenas por variável de ambiente** ao processo/contêiner. Valores conhecidos são mascarados nos logs (melhor esforço).

### Interface interna

```python
class Executor(Protocol):
    kind: str
    async def run(self, attempt: AttemptContext, on_log: Callable[[str], Awaitable[None]]) -> AttemptResult
    async def cancel(self, attempt_id: str) -> None
    async def health(self) -> ExecutorHealth   # usado pelo `doctor` e pela interface
```

Executores adicionais (remoto, Kubernetes) entram por entry point `pipeorc.executors` (ADR-0012).

## Consequências

- Positivas: o Engine é indiferente ao executor; nenhuma imagem especial é necessária; falhas de tarefa nunca derrubam o servidor; o mesmo protocolo serve a testes.
- Negativas: troca de dados por arquivos JSON limita o tamanho das saídas diretas (artefatos cobrem o resto); montar o projeto do usuário em Docker exige caminhos compatíveis no Windows (Docker Desktop resolve; verificar no spike B.2).
- Riscos: K3 (Docker no Windows) só fecha quando o B.2 rodar; imagens sem Python exigem o tipo `container`.

## Relacionados

ADR-0002, ADR-0004, ADR-0005, ADR-0006, ADR-0010; spikes A/B/C; blocos B05, B06, B12.
