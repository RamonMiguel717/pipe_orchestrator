# Relatório dos spikes técnicos

| Campo | Valor |
|---|---|
| Status | `Aprovado` — Gate 2 em 2026-11-22 (spike B.2 segue pendente de Docker na máquina do PO) |
| Versão | 1.0 |
| Data | 2026-11-22 |
| Código | [spikes/](../../spikes/README.md) (descartável) |
| Ambiente | Windows 10, Python 3.14.4, venv `spikes/.venv` com `docker 7.2.0`, `jsonschema 4.26.0`, `pyyaml 6.0.4`. Docker **não instalado**; WSL2 presente. |

## Spike A — Tags por decorators → descoberta → IR

### O que foi testado

- SDK mínimo: objeto explícito `Pipeline("nome", schedule=...)` e decorator `@p.task("tipo", inputs=, after=, retries=, timeout_s=, executor=, params=)`.
- Código de usuário realista ([example_etl.py](../../spikes/spike_a_tags/example_etl.py)): 5 tarefas com fan-out (extrair → validar, transformar) e fan-in (carregar depende de transformar e validar), uma tarefa em executor Docker, uma com parâmetros.
- Duas estratégias de descoberta: **importar o módulo** e ler o registro vs **ler o código-fonte (AST)** sem executar.
- Seis casos negativos: tipo inválido, input que não é parâmetro, dependência inexistente, ciclo, Docker sem imagem, nome duplicado.

### Resultado

| Item | Resultado |
|---|---|
| Descoberta por importação | 1 pipeline, 5 tarefas, dependências e executores corretos em **1,1 ms** |
| Descoberta por AST | Lista as 5 tarefas em 0,8 ms, mas só enxerga valores literais e não valida nada |
| Casos negativos | 6/6 com mensagem que diz **pipeline, tarefa, o que está errado e o que é aceito** |
| IR gerada | [ir_tags.json](../../spikes/spike_a_tags/ir_tags.json) |

### Conclusões para a arquitetura

1. ~~Decorators com objeto `Pipeline` explícito são suficientes~~ — **superado pelo feedback do PO** (forma pesada demais). Ver spike A2 abaixo.
2. **Descoberta oficial é por importação**, porque só ela valida e resolve valores dinâmicos. Como importar executa código do usuário, o registro deve acontecer em **subprocesso isolado** (nunca dentro do servidor). → ADR-0003.
3. AST serve só para pré-visualização rápida/sem execução e para avisar sobre código solto no corpo da pipeline.
4. Dois tipos de dependência são necessários e naturais: `inputs` (dados, parâmetro → tarefa) e `after` (só ordem). → ADR-0005. Mantido na v0.2: agora ambos são **inferidos**.
5. Referência a segredo em configuração (`${secret:NOME}`) surgiu naturalmente e precisa de convenção formal. → ADR-0009.

## Spike A2 — Tags simples com inferência do grafo (após feedback do PO)

### O que foi testado

Código em [spikes/spike_a2_tags_simples/](../../spikes/spike_a2_tags_simples/). A tag é o nome do decorator (`@step`, `@test`, `@extract`, `@load`, `@notify`), a pipeline é uma função `@pipeline` que chama os passos como funções normais, e o sistema infere o grafo executando essa função em **modo de construção** (passos não executam; devolvem referências opacas).

Duas rodadas: **v0.2** (ordem sequencial por padrão + `with parallel()`) e, após as respostas T1–T4 do PO, **v0.3** (só dados ordenam; `@test` como portão; `wait_for=` para ordem sem dados). O resultado abaixo é da v0.3.

- Exemplo realista com dois extratores independentes, teste, passo em Docker, literais como parâmetros e notificação final com `wait_for=` ([example_etl.py](../../spikes/spike_a2_tags_simples/example_etl.py)).
- Oito casos negativos: `if` sobre resultado, `len()` sobre resultado, opção desconhecida, argumento não serializável, pipeline sem passos, chamada com argumentos errados, `wait_for` inválido, função com parâmetro reservado.
- Casos de borda: passo chamado duas vezes, literal vira `params`, passos sem dados ficam paralelos, passo solto é independente, passos antes do teste não esperam por ele, testes encadeiam, redução transitiva, `wait_for` cria ordem, modo de desenvolvimento executando de verdade.
- IR validada contra o schema do spike C (atualizado para `step`/`test`).

### Resultado

| Item | Resultado |
|---|---|
| Grafo inferido | 6 passos em 1,7 ms; `extrair_vendas` ∥ `extrair_clientes`; `validar ← vendas`; `transformar ← vendas, clientes` e espera `validar` (portão); `carregar ← resumo`; `notificar` espera `carregar` por `wait_for` |
| Só dados ordenam | passos sem ligação de dados ficam sem `after` (paralelos) |
| Portão de teste | passos após `validar` recebem `after: [validar]`; os anteriores não; dois testes encadeiam e a redução transitiva deixa só o último |
| `wait_for=` | cria ordem sem dados; nome reservado protegido com erro |
| Literais | `tabela="vendas_resumo_diario"` virou `params` do passo |
| Casos negativos | 8/8 com mensagem orientando a correção |
| Casos de borda | 11/11 |
| Modo de desenvolvimento | `python example_etl.py` executou a pipeline em processo |
| Schema | IR válida |

### Conclusões para a arquitetura

1. Tags nuas + inferência atendem ao pedido do PO sem perder nada na IR: o grafo que o sistema enxerga é o mesmo da v0.1. → ADR-0003.
2. Com **só dados ordenam** (T4), o grafo é literalmente o fluxo de dados e o paralelismo é máximo por padrão. As duas consequências necessárias são `@test` como portão (senão um teste não protege nada) e `wait_for=` como válvula de escape para ordem sem dados. → ADR-0003 v0.3, pontos C1/C2.
3. Referências opacas com erros claros resolvem o principal risco da inferência (lógica condicional no corpo); `@branch` cobre o caso na Sprint 4.
4. A taxonomia vira a lista de tags: `script`→`step`, `validate`→`test`. → ADR-0004 v0.2.
5. Um passo "solto" (sem dados e sem `wait_for`) roda no início: o registro deve avisar e a interface deve deixar isso visível.

## Spike C — IR unificada (tags ≡ blocos)

### O que foi testado

- JSON Schema (draft 2020-12) para a IR v0.1: [ir_schema.json](../../spikes/spike_c_ir/ir_schema.json).
- Simulação do construtor de blocos ([builder.py](../../spikes/spike_c_ir/builder.py)) montando a **mesma** pipeline do spike A por blocos com código inline.
- Validação das duas IRs; comparação semântica; ida e volta em YAML; detecção de IR propositalmente quebrada.

### Resultado

| Item | Resultado |
|---|---|
| IR via tags contra o schema | válida |
| IR via blocos contra o schema | válida |
| Equivalência semântica (grafo, tipos, dependências, executores, retries, params) | **idênticas** |
| Diferença entre os caminhos | só `code.kind` (`module` nas tags, `inline` nos blocos) e `source.kind` |
| YAML ida e volta | sem perda (96 linhas) |
| IR quebrada (tipo inexistente, Docker sem imagem) | 2 erros detectados pelo schema |

### Conclusões para a arquitetura

1. O diferencial D2 é **tecnicamente garantido** por construção: ambos os caminhos produzem o mesmo modelo; a única variação é como o código é referenciado.
2. Logo, o **runner** precisa suportar dois tipos de código: `module` (importar e chamar) e `inline` (executar fonte e chamar o entrypoint). → ADR-0009.
3. JSON é o formato canônico (armazenamento e API); YAML é formato de **import/export** para humanos. → ADR-0005.
4. O schema será **gerado a partir dos modelos Pydantic** no produto, para não manter duas fontes de verdade. → ADR-0005.
5. Testes de equivalência tags ↔ blocos entram no conjunto de testes desde a Sprint 0.

## Spike B — Execução em Docker com logs

### O que foi testado

- **B.1 Diagnóstico** ([diagnose.py](../../spikes/spike_b_docker/diagnose.py)): detectar CLI no PATH, pipe/socket do engine, WSL2, Docker Desktop instalado, ping via SDK; classificar em `ready / not_running / not_installed / unknown`; gerar mensagem em pt-BR.
- **B.2 Execução** ([run_task_in_docker.py](../../spikes/spike_b_docker/run_task_in_docker.py)): rodar uma tarefa em `python:3.12-slim` com diretório de trabalho montado em `/work`, `inputs.json` de entrada, `outputs.json` de saída, variável de ambiente, limite de memória, logs em tempo real com timestamp, código de saída e remoção do contêiner; medir tempo até o primeiro log e total.

### Resultado

| Item | Resultado |
|---|---|
| B.1 nesta máquina | `not_installed`. Mensagem: "Docker não está instalado nesta máquina. O executor Docker ficará indisponível até instalar o Docker Desktop. O WSL2 está presente, que é o pré-requisito do Docker Desktop." |
| B.2 nesta máquina | **Bloqueado** (sai com código 3 e a mesma mensagem). Script pronto para rodar assim que o Docker existir. |

### Conclusões para a arquitetura

1. O caminho "Docker ausente" **já está resolvido** e vira o comando `pipeorc doctor` e o aviso na interface (B06/B14).
2. O protocolo do runner (diretório montado + arquivos JSON + stdout como log + código de saída) é o mesmo para Local e Docker, o que mantém o Engine indiferente ao executor. → ADR-0009.
3. **Risco K3 (Docker no Windows) continua aberto** até o B.2 rodar na máquina do PO. Vira pré-condição da Sprint 1 (pendência A1 do plano da etapa).

## Impacto consolidado nas decisões

| Decisão | Sustentada por |
|---|---|
| Tags nuas (`@pipeline`, `@step`, `@test`, …) com grafo inferido; registro em subprocesso | Spikes A2 + A |
| IR em JSON canônico, YAML para import/export, schema gerado dos modelos | Spike C |
| Runner único com `code.kind` ∈ {module, inline} | Spikes A + C |
| Diagnóstico de ambiente como funcionalidade de produto | Spike B.1 |
| Sprint 1 (Docker) depende de Docker instalado; K3 segue aberto | Spike B.2 |
