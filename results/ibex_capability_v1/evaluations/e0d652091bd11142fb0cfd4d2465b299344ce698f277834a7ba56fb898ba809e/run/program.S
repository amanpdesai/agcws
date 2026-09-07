.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 4294967295
  li a3, 17
  li a4, 4294967295
  li a5, 1892331356
  li a6, 17
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 25409
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 89
.Lloop0:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 38261
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 880
.Lloop1:
  divu a7, a1, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 47289
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 31
.Lloop2:
  or a3, a1, a4
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  and a7, a5, a7
  bnez a0, .Lskip2_3
  mv a7, a7
.Lskip2_3:
  divu a2, a1, a7
  or a4, a2, a6
  and a7, a0, a6
  bnez a6, .Lskip2_7
  mv a5, a0
.Lskip2_7:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 52830
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 184
.Lloop3:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 63708
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 78
.Lloop4:
  bnez a4, .Lskip4_0
  mv a5, a3
.Lskip4_0:
  bnez a1, .Lskip4_1
  mv a0, a2
.Lskip4_1:
  bnez a2, .Lskip4_2
  mv a3, a5
.Lskip4_2:
  bnez a1, .Lskip4_3
  mv a1, a1
.Lskip4_3:
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 127283
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 336
.Lloop5:
  bnez a3, .Lskip5_0
  mv a7, a7
.Lskip5_0:
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 171465
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 136
.Lloop6:
  or a6, a2, a0
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
  .word 221690189
  .word 2876125958
  .word 1235594431
  .word 3890030200
  .word 2249498673
  .word 608967146
  .word 3263402915
  .word 1622871388
  .word 4277307157
  .word 2636775630
  .word 996244103
  .word 3650679872
  .word 2010148345
  .word 369616818
  .word 3024052587
  .word 1383521060
  .word 4037956829
  .word 2397425302
  .word 756893775
  .word 3411329544
  .word 1770798017
  .word 130266490
  .word 2784702259
  .word 1144170732
  .word 3798606501
  .word 2158074974
  .word 517543447
  .word 3171979216
  .word 1531447689
  .word 4185883458
  .word 2545351931
  .word 904820404
  .word 3559256173
  .word 1918724646
  .word 278193119
  .word 2932628888
  .word 1292097361
  .word 3946533130
  .word 2306001603
  .word 665470076
  .word 3319905845
  .word 1679374318
  .word 38842791
  .word 2693278560
  .word 1052747033
  .word 3707182802
  .word 2066651275
  .word 426119748
  .word 3080555517
  .word 1440023990
  .word 4094459759
  .word 2453928232
  .word 813396705
  .word 3467832474
  .word 1827300947
  .word 186769420
  .word 2841205189
  .word 1200673662
  .word 3855109431
  .word 2214577904
  .word 574046377
  .word 3228482146
  .word 1587950619
  .word 4242386388
.section .bss
.balign 4
snapshot: .space 32
