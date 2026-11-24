# Definition of Done (DoD)

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |

A DoD diz **com que qualidade** algo é entregue. Critérios de aceite dizem *o que*; a DoD diz *como*. Vale para todo item de toda sprint.

## 1. Um item está pronto quando

| # | Condição | Evidência |
|---|---|---|
| D1 | Código implementado cobre o critério de aceite e **testes automatizados** o verificam (unitário e, quando envolve servidor/executor, de integração) | caminho do teste no critério |
| D2 | `scripts/check` termina com código 0: formatação e lint (ruff), tipos (mypy no pacote Python; tsc na interface), testes (pytest; vitest/Playwright na interface), build da interface | saída do comando |
| D3 | Cobertura de testes não cai abaixo do piso: **80 %** nos pacotes `ir`, `sdk`, `runner` e `server/engine`; **60 %** no restante do pacote Python. Pisos ajustáveis pelo PO | relatório de cobertura no `check` |
| D4 | Documentação atualizada no mesmo commit: arquitetura ou ADR se um contrato mudou; documentação de uso se o comportamento visível mudou; `CHANGELOG.md` sempre | diff |
| D5 | Textos para o usuário (CLI, interface, erros da API) estão no catálogo em **pt-BR**; identificadores, nomes de rotas, campos da IR e código em **inglês** (A3) | revisão |
| D6 | Nenhum segredo, token ou dado pessoal em código, testes, fixtures, logs ou documentação | varredura no `check` (padrões de segredo) |
| D7 | Mensagens de erro voltadas ao usuário dizem **o que** falhou, **onde** e **como corrigir** (padrão dos spikes A/A2) | revisão dos casos negativos |
| D8 | Revisão de código feita com a lista de verificação da seção 3 e registrada na nota de implementação da sprint | `docs/04-desenvolvimento/sprint-N.md` |
| D9 | Demonstração executada diante do PO e critério marcado `Aceito` (ou `Ressalva` com item rastreado) | arquivo da sprint |

## 2. Uma sprint está pronta quando

| # | Condição |
|---|---|
| F1 | Todos os critérios da sprint estão `Aceito` ou `Ressalva` com item criado na sprint seguinte |
| F2 | Todos os itens cumprem D1–D9 |
| F3 | Roteiro de demonstração do gate executado por completo |
| F4 | Nota de implementação (`docs/04-desenvolvimento/sprint-N.md`), relatório de testes (`docs/05-testes/sprint-N.md`) e retrospectiva (`docs/06-refinamento/sprint-N.md`) escritos |
| F5 | `CHANGELOG.md` tem a seção da sprint; `STATUS.md` registra o gate |
| F6 | Nenhum teste marcado como "pular" sem motivo registrado; testes `docker` pulam apenas quando o Docker está ausente, e isso aparece na saída |
| F7 | O código está commitado no git local (e enviado ao remoto, quando houver), com mensagens que citam o ID do critério |

## 3. Lista de verificação da revisão de código (D8)

- A fronteira da API foi respeitada: nenhum cliente (CLI, interface) importa código do servidor nem toca no banco (A2 da arquitetura).
- Nenhum código do usuário executa no processo do servidor (A3 da arquitetura).
- Toda nova rota tem autenticação, formato de erro único e aparece na OpenAPI.
- Toda nova entidade tem migração Alembic e `project_id` quando é recurso de projeto (ADR-0012).
- Valores de `${secret:}` nunca chegam a `task.json`, logs ou respostas da API.
- Dependências novas estão fixadas no lockfile e justificadas na nota de implementação.
- Nomes seguem o glossário.

## 4. O que não conta como pronto

- "Funciona na minha máquina" sem teste automatizado.
- Teste que só passa com Docker, sem marcação `docker`.
- Funcionalidade sem texto em pt-BR no catálogo ("vai traduzir depois").
- Documentação prometida para "a próxima sprint".
