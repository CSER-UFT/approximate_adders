# =========================================================
# Makefile - Fluxo completo Vivado (genérico por experimento)
# =========================================================

# Diretórios
SRC_DIR            = ./src
DATA_DIR           = ./data
RESULTS_DIR        = ./results
VIVADO_REPORTS_DIR = ./vivado_reports
SIM_OUTPUT_DIR     = ./sim_output
SCRIPTS_DIR        = ./scripts
TCL_DIR            = ./tcl
BUILD_DIR          = ./build

# Script TCL
RUN_TCL = $(TCL_DIR)/sim.tcl

# Lista de experimentos (testbenches)
EXPERIMENTS = \
	sim_rca_8bit \
	sim_loa_8bit \
	sim_heaa_8bit \
	sim_hoeraa_8bit \
	sim_herloa_8bit \
	sim_rca_16bit_exponential \
	sim_rca_16bit_normal \
	sim_rca_16bit_uniform \
	sim_rca_32bit_exponential \
	sim_rca_32bit_normal \
	sim_rca_32bit_uniform \
	sim_loa_16bit_exponential \
	sim_loa_16bit_normal \
	sim_loa_16bit_uniform \
	sim_loa_32bit_exponential \
	sim_loa_32bit_normal \
	sim_loa_32bit_uniform \
	sim_heaa_16bit_exponential \
	sim_heaa_16bit_normal \
	sim_heaa_16bit_uniform \
	sim_heaa_32bit_exponential \
	sim_heaa_32bit_normal \
	sim_heaa_32bit_uniform \
	sim_hoeraa_16bit_exponential \
	sim_hoeraa_16bit_normal \
	sim_hoeraa_16bit_uniform \
	sim_hoeraa_32bit_exponential \
	sim_hoeraa_32bit_normal \
	sim_hoeraa_32bit_uniform \
	sim_herloa_16bit_exponential \
	sim_herloa_16bit_normal \
	sim_herloa_16bit_uniform \
	sim_herloa_32bit_exponential \
	sim_herloa_32bit_normal \
	sim_herloa_32bit_uniform

# =========================================================
# Targets
# =========================================================

# Executa todos os experimentos
all: $(EXPERIMENTS)

# Executa um experimento específico:
# Exemplo padrão:   make run TB=sim_loa_8bit
# Exemplo com K:     make run TB=sim_loa_8bit K=2
run:
	@if [ -z "$(TB)" ]; then \
		echo "Uso: make run TB=<nome_do_testbench> [K=<valor>]"; \
		exit 1; \
	fi
	vivado -mode tcl -source $(RUN_TCL) -tclargs $(TB) $(K)

# Regra genérica para cada experimento
$(EXPERIMENTS): %:
	vivado -mode tcl -source $(RUN_TCL) -tclargs $@ $(K)

# Pós-processamento e Consolidação
parse:
	python3 $(SCRIPTS_DIR)/parse_results.py

metrics:
	python3 $(SCRIPTS_DIR)/calculate_error_metrics.py

plots:
	python3 $(SCRIPTS_DIR)/plot_results.py

# Limpeza
clean:
	rm -rf $(BUILD_DIR)

# Limpeza completa (inclui projetos Vivado)
clean_all:
	rm -rf $(BUILD_DIR) *.jou *.log .Xil

.PHONY: all run parse metrics plots clean clean_all $(EXPERIMENTS)
