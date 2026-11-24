# ADR-0005 — Formato e versionamento da IR

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Agente, sustentado pelo spike C |

## Contexto

A Definição de pipeline (IR) é o ponto de convergência entre tags e blocos e o que o servidor armazena e executa. O spike C validou um esquema v0.1 e a equivalência entre os dois caminhos.

## Opções consideradas

| Aspecto | Opções | Escolha |
|---|---|---|
| Formato canônico | JSON; YAML; formato binário | **JSON** (API, banco); YAML só import/export |
| Fonte do schema | schema escrito à mão; **gerado dos modelos Pydantic** | gerado (uma fonte de verdade) |
| Arestas | lista separada de `edges`; **derivadas de `inputs` + `after`** | derivadas (sem redundância que dessincroniza) |
| Versionamento | mutável; **versões imutáveis por hash** | imutáveis |

## Decisão

### Estrutura (v0.1, evolui com `ir_version`)

```json
{
  "ir_version": "0.1",
  "pipeline": {
    "name": "etl_vendas", "description": "...", "version": null,
    "schedule": {"cron": "0 6 * * *"},
    "source": {"kind": "tags" | "builder", "module": "...", "path": "..."}
  },
  "tasks": [{
    "id": "carregar", "type": "load",
    "inputs": {"transformar": "transformar"},
    "after": ["validar"],
    "retries": 0, "timeout_s": null, "params": {},
    "executor": {"kind": "local"} | {"kind": "docker", "image": "...", "env": {...}},
    "code": {"kind": "module", "language": "python", "module": "etl", "callable": "carregar", "path": "etl.py"}
          | {"kind": "inline", "language": "python", "source": "...", "entrypoint": "carregar"}
  }]
}
```

### Regras

1. **JSON canônico** (chaves ordenadas, tarefas ordenadas por `id`) é o que a API recebe/devolve e o banco guarda. O **hash SHA-256** do JSON canônico identifica a versão.
2. **Registrar uma IR** cuja hash já existe para aquela pipeline não cria versão nova. Hash diferente cria `PipelineVersion` nova e imutável; runs referenciam a versão.
3. O JSON Schema é **gerado** dos modelos Pydantic (`pipeorc ir schema`) e publicado com a API para validação por terceiros.
4. **YAML** é aceito em `pipeorc import` / produzido em `pipeorc export` e no botão de exportar da interface; convertido para JSON canônico na entrada.
5. Referências a segredos em `executor.env` e `params` usam `${secret:NOME}` e são resolvidas só no despacho (ADR-0009); a IR nunca contém o valor.
6. Mudanças incompatíveis incrementam `ir_version`; o servidor mantém migradores de IR entre versões.

## Consequências

- Positivas: equivalência tags ≡ blocos garantida por construção; histórico de versões gratuito; validação uniforme em SDK, servidor e interface (schema).
- Negativas: `inline` guarda código no banco (ok para blocos; limitar tamanho); `module` depende de o arquivo existir na execução.
- Riscos: crescimento do schema; mitigado por `ir_version` e testes de compatibilidade.

## Relacionados

ADR-0003, ADR-0004, ADR-0009; spike C; bloco B02.
