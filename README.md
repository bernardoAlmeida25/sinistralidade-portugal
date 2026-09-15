# Sinistralidade em Portugal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![Data](https://img.shields.io/badge/data-daily%20updates-brightgreen)

Análise e visualização de dados sobre sinistralidade rodoviária em Portugal.

Part of a broader effort to build open datasets about Portugal, inspired by [Central de Dados](https://github.com/centraldedados).

## What it does

Este projeto coleta, processa e analisa dados sobre sinistralidade rodoviária em Portugal, fornecendo insights sobre padrões e tendências de acidentes de trânsito ao longo do tempo e por região.

O projeto:
- Coleta dados de sinistralidade de fontes oficiais
- Processa e normaliza os dados em um formato consistente
- Gera análises descritivas e visualizações gráficas
- Exporta resultados para análise adicional

## Sample data

| Ano | Tipo_de_Acidente | Localizacao | Numero_de_Vitimas | Condicoes_Meteorologicas |
|---|---|---|---|---|
| 2019 | Colisão Frontal | Avenida da Liberdade, Lisboa | 2 | Ensolarado |
| 2020 | Queda de Veículo | Estrada Nacional 10, Porto | 1 | Chuvoso |
| 2021 | Colisão Lateral | Autoestrada A1, Coimbra | 3 | Nublado |
## Requirements

- Python version pinned in `.python-version`
- Dependencies declared in `pyproject.toml` (`pandas`, `matplotlib`, `seaborn`, `numpy`)
- [uv](https://docs.astral.sh/uv/) for dependency management

Install with:

```bash
uv sync
```

## Usage

```bash
uv run main.py
```
Este script processa os dados de sinistralidade e gera visualizações e análises que são salvas na pasta output/.

### Output

A pasta `output/` contém:
- Gráficos e visualizações geradas
- Arquivos CSV com dados processados
- Relatórios de análise

## Adding another data source

O projeto pode ser expandido para incluir mais fontes de dados sobre sinistralidade rodoviária em Portugal. Para adicionar uma nova fonte:

1. Crie uma nova função de coleta que se conecte à API ou fonte de dados
2. Adicione a lógica de processamento para normalizar os dados
3. Atualize o script principal para incluir a nova fonte

## Notes

- Os dados são coletados de fontes oficiais do Instituto Nacional de Estatística (INE) e outros órgãos governamentais
- O projeto segue boas práticas de tratamento de dados e é compatível com as regulamentações de proteção de dados em Portugal
- As visualizações geradas podem ser usadas para análises políticas e de segurança pública

## License

Code is licensed under the [MIT License](LICENSE).

