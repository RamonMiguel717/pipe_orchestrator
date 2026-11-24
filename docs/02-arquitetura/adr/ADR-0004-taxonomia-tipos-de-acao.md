# ADR-0004 — Taxonomia única de tipos de ação

| Status | Data | Decisores |
|---|---|---|
| `Aceito` (v1.0) — Gate 2 em 2026-11-22 | 2026-11-22 | PO aprovou taxonomia única em Q5 |

## Contexto

Toda tarefa tem um tipo de ação. Nas tags ele é **o próprio nome do decorator** (ADR-0003 v0.2); nos blocos é a "tag" do bloco escolhida na paleta. Uma taxonomia única faz uma pipeline de código aparecer como blocos sem tradução, e dá à interface cor, ícone e modelo de código por tipo.

## Decisão

### Taxonomia do núcleo (v1) — os nomes são as tags

| Tipo / tag | Significado | Semântica no Engine |
|---|---|---|
| `step` | Passo genérico; o padrão quando o usuário não quer classificar | Nenhuma especial |
| `test` | Verificação; falha interrompe o que vem depois | **Portão** (única exceção a "só dados ordenam", ADR-0003 I2): passos chamados depois dela no corpo recebem `after`; a falha deixa esses passos `SKIPPED` |
| `extract` | Busca dados de uma origem | Nenhuma especial (só visualização) |
| `transform` | Transforma dados recebidos | Nenhuma especial |
| `load` | Grava dados em um destino | Nenhuma especial |
| `notify` | Envia aviso (e-mail, webhook, mensagem) | Nenhuma especial; conectores de alerta na Sprint 4 |
| `container` | Executa uma imagem/comando como a própria tarefa (sem função Python) | Executor Docker obrigatório; `code` ausente, comando em `params` (Sprint 1) |
| `branch` | Decide quais tarefas a jusante seguem | Saída define tarefas puladas (`SKIPPED`) — Sprint 4 |
| `wait` | Espera uma condição/evento externo (sensor) | Reexecução periódica até sucesso ou timeout — Sprint 4 |

Mudanças em relação à v0.1: `script` → `step` (nome mais natural e é o padrão); `validate` → `test` (vocabulário pedido pelo PO). No MVP todos os tipos são **aceitos na IR**; `branch` e `wait` executam como `step` até a Sprint 4 e a interface avisa isso.

### Regras

1. O tipo é **obrigatório** e validado contra a taxonomia no SDK, no construtor e no servidor.
2. A taxonomia é **extensível por plugin** (entry point `pipeorc.action_types`, ADR-0012): um plugin registra nome, descrição, ícone, modelo de código e, opcionalmente, um gancho de execução; o nome também vira uma tag importável (`from pipeorc.tags import <nome>`). Tipos de plugin usam prefixo (`plugin.tipo`) para não colidir com o núcleo.
3. Tipos do núcleo não são removidos em v1; podem ser adicionados por novo ADR.
4. "Tipo é metadado" — salvo `test` (portão), `container`, `branch` e `wait`.

## Consequências

- Positivas: vocabulário único em código, interface, API e documentação; `@step` sozinho já funciona; os demais só enriquecem a visualização.
- Negativas: usuários podem discordar da classificação — `step` é a válvula de escape.
- Riscos: tentação de dar semântica especial demais ao Engine por tipo; a regra 4 é o limite.

## Relacionados

ADR-0003, ADR-0005, ADR-0012; glossário "Tipo de ação".
