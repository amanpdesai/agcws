read_liberty {/home/aman/agcws/third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
read_verilog {/home/aman/agcws/out/axi-dma-synthesis-gls3/mapped.v}
link_design axi_dma
create_clock -period 10 [get_ports clk]
read_vcd -scope axi_dma -begin_time 75009999 -end_time 90009999 {/home/aman/agcws/out/structural-temporal-finalists-v1/replays/410f2f1aa78f552043ad88f465c2478c33b81a695a0cdf0edcc5fe73bf9d21c6/gls/activity.vcd}
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
