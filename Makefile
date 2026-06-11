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
	sim_ip_8bit \
	sim_ip_16bit_exponential \
	sim_ip_16bit_normal \
	sim_ip_16bit_uniform \
	sim_ip_32bit_exponential \
	sim_ip_32bit_normal \
	sim_ip_32bit_uniform \
	sim_rca_8bit \
	sim_rca_16bit_exponential \
	sim_rca_16bit_normal \
	sim_rca_16bit_uniform \
	sim_rca_32bit_exponential \
	sim_rca_32bit_normal \
	sim_rca_32bit_uniform \
	sim_cska_8bit \
	sim_cska_16bit_exponential \
	sim_cska_16bit_normal \
	sim_cska_16bit_uniform \
	sim_cska_32bit_exponential \
	sim_cska_32bit_normal \
	sim_cska_32bit_uniform \
	sim_csla_8bit \
	sim_csla_16bit_exponential \
	sim_csla_16bit_normal \
	sim_csla_16bit_uniform \
	sim_csla_32bit_exponential \
	sim_csla_32bit_normal \
	sim_csla_32bit_uniform \
	sim_csa_8bit \
	sim_csa_16bit_exponential \
	sim_csa_16bit_normal \
	sim_csa_16bit_uniform \
	sim_csa_32bit_exponential \
	sim_csa_32bit_normal \
	sim_csa_32bit_uniform \
	sim_cla_8bit \
	sim_cla_16bit_exponential \
	sim_cla_16bit_normal \
	sim_cla_16bit_uniform \
	sim_cla_32bit_exponential \
	sim_cla_32bit_normal \
	sim_cla_32bit_uniform \
	sim_ksa_8bit \
	sim_ksa_16bit_exponential \
	sim_ksa_16bit_normal \
	sim_ksa_16bit_uniform \
	sim_ksa_32bit_exponential \
	sim_ksa_32bit_normal \
	sim_ksa_32bit_uniform

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
