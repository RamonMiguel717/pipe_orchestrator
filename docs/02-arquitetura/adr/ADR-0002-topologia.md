# ADR-0002 — Topologia e fronteira da API

| Status | Data | Decisores |
|---|---|---|
| `Aceito` — Gate 2 em 2026-11-22 | 2026-11-22 | Direção dada pelo PO em Q1 (servidor único local no MVP) |

## Contexto

O PO definiu servidor único local para o MVP. A visão mantém a persona "equipe pequena" e a conexão a servidor remoto para a Fase 2. É preciso garantir que o MVP local **não** feche a porta para isso.

## Opções consideradas

| Opção | Descrição | Avaliação |
|---|---|---|
| A. App monolítico | Interface e Engine no mesmo processo, chamando funções internas | Mais simples no início; torna o servidor remoto uma reescrita |
| **B. Um processo servidor local + clientes só via HTTP** | Servidor (API + Engine + agendador + executores + UI estática) roda em `127.0.0.1`; CLI e interface falam **apenas** pela API | Mesmo custo que A no MVP; remoto vira troca de endereço e token |
| C. Servidor + worker separados desde o início | Engine em processo próprio, fila entre eles | Mais robusto, mas complexidade prematura para um usuário local |

## Decisão

Opção **B**:

1. **Um processo servidor** (`pipeorc server start`) que contém API, Engine, agendador, executores, persistência e a interface estática.
2. Escuta **somente em `127.0.0.1`** no MVP (porta padrão configurável). Expor em rede é uma configuração explícita da Fase 2, acompanhada de TLS/proxy.
3. **CLI e interface web são clientes HTTP** da API. Nenhum componente cliente importa código do servidor nem toca no banco (regra R5).
4. O Engine conversa com a camada de API por **interfaces internas** (fila/eventos assíncronos), não por acoplamento às rotas, para que a opção C (worker separado) seja possível depois sem mudar a API.
5. Conexão a servidor remoto (Fase 2) = `pipeorc config set server.url` + token; nenhuma mudança de arquitetura.

## Consequências

- Positivas: MVP simples de instalar e rodar; caminho limpo para remoto; a interface web pode ser servida de qualquer lugar.
- Negativas: até operações triviais passam por HTTP local (latência desprezível); exige disciplina para não criar atalhos.
- Riscos: processo único significa que uma tarefa mal comportada não pode derrubar o servidor — por isso tarefas **nunca** rodam no processo do servidor (ADR-0009).

## Relacionados

ADR-0008, ADR-0009, ADR-0010; visão R4/R5; blocos B07/B08.
