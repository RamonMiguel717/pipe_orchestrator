# Definition of Ready (DoR)

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |

A DoR diz o que um **item** precisa ter para entrar numa sprint e o que uma **sprint** precisa ter para começar. Evita começar a codificar algo que ainda depende de decisão.

## 1. Um item está pronto para entrar na sprint quando

| # | Condição | Como se verifica |
|---|---|---|
| R1 | Tem critério de aceite com ID no arquivo da sprint | `sprint-N.md` |
| R2 | O ADR que o sustenta está `Aceito` | [adr/README.md](../02-arquitetura/adr/README.md) |
| R3 | Se cria ou muda um contrato (IR, rota da API, Protocol de plugin, formato de arquivo), o contrato está escrito antes do código | seção correspondente em [01-arquitetura.md](../02-arquitetura/01-arquitetura.md) ou no ADR |
| R4 | Os dados ou fixtures de teste estão identificados (ex.: `exemplos/etl_vendas.py`, IR de referência) | listados no critério |
| R5 | As dependências de ambiente existem na máquina de desenvolvimento (ex.: Docker para a Sprint 1) | `pipeorc doctor` ou verificação manual |
| R6 | Tem tamanho estimado (P/M/G) e nenhum bloqueio conhecido sem dono | tabela de escopo da sprint |
| R7 | Mensagens voltadas ao usuário que o item introduz têm texto em pt-BR definido ou rascunhado (A3) | catálogo de textos |

## 2. Uma sprint está pronta para começar quando

| # | Condição |
|---|---|
| S1 | A sprint anterior passou pelo gate (ou é a Sprint 0 e o Gate 3 foi aprovado) |
| S2 | Todos os itens da sprint cumprem R1–R7 |
| S3 | As ressalvas herdadas da sprint anterior estão listadas como itens desta sprint |
| S4 | O roteiro de demonstração do gate está escrito no arquivo da sprint |
| S5 | Pré-condições duras cumpridas (ex.: Sprint 1 exige Docker `ready` e spike B.2 executado) |

## 3. O que acontece quando um item não está pronto

Ele **não entra** na sprint. Vira pendência com dono (PO ou agente) no `STATUS.md` e entra na sprint seguinte quando cumprir a DoR. Isso vale também para itens que dependem de decisão do PO: a decisão é tomada antes, não durante a sprint.
