# Como executar o projeto

## 1. Visão geral

Este repositório contém a descrição em Verilog de somadores aproximados para FPGA, o fluxo de síntese, implementação e simulação no Vivado e os scripts Python que extraem as métricas e geram os gráficos a partir dos resultados.

São avaliadas cinco arquiteturas: RCA (somador exato, usado como referência), LOA, HEAA, HOERAA e HERLOA. Nos somadores aproximados, os `K` bits menos significativos são calculados por uma lógica simplificada e os `N - K` bits restantes por uma cadeia de somadores completos. Cada configuração é avaliada quanto ao erro (MAE, MSE, MRE e EP), à área (LUTs) e à potência, em larguras de 8, 16 e 32 bits. O dispositivo alvo é o Spartan-7 `xc7s50csga324-1`.

O fluxo:

1. **Instalar as dependências** (Vivado e pacotes Python).
2. **Gerar as entradas** dos testbenches (`entries.py` e `generate_data_and_plot.py`), caso seja necessário alterá-las.
3. **Executar os experimentos no Vivado** (`make <testbench> K=<valor>`).
4. **Processar os resultados e gerar os gráficos** (`make parse`, `make metrics` e `make plots`).
5. **Executar a análise visual** em imagens (`make visual` e `make visual_dataset`).

## 2. Requisitos

- AMD Vivado, com o comando `vivado` disponível no `PATH`. A edição gratuita (ML Standard) oferece suporte ao dispositivo utilizado.
- Python 3 com os pacotes `numpy`, `matplotlib` e `scikit-image`.
- `make`.

Os gráficos utilizam vírgula como separador decimal quando o locale `pt_BR.UTF-8` está disponível no sistema. Caso contrário, é utilizado o ponto.

## 3. Instalação

### 3.1 Vivado

Após a instalação, carregue o script de ambiente para disponibilizar o comando `vivado` no terminal:

```bash
source /caminho/para/Xilinx/Vivado/<versão>/settings64.sh
vivado -version
```

### 3.2 Dependências Python

```bash
# Na raiz do repositório
python3 -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib scikit-image
```

## 4. Estrutura do repositório

| Diretório         | Conteúdo                                                        |
|-------------------|-----------------------------------------------------------------|
| `src/`            | Módulos Verilog dos somadores e testbenches (`sim_*.v`)         |
| `tcl/`            | Fluxo do Vivado: síntese, implementação, simulação e relatórios |
| `data/`           | Entradas dos testbenches e imagens da análise visual            |
| `sim_output/`     | Saídas das simulações, organizadas por largura e por K          |
| `vivado_reports/` | Relatórios de utilização, timing e potência                     |
| `results/`        | Arquivos CSV com as métricas consolidadas                       |
| `plots/`          | Gráficos gerados a partir dos arquivos CSV                      |
| `scripts/`        | Scripts Python de geração de dados, processamento e gráficos    |

## 5. Execução

Todos os comandos devem ser executados a partir da raiz do repositório.

### 5.1 Geração das entradas

Os arquivos de entrada já estão disponíveis em `data/`. A geração só é necessária caso eles sejam alterados.

```bash
python3 scripts/entries.py                  # 8 bits: todas as combinações de entrada
python3 scripts/generate_data_and_plot.py   # 16 e 32 bits: distribuições uniforme, normal e exponencial
```

O segundo script utiliza semente fixa e também salva os histogramas das distribuições em `plots/error_metrics/`.

### 5.2 Experimentos no Vivado

Cada experimento corresponde a um testbench em `src/`, nomeado no padrão `sim_<arquitetura>_<largura>[_<distribuição>]`. Para executar um experimento com um valor de K específico:

```bash
make sim_loa_16bit_uniform K=4
# ou
make run TB=sim_loa_16bit_uniform K=4
```

O somador exato deve ser executado sem o parâmetro K:

```bash
make sim_rca_16bit_uniform
```

Os valores de K avaliados são:

| Largura | Entradas                                              | K             |
|---------|-------------------------------------------------------|---------------|
| 8 bits  | 65.536 pares (todas as combinações)                   | 1, 2, 3, 4    |
| 16 bits | 50.000 pares por distribuição                         | 2, 3, 4, 5, 6 |
| 32 bits | 100.000 pares por distribuição                        | 4, 6, 8, 10   |

Exemplo de varredura para 16 bits com distribuição uniforme:

```bash
make sim_rca_16bit_uniform
for arch in loa heaa hoeraa herloa; do
  for k in 2 3 4 5 6; do
    make sim_${arch}_16bit_uniform K=$k
  done
done
```

As saídas de simulação são salvas em `sim_output/<largura>/k<K>/` e os relatórios em `vivado_reports/<largura>/k<K>/`.

### 5.3 Processamento dos resultados

```bash
make parse     # relatórios do Vivado -> results/summary_main.csv
make metrics   # métricas de erro em relação ao RCA -> results/error_metrics_main.csv
make plots     # gráficos em plots/
```

Os gráficos são organizados em:

- `plots/design_space_exploration/`: erro, LUTs e potência em função de K para cada largura.
- `plots/error_metrics/`: comparações de erro entre arquiteturas e distribuições.
- `plots/hardware_metrics/`: comparações de área e potência.

### 5.4 Análise visual

A análise visual aplica os somadores de 8 bits em operações sobre imagens (soma de pixels vizinhos e filtro de média 2x2) e calcula PSNR e SSIM em relação ao resultado exato. Esta etapa não depende do Vivado.

```bash
make visual           # imagens de teste: painéis em plots/visual_benchmark/ e métricas em results/visual_metrics.csv
make visual_dataset   # conjunto de 100 imagens: métricas em results/dataset_filter_*.csv
```

### 5.5 Limpeza

```bash
make clean       # remove os projetos do Vivado em build/
make clean_all   # remove também logs e arquivos temporários do Vivado
```
