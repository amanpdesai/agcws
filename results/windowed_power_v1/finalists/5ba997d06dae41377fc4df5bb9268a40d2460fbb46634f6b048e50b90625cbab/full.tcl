read_liberty {/home/aman/agcws/third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
read_verilog {/home/aman/agcws/out/axi-dma-synthesis-gls3/mapped.v}
link_design axi_dma
create_clock -period 10 [get_ports clk]
read_vcd -scope axi_dma -begin_time 0 -end_time 120005001 {/home/aman/agcws/out/structural-temporal-finalists-v1/replays/5ba997d06dae41377fc4df5bb9268a40d2460fbb46634f6b048e50b90625cbab/gls/activity.vcd}
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
