# Set project name and part
set project_name "somador_experiment"
set part_name "xc7s50csga324-1"

# Create project
create_project $project_name . -part $part_name -force
set_property target_language Verilog [current_project]

# Add design sources
add_files -norecurse ./src/full_adder.v
add_files -norecurse ./src/adder_8bit.v
add_files -norecurse ./src/adder_16bit.v
add_files -norecurse ./src/adder_32bit.v
add_files -norecurse ./src/cla_4bit.v
add_files -norecurse ./src/cla_8bit.v
add_files -norecurse ./src/cla_16bit.v
add_files -norecurse ./src/cla_32bit.v

# Add testbench sources
add_files -norecurse ./src/sim_adder_8bit.v
add_files -norecurse ./src/sim_adder_16bit_exponential.v
add_files -norecurse ./src/sim_adder_16bit_normal.v
add_files -norecurse ./src/sim_adder_16bit_uniform.v
add_files -norecurse ./src/sim_adder_32bit_exponential.v
add_files -norecurse ./src/sim_adder_32bit_normal.v
add_files -norecurse ./src/sim_adder_32bit_uniform.v
add_files -norecurse ./src/sim_cla_8bit.v
add_files -norecurse ./src/sim_cla_16bit_exponential.v
add_files -norecurse ./src/sim_cla_16bit_normal.v
add_files -norecurse ./src/sim_cla_16bit_uniform.v
add_files -norecurse ./src/sim_cla_32bit_exponential.v
add_files -norecurse ./src/sim_cla_32bit_normal.v
add_files -norecurse ./src/sim_cla_32bit_uniform.v

# Synthesize design
synth_design -top adder_8bit

# Synthesize design
synth_design -top adder_8bit
write_checkpoint -force ./results/adder_8bit_synth.dcp
report_utilization -file ./results/adder_8bit_utilization.rpt
report_timing -file ./results/adder_8bit_timing.rpt

synth_design -top adder_16bit
write_checkpoint -force ./results/adder_16bit_synth.dcp
report_utilization -file ./results/adder_16bit_utilization.rpt
report_timing -file ./results/adder_16bit_timing.rpt

synth_design -top adder_32bit
write_checkpoint -force ./results/adder_32bit_synth.dcp
report_utilization -file ./results/adder_32bit_utilization.rpt
report_timing -file ./results/adder_32bit_timing.rpt

synth_design -top cla_8bit
write_checkpoint -force ./results/cla_8bit_synth.dcp
report_utilization -file ./results/cla_8bit_utilization.rpt
report_timing -file ./results/cla_8bit_timing.rpt

synth_design -top cla_16bit
write_checkpoint -force ./results/cla_16bit_synth.dcp
report_utilization -file ./results/cla_16bit_utilization.rpt
report_timing -file ./results/cla_16bit_timing.rpt

synth_design -top cla_32bit
write_checkpoint -force ./results/cla_32bit_synth.dcp
report_utilization -file ./results/cla_32bit_utilization.rpt
report_timing -file ./results/cla_32bit_timing.rpt

# Implement design
place_design
route_design
# write_bitstream -force ./results/design.bit

exit
