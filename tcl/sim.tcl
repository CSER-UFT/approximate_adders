# ============================================================
# sim.tcl - Fluxo completo (synth + impl + sim + VCD + reports)
# Uso via Makefile:
#   vivado -mode tcl -source ./tcl/sim.tcl -tclargs <TB_NAME> [K]
# ============================================================

if {$argc < 1} {
    puts "ERRO: informe o nome do testbench (ex: sim_adder_8bit)"
    exit 1
}

set TB_NAME [lindex $argv 0]
set USER_K  ""
if {$argc > 1} {
    set USER_K [lindex $argv 1]
}

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

# Identifica N (8bit, 16bit, 32bit)
set BIT_STR "8bit"
foreach p $parts {
    if {[string match "*bit" $p]} {
        set BIT_STR $p
        break
    }
}

set ARCH_NAME [lindex $parts 0]

# Identifica K (parâmetro de aproximação)
if {$USER_K ne ""} {
    set K_VAL $USER_K
    set K_STR "k$USER_K"
} else {
    set K_STR ""
    foreach p $parts {
        if {[regexp {^k\d+$} $p]} {
            set K_STR $p
            set K_VAL [string range $p 1 end]
            break
        }
    }
    if {$K_STR eq ""} {
        if {$ARCH_NAME eq "rca"} {
            set K_VAL 0
            set K_STR "k0"
        } elseif {$BIT_STR eq "8bit"} {
            set K_VAL 4
            set K_STR "k4"
        } elseif {$BIT_STR eq "16bit"} {
            set K_VAL 8
            set K_STR "k8"
        } elseif {$BIT_STR eq "32bit"} {
            set K_VAL 16
            set K_STR "k16"
        } else {
            set K_VAL 0
            set K_STR "k0"
        }
    }
}

# Diretorios organizados
set REPORT_DIR  "$ROOT_DIR/vivado_reports/$BIT_STR/$K_STR"
set SIM_OUT_DIR "$ROOT_DIR/sim_output/$BIT_STR/$K_STR"
file mkdir $REPORT_DIR
file mkdir $SIM_OUT_DIR

set DESIGN_TOP "${ARCH_NAME}_${BIT_STR}"

set_property top $DESIGN_TOP [get_filesets sources_1]
set_property top $TB_NAME    [get_filesets sim_1]

# Injeta parâmetro K diretamente no Vivado (síntese e simulação)
if {$ARCH_NAME ne "rca"} {
    set_property generic "K=$K_VAL" [get_filesets sources_1]
    set_property generic "K=$K_VAL" [get_filesets sim_1]
    puts ">>> Parametro configurado: K = $K_VAL"
}

# Evita que o launch_simulation execute antes de abrir o VCD
set_property xsim.simulate.runtime 0ns [get_filesets sim_1]

catch { exec ln -sfn "$ROOT_DIR/data" "$BUILD_DIR/data" }
catch { exec ln -sfn "$RESULTS_DIR" "$BUILD_DIR/results" }
catch { exec ln -sfn "$ROOT_DIR/sim_output" "$BUILD_DIR/sim_output" }

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Síntese
launch_runs synth_1
wait_on_run synth_1

# Implementação
launch_runs impl_1
wait_on_run impl_1

# Relatórios de Área e Timing em vivado_reports/<N>bit/k<K>/
open_run impl_1
report_utilization -file "$REPORT_DIR/${TB_NAME}_resource.rpt"
report_timing_summary -file "$REPORT_DIR/${TB_NAME}_timing.rpt"

# Simulação e VCD em sim_output/<N>bit/k<K>/
set VCD_FILE "$SIM_OUT_DIR/${TB_NAME}.vcd"
set SIM_BEHAV_DIR "$BUILD_DIR/${PROJECT_NAME}.sim/sim_1/behav/xsim"
file mkdir $SIM_BEHAV_DIR
catch { exec ln -sfn "$ROOT_DIR/data" "$SIM_BEHAV_DIR/data" }
catch { exec ln -sfn "$RESULTS_DIR" "$SIM_BEHAV_DIR/results" }
catch { exec ln -sfn "$ROOT_DIR/sim_output" "$SIM_BEHAV_DIR/sim_output" }

launch_simulation
open_vcd $VCD_FILE

# Captura os objetos/sinais do DUT para o VCD de potência (evita variáveis de arquivos do testbench)
catch {
    set vcd_objs [get_objects -quiet "/$TB_NAME/dut/*"]
    if {[llength $vcd_objs] == 0} {
        set vcd_objs [get_objects -quiet "/$TB_NAME/DUT/*"]
    }
    if {[llength $vcd_objs] == 0} {
        set vcd_objs [get_objects -quiet -r "/$TB_NAME/dut/*"]
    }
    if {[llength $vcd_objs] == 0} {
        set vcd_objs [get_objects -quiet -r "/$TB_NAME/DUT/*"]
    }
    if {[llength $vcd_objs] == 0} {
        set vcd_objs [get_objects -quiet "/$TB_NAME/*"]
    }
    if {[llength $vcd_objs] == 0} {
        set vcd_objs [get_objects -quiet -r *]
    }
    if {[llength $vcd_objs] > 0} {
        log_vcd $vcd_objs
    }
}

run all
catch { close_vcd }
puts ">>> VCD gerado: $VCD_FILE"
catch { close_sim }

# Relatório de Potência em vivado_reports/<N>bit/k<K>/
current_design [get_designs impl_1]
catch { set_msg_config -id {Power 33-36} -suppress }
catch { read_vcd $VCD_FILE }
create_clock -name clk -period 10.0
report_power -file "$REPORT_DIR/${TB_NAME}_power.rpt"
puts ">>> Power gerado em $REPORT_DIR"

puts "=== FINALIZADO: $TB_NAME (K=$K_VAL) ==="
catch { close_project }
exit
