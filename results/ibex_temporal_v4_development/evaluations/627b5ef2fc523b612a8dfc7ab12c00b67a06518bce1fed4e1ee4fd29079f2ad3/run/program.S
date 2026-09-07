.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 17
  li a2, 31
  li a3, 4294967295
  li a4, 3711298540
  li a5, 0
  li a6, 31
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 37940
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 768
.Lloop0:
  mul a7, a5, a0
  mul a6, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 59780
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 328
.Lloop1:
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 63551
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 66
.Lloop2:
  add a4, a0, a1
  xor a4, a1, a0
  srl a6, a5, a0
  or a2, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 67459
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 42
.Lloop3:
  bnez a7, .Lskip3_0
  mv a6, a0
.Lskip3_0:
  bnez a0, .Lskip3_1
  mv a4, a1
.Lskip3_1:
  bnez a0, .Lskip3_2
  mv a6, a0
.Lskip3_2:
  bnez a6, .Lskip3_3
  mv a5, a1
.Lskip3_3:
  bnez a4, .Lskip3_4
  mv a2, a0
.Lskip3_4:
  bnez a6, .Lskip3_5
  mv a4, a0
.Lskip3_5:
  bnez a3, .Lskip3_6
  mv a4, a1
.Lskip3_6:
  bnez a2, .Lskip3_7
  mv a6, a0
.Lskip3_7:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 70693
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 95
.Lloop4:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 133467
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 60
.Lloop5:
  add a3, a3, a2
  sll a3, a5, a5
  mul a5, a3, a4
  bnez a1, .Lskip5_3
  mv a7, a5
.Lskip5_3:
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 139880
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 592
.Lloop6:
  sll a7, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop6
.global agcws_segment_7_setup
agcws_segment_7_setup:
  li s9, 155393
  add s9, s9, s10
.global agcws_segment_7_poll
agcws_segment_7_poll:
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
.global agcws_segment_7_body
agcws_segment_7_body:
  li t6, 40
.Lloop7:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 491914751
  .word 3146350520
  .word 1505818993
  .word 4160254762
  .word 2519723235
  .word 879191708
  .word 3533627477
  .word 1893095950
  .word 252564423
  .word 2907000192
  .word 1266468665
  .word 3920904434
  .word 2280372907
  .word 639841380
  .word 3294277149
  .word 1653745622
  .word 13214095
  .word 2667649864
  .word 1027118337
  .word 3681554106
  .word 2041022579
  .word 400491052
  .word 3054926821
  .word 1414395294
  .word 4068831063
  .word 2428299536
  .word 787768009
  .word 3442203778
  .word 1801672251
  .word 161140724
  .word 2815576493
  .word 1175044966
  .word 3829480735
  .word 2188949208
  .word 548417681
  .word 3202853450
  .word 1562321923
  .word 4216757692
  .word 2576226165
  .word 935694638
  .word 3590130407
  .word 1949598880
  .word 309067353
  .word 2963503122
  .word 1322971595
  .word 3977407364
  .word 2336875837
  .word 696344310
  .word 3350780079
  .word 1710248552
  .word 69717025
  .word 2724152794
  .word 1083621267
  .word 3738057036
  .word 2097525509
  .word 456993982
  .word 3111429751
  .word 1470898224
  .word 4125333993
  .word 2484802466
  .word 844270939
  .word 3498706708
  .word 1858175181
  .word 217643654
.section .bss
.balign 4
snapshot: .space 32
