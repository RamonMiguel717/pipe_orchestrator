# Spikes técnicos (Etapa 2 — ajuste P2)

Código **descartável**, com tempo limitado, para reduzir incerteza antes das decisões de arquitetura. Nada aqui vira código de produto; as conclusões vão para `docs/02-arquitetura/relatorio-spikes.md` e para os ADRs.

| Spike | Pergunta que responde | Pasta |
|---|---|---|
| A | Decorators Python conseguem descrever tarefas, tipos, dependências e executor, e ser descobertos e traduzidos para a IR com erros claros? (forma explícita, **superada** pelo A2) | `spike_a_tags/` |
| A2 | Tags nuas (`@step`, `@test`, `@pipeline`) com o grafo **inferido** (só dados ordenam; `@test` como portão; `wait_for=`) são simples para o usuário e completas para o sistema? | `spike_a2_tags_simples/` |
| B | Conseguimos rodar uma tarefa em contêiner Docker com volume, variáveis, logs em tempo real e código de saída, a partir de Python? E o que o usuário vê quando o Docker não existe? | `spike_b_docker/` |
| C | Uma IR única, validável por esquema, é produzida de forma idêntica pelo caminho das tags e pelo caminho dos blocos? | `spike_c_ir/` |

## Como rodar

Ambiente: `spikes/.venv` (Python 3.14, pacotes `docker`, `jsonschema`, `pyyaml`).

```powershell
spikes\.venv\Scripts\python spikes\spike_a_tags\discover.py spikes\spike_a_tags\example_etl.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_a_tags\tests_spike_a.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_a2_tags_simples\discover.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_a2_tags_simples\tests_spike_a2.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_c_ir\compare.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_b_docker\diagnose.py
```

```powershell
spikes\.venv\Scripts\python spikes\spike_b_docker\run_task_in_docker.py
```
