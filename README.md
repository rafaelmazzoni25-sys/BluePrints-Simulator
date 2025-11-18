# Blueprint Simulator

Ferramenta em Python para simular grafos simples inspirados em Blueprints da Unreal Engine 5+. 

## Recursos

- Estrutura de nós com tipos básicos (`Event`, `PrintString`, `SetVariable`, `Compute`, `Branch`).
- Sistema de resolução de valores com operações matemáticas e lógicas aninhadas.
- CLI para executar, descrever e listar nós disponíveis.
- Exemplo de grafo (`examples/player_speed.json`) pronto para uso.

## Instalação

Não há dependências externas além do Python 3.11+. Clone o repositório e execute os comandos diretamente com `python`.

```bash
python -m blueprint_simulator.cli nodes
```

## Formato de Blueprint

Arquivo JSON com os campos:

- `name`: nome do blueprint.
- `entry_point`: ID do nó inicial.
- `variables`: dicionário de variáveis expostas.
- `nodes`: lista de nós. Cada nó possui:
  - `id`: identificador único.
  - `type`: tipo do nó (veja `python -m blueprint_simulator.cli nodes`).
  - `next`: próximo nó (quando aplicável).
  - Parâmetros específicos por tipo (ex: `value`, `condition`, `store_as`, etc.).

### Valores e operações

Campos como `value`, `expression` ou `condition` aceitam:

- Literais (números, strings, booleanos).
- Referências a variáveis: `{ "var": "Speed" }`.
- Operações: 

```json
{
  "op": "add",
  "inputs": [ { "var": "Speed" }, 50 ]
}
```

- Strings formatadas: `{ "format": "Velocidade: {Speed}" }`.

Operações suportadas: `add`, `sub`, `mul`, `div`, `max`, `min`, `==`, `!=`, `>`, `<`, `>=`, `<=`, `and`, `or`, `not`.

## Executando um Blueprint

Use o CLI para rodar o exemplo:

```bash
python -m blueprint_simulator.cli run examples/player_speed.json
```

Saída esperada:

```json
{
  "variables": {
    "Speed": 750,
    "Acceleration": 150,
    "MaxSpeed": 1200
  },
  "logs": [
    "Velocidade final: 750"
  ]
}
```

É possível sobrescrever variáveis expostas:

```bash
python -m blueprint_simulator.cli run examples/player_speed.json --variable Speed=1000 --variable Acceleration=400
```

## Estrutura do Projeto

```
blueprint_simulator/
  cli.py            # Interface de linha de comando
  loader.py         # Leitura/validação de arquivos JSON
  nodes.py          # Implementação dos nós suportados
  runtime.py        # Runner que executa o grafo
  value_resolver.py # Resolução de valores e operações
examples/
  player_speed.json # Exemplo de blueprint
```

## Próximos Passos

- Adicionar suporte a loops e eventos personalizados.
- Exportar visualizações do grafo.
- Integrar com arquivos `.uasset` no futuro.
