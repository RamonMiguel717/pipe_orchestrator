# Critérios de aceite — Sprint 3: construtor de blocos v1 (Fluxo B)

| Campo | Valor |
|---|---|
| Status | `Em validação` — Gate 3 |
| Versão | 0.1 |
| Data | 2026-11-22 |
| Tamanho | G |
| Blocos | B04, B08, B02, B07 |

## Objetivo

Criar uma pipeline inteira dentro do app: blocos tipados, código em cada bloco, ligações, salvar como IR e executar. Pipelines vindas de tags aparecem como blocos.

## Pré-condições (DoR da sprint)

- Sprints 0 e 2 aprovadas (IR, API de registro, execução e histórico estáveis).
- Modelos de código por tipo de ação escritos (texto inicial de cada bloco).

## Critérios

| ID | Bloco | Critério | Verificação | Status |
|---|---|---|---|---|
| S3-01 | B04 | Paleta com os tipos de ação do núcleo (`step`, `test`, `extract`, `transform`, `load`, `notify`, `container`; `branch` e `wait` com aviso "semântica na Sprint 4"), cada um com ícone, cor e modelo de código | `tests/e2e/test_builder_palette.py` | Pendente |
| S3-02 | B04 | Criar pipeline nova (nome, descrição, agendamento opcional); adicionar bloco a partir da paleta; renomear; remover; desfazer/refazer | `tests/e2e/test_builder_crud.py` | Pendente |
| S3-03 | B04 | Editor de código por bloco (Monaco) com realce Python, modelo por tipo, e a assinatura da função definindo as **portas de entrada** (parâmetros) e a **porta de saída** (retorno) | `tests/e2e/test_builder_editor.py` | Pendente |
| S3-04 | B04 | Ligações: arrastar da saída de um bloco para um parâmetro de outro cria aresta de **dados** (`inputs`); ligação de **ordem** (equivale a `wait_for`) disponível por ação explícita e desenhada tracejada; `@test` como portão aplicado automaticamente aos blocos criados depois dele (com indicação visual e possibilidade de desligar) | `tests/e2e/test_builder_edges.py` | Pendente |
| S3-05 | B04 | Propriedades do bloco: `retries`, `timeout`, executor (Local / Docker + imagem + env), `params` literais, `name` | `tests/e2e/test_builder_props.py` | Pendente |
| S3-06 | B04 | Validação no cliente antes de salvar: ciclo, parâmetro sem ligação nem valor padrão, nome duplicado, Docker sem imagem; mensagens em pt-BR apontando o bloco | `tests/unit/web/test_builder_validation.spec.ts` | Pendente |
| S3-07 | B07 | `POST /api/v1/pipelines:validate` valida uma IR sem salvar e devolve erros no formato único; o construtor o usa | `tests/integration/test_validate_endpoint.py` | Pendente |
| S3-08 | B04 | Salvar gera IR com `source.kind = builder` e `code.kind = inline` e chama o **mesmo** endpoint de registro; cada salvamento com conteúdo diferente cria nova versão; histórico de versões com diferença entre duas versões (blocos adicionados/removidos/alterados) | `tests/integration/test_builder_save.py`, `tests/e2e/test_versions.py` | Pendente |
| S3-09 | B04 | Executar a partir do construtor e acompanhar o run na mesma tela, com o estado de cada bloco colorido em tempo real | `tests/e2e/test_builder_run.py` + Demo | Pendente |
| S3-10 | B04 | Pipeline vinda de tags é exibida como blocos **somente leitura**: código do módulo mostrado no editor em modo leitura, origem indicada, botão "Exportar IR/YAML"; tentativa de edição explica que a origem é o código | `tests/e2e/test_tags_readonly.py` | Pendente |
| S3-11 | B05 | Código inline com erro de sintaxe: linha apontada no editor e no erro de registro; limite de tamanho por bloco aplicado com mensagem | `tests/integration/test_inline_errors.py` | Pendente |
| S3-12 | B02 | Equivalência ampliada: três pipelines de referência (linear, fan-out/fan-in, com teste e `wait_for`) criadas via tags e via construtor geram IR semanticamente idêntica; o teste roda no `check` | `tests/equivalence/test_fixtures.py` | Pendente |
| S3-13 | B04 | Teste de ponta a ponta: criar pipeline com 3 blocos (extract → test → load em Docker), ligar, salvar, executar, ver sucesso e logs | `tests/e2e/test_builder_flow.py` | Pendente |
| S3-14 | B08 | Acessibilidade básica do construtor: operações principais por teclado; contraste dos tipos de ação verificado | Inspeção com lista de verificação | Pendente |

## Fora do escopo

Exportar pipeline de blocos como código com tags (Fase 2 posterior), colaboração, outras linguagens no bloco (Fase 2), `branch`/`wait` com semântica (Sprint 4).

## Roteiro de demonstração do gate (G3)

1. Criar do zero a pipeline "resumo_diario" com blocos extract → test → transform → load (Docker) → notify (ordem explícita).
2. Mostrar a validação impedindo salvar com um ciclo; corrigir.
3. Salvar, executar, acompanhar os blocos mudando de cor; abrir logs de um bloco.
4. Alterar o código de um bloco, salvar (versão 2), mostrar a diferença entre versões.
5. Abrir `etl_vendas` (vinda de tags) como blocos somente leitura; exportar YAML.
6. `scripts/check` com os testes de equivalência.

## Registro do gate

| Data | Decisão | Ressalvas |
|---|---|---|
| — | — | — |
