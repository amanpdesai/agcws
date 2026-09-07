.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 1
  li a2, 4294967295
  li a3, 1
  li a4, 1
  li a5, 3072610141
  li a6, 17
  li a7, 464496524
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 17887
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 144
.Lloop0:
  srl a7, a0, a0
  sll a2, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 28997
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 72
.Lloop1:
  add a3, a6, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 51288
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 464
.Lloop2:
  add a6, a6, a3
  sll a5, a2, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 126603
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 60
.Lloop3:
  divu a6, a7, a1
  divu a2, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 132028
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 114
.Lloop4:
  mul a6, a1, a5
  mul a0, a7, a7
  mul a3, a0, a2
  mul a2, a4, a2
  mul a2, a1, a0
  mul a0, a0, a3
  mul a2, a3, a3
  mul a6, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 151099
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 428
.Lloop5:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 153338
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 230
.Lloop6:
  mul a1, a5, a0
  mul a1, a6, a0
  mul a3, a0, a3
  mul a2, a4, a2
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
  .word 430428152
  .word 3084863921
  .word 1444332394
  .word 4098768163
  .word 2458236636
  .word 817705109
  .word 3472140878
  .word 1831609351
  .word 191077824
  .word 2845513593
  .word 1204982066
  .word 3859417835
  .word 2218886308
  .word 578354781
  .word 3232790550
  .word 1592259023
  .word 4246694792
  .word 2606163265
  .word 965631738
  .word 3620067507
  .word 1979535980
  .word 339004453
  .word 2993440222
  .word 1352908695
  .word 4007344464
  .word 2366812937
  .word 726281410
  .word 3380717179
  .word 1740185652
  .word 99654125
  .word 2754089894
  .word 1113558367
  .word 3767994136
  .word 2127462609
  .word 486931082
  .word 3141366851
  .word 1500835324
  .word 4155271093
  .word 2514739566
  .word 874208039
  .word 3528643808
  .word 1888112281
  .word 247580754
  .word 2902016523
  .word 1261484996
  .word 3915920765
  .word 2275389238
  .word 634857711
  .word 3289293480
  .word 1648761953
  .word 8230426
  .word 2662666195
  .word 1022134668
  .word 3676570437
  .word 2036038910
  .word 395507383
  .word 3049943152
  .word 1409411625
  .word 4063847394
  .word 2423315867
  .word 782784340
  .word 3437220109
  .word 1796688582
  .word 156157055
.section .bss
.balign 4
snapshot: .space 32
