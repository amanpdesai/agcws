read_liberty {/home/aman/agcws/out/tools/opensta-a9a3f30/source/test/asap7_invbuf.lib.gz}
read_verilog {/home/aman/agcws/out/tools/opensta-a9a3f30/source/test/vcd_begin_end_time.v}
link_design top
create_clock -period 100 [get_ports clk]
sta::clear_power
read_vcd -scope top -begin_time 0 -end_time 24 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 0 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 24 -end_time 44 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 1 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 44 -end_time 64 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 2 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 64 -end_time 84 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 3 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 84 -end_time 104 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 4 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 104 -end_time 124 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 5 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 124 -end_time 144 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 6 [get_property [get_pins u_inv/A] activity]"
sta::clear_power
read_vcd -scope top -begin_time 144 -end_time 160 {/home/aman/agcws/results/window_semantics_v1/toy-10ps.vcd.txt}
puts "BIN 7 [get_property [get_pins u_inv/A] activity]"
