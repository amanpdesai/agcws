.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 17
  li a2, 31
  li a3, 17
  li a4, 1
  li a5, 1
  li a6, 4294967295
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 6191
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 56
.Lloop0:
  sll a0, a4, a4
  sll a7, a5, a1
  add a1, a5, a5
  srl a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 36149
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 25
.Lloop1:
  sll a3, a7, a7
  srl a6, a3, a1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  mul a0, a3, a5
  or a5, a7, a1
  add a1, a0, a7
  sll a1, a6, a5
  mul a5, a5, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 45823
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 232
.Lloop2:
  divu a6, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 126709
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 2200
.Lloop3:
  bnez a1, .Lskip3_0
  mv a4, a5
.Lskip3_0:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 134135
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 112
.Lloop4:
  divu a0, a2, a3
  divu a6, a2, a1
  divu a3, a1, a1
  divu a0, a4, a7
  divu a2, a5, a2
  divu a6, a7, a1
  divu a5, a3, a4
  divu a0, a2, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 148674
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 144
.Lloop5:
  and a6, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 166736
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 100
.Lloop6:
  bnez a2, .Lskip6_0
  mv a1, a1
.Lskip6_0:
  bnez a1, .Lskip6_1
  mv a1, a3
.Lskip6_1:
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
  .word 1454175950
  .word 4108611719
  .word 2468080192
  .word 827548665
  .word 3481984434
  .word 1841452907
  .word 200921380
  .word 2855357149
  .word 1214825622
  .word 3869261391
  .word 2228729864
  .word 588198337
  .word 3242634106
  .word 1602102579
  .word 4256538348
  .word 2616006821
  .word 975475294
  .word 3629911063
  .word 1989379536
  .word 348848009
  .word 3003283778
  .word 1362752251
  .word 4017188020
  .word 2376656493
  .word 736124966
  .word 3390560735
  .word 1750029208
  .word 109497681
  .word 2763933450
  .word 1123401923
  .word 3777837692
  .word 2137306165
  .word 496774638
  .word 3151210407
  .word 1510678880
  .word 4165114649
  .word 2524583122
  .word 884051595
  .word 3538487364
  .word 1897955837
  .word 257424310
  .word 2911860079
  .word 1271328552
  .word 3925764321
  .word 2285232794
  .word 644701267
  .word 3299137036
  .word 1658605509
  .word 18073982
  .word 2672509751
  .word 1031978224
  .word 3686413993
  .word 2045882466
  .word 405350939
  .word 3059786708
  .word 1419255181
  .word 4073690950
  .word 2433159423
  .word 792627896
  .word 3447063665
  .word 1806532138
  .word 166000611
  .word 2820436380
  .word 1179904853
.section .bss
.balign 4
snapshot: .space 32
