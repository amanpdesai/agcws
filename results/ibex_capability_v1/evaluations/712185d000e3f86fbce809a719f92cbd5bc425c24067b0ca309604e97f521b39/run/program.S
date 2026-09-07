.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1262128920
  li a2, 1
  li a3, 4294967295
  li a4, 0
  li a5, 31
  li a6, 0
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 69865
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 102
.Lloop0:
  mul a6, a4, a1
  mul a4, a5, a1
  mul a6, a3, a1
  mul a5, a6, a1
  mul a4, a3, a1
  mul a4, a5, a0
  mul a7, a5, a0
  mul a4, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 99516
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 700
.Lloop1:
  mul a2, a2, a4
  mul a5, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 114598
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 87
.Lloop2:
  divu a4, a7, a1
  divu a4, a4, a0
  divu a4, a3, a1
  divu a5, a4, a0
  divu a2, a0, a1
  divu a7, a4, a0
  divu a4, a5, a0
  divu a2, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 135985
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 8
.Lloop3:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 173189
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 288
.Lloop4:
  divu a0, a5, a2
  divu a6, a7, a0
  divu a3, a5, a4
  divu a3, a2, a7
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 125649464
  .word 2780085233
  .word 1139553706
  .word 3793989475
  .word 2153457948
  .word 512926421
  .word 3167362190
  .word 1526830663
  .word 4181266432
  .word 2540734905
  .word 900203378
  .word 3554639147
  .word 1914107620
  .word 273576093
  .word 2928011862
  .word 1287480335
  .word 3941916104
  .word 2301384577
  .word 660853050
  .word 3315288819
  .word 1674757292
  .word 34225765
  .word 2688661534
  .word 1048130007
  .word 3702565776
  .word 2062034249
  .word 421502722
  .word 3075938491
  .word 1435406964
  .word 4089842733
  .word 2449311206
  .word 808779679
  .word 3463215448
  .word 1822683921
  .word 182152394
  .word 2836588163
  .word 1196056636
  .word 3850492405
  .word 2209960878
  .word 569429351
  .word 3223865120
  .word 1583333593
  .word 4237769362
  .word 2597237835
  .word 956706308
  .word 3611142077
  .word 1970610550
  .word 330079023
  .word 2984514792
  .word 1343983265
  .word 3998419034
  .word 2357887507
  .word 717355980
  .word 3371791749
  .word 1731260222
  .word 90728695
  .word 2745164464
  .word 1104632937
  .word 3759068706
  .word 2118537179
  .word 478005652
  .word 3132441421
  .word 1491909894
  .word 4146345663
.section .bss
.balign 4
snapshot: .space 32
