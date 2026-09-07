.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 0
  li a2, 1
  li a3, 4294967295
  li a4, 2936092242
  li a5, 1
  li a6, 4294967295
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 463
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 260
.Lloop0:
  srl a3, a6, a1
  and a4, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 2495
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 276
.Lloop1:
  sll a6, a0, a5
  divu a1, a4, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 22162
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 112
.Lloop2:
  srl a4, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 47338
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 524
.Lloop3:
  divu a5, a3, a3
  divu a2, a5, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 58746
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 30
.Lloop4:
  mul a7, a3, a0
  mul a5, a6, a1
  mul a2, a2, a1
  mul a5, a3, a0
  mul a6, a0, a0
  mul a6, a0, a0
  mul a2, a1, a1
  mul a5, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 96682
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 504
.Lloop5:
  mul a3, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 110408
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 140
.Lloop6:
  bnez a1, .Lskip6_0
  mv a7, a5
.Lskip6_0:
  bnez a7, .Lskip6_1
  mv a2, a3
.Lskip6_1:
  bnez a0, .Lskip6_2
  mv a7, a7
.Lskip6_2:
  bnez a4, .Lskip6_3
  mv a2, a5
.Lskip6_3:
  bnez a0, .Lskip6_4
  mv a0, a6
.Lskip6_4:
  bnez a7, .Lskip6_5
  mv a4, a6
.Lskip6_5:
  bnez a7, .Lskip6_6
  mv a1, a6
.Lskip6_6:
  bnez a6, .Lskip6_7
  mv a2, a3
.Lskip6_7:
  addi t6, t6, -1
  bnez t6, .Lloop6
.global body_complete
body_complete:
  addi s11, zero, 2
  li s9, 200064
  add s9, s9, s10
.Lwait:
  csrr t0, mcycle
  bltu t0, s9, .Lwait
.global measure_stop
measure_stop:
  la t0, snapshot
  sw a0, 0(t0)
  sw a1, 4(t0)
  sw a2, 8(t0)
  sw a3, 12(t0)
  sw a4, 16(t0)
  sw a5, 20(t0)
  sw a6, 24(t0)
  sw a7, 28(t0)
  la a0, state_label
  call puts
  la s2, snapshot
  li s3, 8
.Lprint_regs:
  lw a0, 0(s2)
  call puthex
  li a0, 32
  call putchar
  addi s2, s2, 4
  addi s3, s3, -1
  bnez s3, .Lprint_regs
  la s2, data_words
  li s3, 64
.Lprint_mem:
  lw a0, 0(s2)
  call puthex
  li a0, 32
  call putchar
  addi s2, s2, 4
  addi s3, s3, -1
  bnez s3, .Lprint_mem
  li a0, 10
  call putchar
  call sim_halt
.Lhalt:
  j .Lhalt
.section .rodata
state_label: .asciz "AGCWS_STATE "
.section .data
.balign 4
data_words:
  .word 3655524816
  .word 2014993289
  .word 374461762
  .word 3028897531
  .word 1388366004
  .word 4042801773
  .word 2402270246
  .word 761738719
  .word 3416174488
  .word 1775642961
  .word 135111434
  .word 2789547203
  .word 1149015676
  .word 3803451445
  .word 2162919918
  .word 522388391
  .word 3176824160
  .word 1536292633
  .word 4190728402
  .word 2550196875
  .word 909665348
  .word 3564101117
  .word 1923569590
  .word 283038063
  .word 2937473832
  .word 1296942305
  .word 3951378074
  .word 2310846547
  .word 670315020
  .word 3324750789
  .word 1684219262
  .word 43687735
  .word 2698123504
  .word 1057591977
  .word 3712027746
  .word 2071496219
  .word 430964692
  .word 3085400461
  .word 1444868934
  .word 4099304703
  .word 2458773176
  .word 818241649
  .word 3472677418
  .word 1832145891
  .word 191614364
  .word 2846050133
  .word 1205518606
  .word 3859954375
  .word 2219422848
  .word 578891321
  .word 3233327090
  .word 1592795563
  .word 4247231332
  .word 2606699805
  .word 966168278
  .word 3620604047
  .word 1980072520
  .word 339540993
  .word 2993976762
  .word 1353445235
  .word 4007881004
  .word 2367349477
  .word 726817950
  .word 3381253719
.section .bss
.balign 4
snapshot: .space 32
