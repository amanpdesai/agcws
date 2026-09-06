read_liberty {/home/aman/agcws/third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
read_verilog {/home/aman/agcws/out/aes-unmasked-matched-synthesis-v2/mapped.v}
link_design aes_cipher_core
create_clock -period 10 [get_ports clk_i]
read_vcd -scope aes_core_smoke/dut -begin_time 0 -end_time 8464999 {/home/aman/agcws/out/structural-temporal-finalists-v1/replays/5931833fd4c145d561d7d0c80484ce7c21da5668f7293b432dd13118bced9f15/gls/activity.vcd}
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
