# ADR-0007 — Interface web

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | PO definiu interface web (Q3); tecnologia escolhida pelo agente |

## Contexto

A interface precisa de: lista e detalhe de pipelines, **grafo de blocos** (visualização no MVP, edição na Sprint 3), acompanhamento de runs com logs em tempo real, agendamentos e, na Fase 2, um **editor de código por bloco**. Node e npm estão disponíveis na máquina do PO.

## Opções consideradas

| Opção | Prós | Contras |
|---|---|---|
| A. Templates no servidor (Jinja) + HTMX | Sem build de front; tudo em Python | Construtor de blocos (arrastar, ligar, editar código) é inviável sem um cliente rico |
| **B. React + TypeScript + Vite, servido como estático pelo FastAPI** | Ecossistema maduro para grafos (React Flow) e editor (Monaco); build simples; um só servidor | Dois toolchains (Python + Node) no desenvolvimento |
| C. App desktop nativo (Tauri/Electron) desde o início | Experiência de app instalado | Custo de empacotamento alto cedo; a interface web pode ser envelopada depois |

## Decisão

Opção **B**:

- **React 18 + TypeScript + Vite**; roteamento com React Router; dados com TanStack Query; cliente da API gerado do OpenAPI.
- **React Flow** para o grafo de pipelines (somente leitura no MVP; edição e ligação de blocos na Sprint 3).
- **Monaco Editor** para o código de cada bloco (Sprint 3).
- Build produz arquivos estáticos copiados para o pacote Python e servidos pelo FastAPI em `/`; a API fica em `/api/v1`. Nenhum servidor Node em produção.
- Textos da interface em **catálogo** (JSON) para permitir tradução; idioma inicial conforme pendência A3 (recomendação: pt-BR).
- Abertura no navegador padrão (`pipeorc ui` ou ao iniciar o servidor). Envelope desktop (pywebview ou Tauri) **avaliado na Fase 2**, sem mudança na interface.
- Design: paleta e componentes próprios simples; sem framework visual pesado. Acessibilidade básica (teclado, contraste) desde o início.

## Consequências

- Positivas: capacidade para o construtor de blocos; interface desacoplada do servidor (só API); fácil envelopar como desktop depois.
- Negativas: exige Node no desenvolvimento (não no uso); build de front entra na pipeline de empacotamento.
- Riscos: React Flow e Monaco são dependências grandes — carregadas sob demanda nas rotas que usam.

## Relacionados

ADR-0002, ADR-0008, ADR-0011; blocos B04, B08.
