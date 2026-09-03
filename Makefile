# =========================================================
# Makefile - Fluxo completo Vivado (genérico por experimento)
# =========================================================

# Diretórios
SRC_DIR     = ./src
DATA_DIR    = ./data
RESULTS_DIR = ./results
TCL_DIR     = ./tcl
BUILD_DIR   = ./build

# Script TCL
RUN_TCL = $(TCL_DIR)/sim.tcl

# Lista de experimentos (testbenches)
EXPERIMENTS = \
	sim_rca_8bit \
	sim_rca_16bit_exponential \
	sim_rca_16bit_normal \
	sim_rca_16bit_uniform \
	sim_rca_32bit_exponential \
	sim_rca_32bit_normal \
	sim_rca_32bit_uniform \
	sim_loa_8bit \
	sim_loa_16bit_exponential \
	sim_loa_16bit_normal \
	sim_loa_16bit_uniform \
	sim_loa_32bit_exponential \
	sim_loa_32bit_normal \
	sim_loa_32bit_uniform \
	sim_heaa_8bit \
	sim_heaa_16bit_exponential \
	sim_heaa_16bit_normal \
	sim_heaa_16bit_uniform \
	sim_heaa_32bit_exponential \
	sim_heaa_32bit_normal \
	sim_heaa_32bit_uniform \
	sim_hoeraa_8bit \
	sim_hoeraa_16bit_exponential \
	sim_hoeraa_16bit_normal \
	sim_hoeraa_16bit_uniform \
	sim_hoeraa_32bit_exponential \
	sim_hoeraa_32bit_normal \
	sim_hoeraa_32bit_uniform \
	sim_herloa_8bit \
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
all: $(RESULTS_DIR) $(EXPERIMENTS)

# Executa um experimento específico:
# make run TB=sim_rca_16bit_uniform
run:
	@if [ -z "$(TB)" ]; then \
		echo "Uso: make run TB=<nome_do_testbench>"; \
		exit 1; \
	fi
	vivado -mode tcl -source $(RUN_TCL) -tclargs $(TB)

# Regra genérica para cada experimento
$(EXPERIMENTS): %: $(RESULTS_DIR)
	vivado -mode tcl -source $(RUN_TCL) -tclargs $@

# Garante pasta de resultados
$(RESULTS_DIR):
	mkdir -p $(RESULTS_DIR)

# Limpeza
clean:
	rm -rf $(RESULTS_DIR) $(BUILD_DIR)

# Limpeza completa (inclui projetos Vivado)
clean_all:
	rm -rf $(RESULTS_DIR) $(BUILD_DIR) *.jou *.log .Xil

.PHONY: all run clean clean_all $(EXPERIMENTS)
