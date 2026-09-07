read_liberty {/opt/agcws/third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
read_verilog {/opt/agcws/out/inputs/aes/synthesis/mapped.v}
link_design aes_cipher_core
create_clock -period 10 [get_ports clk_i]
read_vcd -scope aes_core_smoke/dut -begin_time 25404999 -end_time 33874999 {/opt/agcws/out/aes/gls/activity.vcd}
report_power -digits 12
report_activity_annotation -report_unannotated

set leaf_switching 0.0
set leaf_count 0
foreach inst [sta::network_leaf_instances] {
    set values [sta::instance_power $inst [sta::cmd_scene]]
    set leaf_switching [expr {$leaf_switching + [lindex $values 1]}]
    incr leaf_count
}
puts "LEAF_SWITCHING_SUM $leaf_count [format %.17g $leaf_switching]"
