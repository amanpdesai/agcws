.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 31
  li a2, 17
  li a3, 17
  li a4, 17
  li a5, 0
  li a6, 17
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 45302
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 116
.Lloop0:
  divu a6, a3, a0
  sll a3, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 56659
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 61
.Lloop1:
  srl a4, a5, a1
  sll a2, a0, a1
  and a7, a3, a0
  and a5, a3, a0
  add a2, a1, a1
  or a2, a5, a1
  srl a3, a4, a1
  add a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 85388
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 280
.Lloop2:
  srl a6, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 93852
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 102
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a4, a7, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  or a2, a0, a6
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  srl a4, a2, a2
  xor a4, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 103490
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 408
.Lloop4:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 105456
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 71
.Lloop5:
  srl a2, a1, a4
  xor a7, a3, a0
  sll a4, a0, a7
  sll a5, a5, a2
  xor a7, a1, a2
  or a0, a6, a0
  or a7, a1, a2
  and a1, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 175860
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 20
.Lloop6:
  divu a7, a5, a0
  divu a2, a0, a1
  divu a5, a2, a0
  divu a3, a0, a0
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
  .word 2630663762
  .word 990132235
  .word 3644568004
  .word 2004036477
  .word 363504950
  .word 3017940719
  .word 1377409192
  .word 4031844961
  .word 2391313434
  .word 750781907
  .word 3405217676
  .word 1764686149
  .word 124154622
  .word 2778590391
  .word 1138058864
  .word 3792494633
  .word 2151963106
  .word 511431579
  .word 3165867348
  .word 1525335821
  .word 4179771590
  .word 2539240063
  .word 898708536
  .word 3553144305
  .word 1912612778
  .word 272081251
  .word 2926517020
  .word 1285985493
  .word 3940421262
  .word 2299889735
  .word 659358208
  .word 3313793977
  .word 1673262450
  .word 32730923
  .word 2687166692
  .word 1046635165
  .word 3701070934
  .word 2060539407
  .word 420007880
  .word 3074443649
  .word 1433912122
  .word 4088347891
  .word 2447816364
  .word 807284837
  .word 3461720606
  .word 1821189079
  .word 180657552
  .word 2835093321
  .word 1194561794
  .word 3848997563
  .word 2208466036
  .word 567934509
  .word 3222370278
  .word 1581838751
  .word 4236274520
  .word 2595742993
  .word 955211466
  .word 3609647235
  .word 1969115708
  .word 328584181
  .word 2983019950
  .word 1342488423
  .word 3996924192
  .word 2356392665
.section .bss
.balign 4
snapshot: .space 32
