# ============================================================
# sim.tcl - Fluxo completo (synth + impl + sim + VCD + reports)
# Uso via Makefile:
#   vivado -mode tcl -source ./tcl/sim.tcl -tclargs <TB_NAME>
# ============================================================

if {$argc < 1} {
    puts "ERRO: informe o nome do testbench (ex: sim_adder_8bit)"
    exit 1
}

set TB_NAME [lindex $argv 0]

set SCRIPT_DIR [file dirname [file normalize [info script]]]
set ROOT_DIR   [file normalize "$SCRIPT_DIR/.."]

set SRC_DIR     "$ROOT_DIR/src"
set RESULTS_DIR "$ROOT_DIR/results"
set BUILD_DIR   "$ROOT_DIR/build/$TB_NAME"

file mkdir $RESULTS_DIR
catch { exec rm -rf $BUILD_DIR }
file mkdir $BUILD_DIR

set PROJECT_NAME "${TB_NAME}_proj"

create_project $PROJECT_NAME $BUILD_DIR -part xc7s50csga324-1 -force
set_property target_language Verilog [current_project]

foreach f [glob -nocomplain "$SRC_DIR/*.v"] {
    add_files $f
}

set name_no_sim [string range $TB_NAME 4 end]
set parts [split $name_no_sim "_"]
set DESIGN_TOP "[lindex $parts 0]_[lindex $parts 1]"

set_property top $DESIGN_TOP [get_filesets sources_1]
set_property top $TB_NAME    [get_filesets sim_1]

# Evita que o launch_simulation execute antes de abrir o VCD
set_property xsim.simulate.runtime 0ns [get_filesets sim_1]

catch { exec ln -sfn "$ROOT_DIR/data" "$BUILD_DIR/data" }
catch { exec ln -sfn "$RESULTS_DIR" "$BUILD_DIR/results" }

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Síntese
launch_runs synth_1
wait_on_run synth_1

# Implementação
launch_runs impl_1
wait_on_run impl_1

# Relatórios de Área e Timing
open_run impl_1
report_utilization -file "$RESULTS_DIR/${TB_NAME}_resource.rpt"
report_timing_summary -file "$RESULTS_DIR/${TB_NAME}_timing.rpt"

# Simulação e VCD
set VCD_FILE "$RESULTS_DIR/${TB_NAME}.vcd"
set SIM_BEHAV_DIR "$BUILD_DIR/${PROJECT_NAME}.sim/sim_1/behav/xsim"
file mkdir $SIM_BEHAV_DIR
catch { exec ln -sfn "$ROOT_DIR/data" "$SIM_BEHAV_DIR/data" }
catch { exec ln -sfn "$RESULTS_DIR" "$SIM_BEHAV_DIR/results" }

launch_simulation
open_vcd $VCD_FILE
log_vcd [get_objects /$TB_NAME/*]
run all
close_vcd
puts ">>> VCD gerado: $VCD_FILE"
catch { close_sim }

# Relatório de Potência
current_design [get_designs impl_1]
read_vcd $VCD_FILE
create_clock -name clk -period 10.0
report_power -file "$RESULTS_DIR/${TB_NAME}_power.rpt"
puts ">>> Power gerado"

puts "=== FINALIZADO: $TB_NAME ==="
catch { close_project }
exit
