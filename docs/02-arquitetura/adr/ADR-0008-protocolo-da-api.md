# ADR-0008 — Protocolo da API aberta

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente |

## Contexto

A API é o único caminho de entrada ao servidor (ADR-0002) e um diferencial declarado (D4). Precisa de operações CRUD, disparo de runs e **fluxos em tempo real** (logs, estado), com especificação pública.

## Opções consideradas

| Aspecto | Opções | Escolha |
|---|---|---|
| Estilo | **REST JSON**; GraphQL; gRPC | REST (simplicidade, OpenAPI, curl) |
| Tempo real | WebSocket; **SSE**; polling | SSE (unidirecional basta; HTTP puro; reconexão nativa) |
| Autenticação | nenhuma (local); **token Bearer**; sessão/cookie | token Bearer desde o MVP |
| Versionamento | header; **prefixo de caminho** | `/api/v1` |

## Decisão

1. **REST JSON em `/api/v1`**, com **OpenAPI 3.1** gerada pelo FastAPI e publicada em `/api/openapi.json` e `/api/docs`.
2. **Server-Sent Events** para fluxos: `GET /api/v1/events` (estado de runs/tarefas de todo o servidor, filtrável), `GET /api/v1/runs/{id}/events` e `GET /api/v1/runs/{id}/tasks/{task}/logs/stream`. Mensagens JSON com `id` incremental para `Last-Event-ID`; em reconexão, o cliente reconsulta o estado via REST. WebSocket só se surgir necessidade bidirecional.
3. **Autenticação por token Bearer** (API key). No primeiro `pipeorc server start` um token é gerado, gravado em `<dados>/config.toml` com permissão restrita e exibido uma vez. CLI e interface o leem dali; sistemas externos recebem tokens criados por `pipeorc token create`. Tokens guardados como hash.
4. **CORS** restrito à origem local da interface. Sem TLS no MVP (só `127.0.0.1`); TLS/proxy entra com exposição em rede (Fase 2).
5. Erros em formato único: `{ "error": { "code": "...", "message": "...", "details": [...] } }`, mensagens voltadas ao usuário.
6. Paginação por cursor em listagens; filtros por query string; `ETag` nas versões de pipeline.
7. Compatibilidade: `v1` não quebra contratos após a Entrega final; mudanças incompatíveis criam `v2`.

## Consequências

- Positivas: qualquer linguagem integra com curl; especificação gera clientes (TypeScript da interface, Python do SDK); SSE funciona atrás de proxies comuns.
- Negativas: SSE é unidirecional (controle sempre por REST); limite de conexões SSE por navegador (6 por origem em HTTP/1.1) — a interface multiplexa em um canal `/events`.
- Riscos: token em arquivo local — mitigado por permissões do arquivo e por nunca aparecer em logs.

## Relacionados

ADR-0002, ADR-0007, ADR-0012; bloco B07, B12.
