# Documentação do projeto

Esta pasta é a fonte única de verdade sobre **o que** o sistema deve ser, **como** será construído e **em que ponto** o desenvolvimento está. Cada etapa do fluxo tem a sua pasta numerada; o que é transversal fica em `00-processo`.

## Mapa

| Pasta | Conteúdo | Etapa do fluxo |
|---|---|---|
| [00-processo/](00-processo/) | Metodologia, gates de validação, acompanhamento (STATUS), glossário | Transversal |
| [01-planejamento/](01-planejamento/) | Visão e escopo, blocos funcionais e responsabilidades, perguntas de validação | 1. Planejamento |
| [02-arquitetura/](02-arquitetura/) | Arquitetura detalhada, ADRs (registro de decisões), spikes, plano de sprints | 2. Refinamento e arquitetura |
| [03-criterios-aceite/](03-criterios-aceite/) | Critérios de aceite por sprint, Definition of Ready / Done | 3. Critérios de aceite |
| [04-desenvolvimento/](04-desenvolvimento/) | Notas de implementação por sprint, changelog | 4. Desenvolvimento |
| [05-testes/](05-testes/) | Estratégia e relatórios de teste | 5. Testes |
| [06-refinamento/](06-refinamento/) | Retrospectivas, débitos técnicos, ajustes (ciclo DevOps) | 6. Refinamento |
| [07-entrega-final/](07-entrega-final/) | Empacotamento, documentação de uso, checklist de entrega | 7. Entrega final |

## Legenda de status dos documentos

| Status | Significado |
|---|---|
| `Rascunho` | Escrito pelo agente, ainda não lido/validado pelo Product Owner |
| `Em validação` | Entregue para leitura; aguardando aprovação ou pedidos de ajuste |
| `Aprovado` | Validado pelo Product Owner; serve de base para a etapa seguinte |
| `Superado` | Substituído por uma versão mais nova (mantido para histórico) |

Todo documento começa com um cabeçalho de **Status**, **Versão** e **Data**. Mudanças depois de `Aprovado` geram nova versão e voltam para `Em validação`.

## Por onde começar

1. [00-processo/metodologia.md](00-processo/metodologia.md) — o fluxo de trabalho e os ajustes propostos a ele.
2. [01-planejamento/01-visao-e-escopo.md](01-planejamento/01-visao-e-escopo.md) — o que o sistema é e o que não é.
3. [01-planejamento/02-blocos-funcionais.md](01-planejamento/02-blocos-funcionais.md) — os blocos gerais e suas responsabilidades (entrega da Etapa 1).
4. [01-planejamento/03-perguntas-para-validacao.md](01-planejamento/03-perguntas-para-validacao.md) — as decisões que precisam do Product Owner antes do Gate 1.
