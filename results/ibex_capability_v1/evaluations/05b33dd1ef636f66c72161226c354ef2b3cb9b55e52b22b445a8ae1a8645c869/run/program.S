.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 17
  li a2, 2407234899
  li a3, 0
  li a4, 4294967295
  li a5, 17
  li a6, 1
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 8221
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 360
.Lloop0:
  add a6, a7, a2
  or a7, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 35562
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 144
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 65770
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 92
.Lloop2:
  srl a5, a1, a0
  sll a3, a4, a1
  xor a5, a6, a1
  sll a4, a3, a1
  bnez a7, .Lskip2_4
  mv a4, a0
.Lskip2_4:
  bnez a1, .Lskip2_5
  mv a3, a1
.Lskip2_5:
  mul a5, a3, a0
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 75976
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 216
.Lloop3:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  and a3, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 86436
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 49
.Lloop4:
  mul a4, a3, a5
  mul a1, a4, a3
  mul a6, a0, a7
  mul a6, a3, a1
  mul a1, a0, a5
  mul a0, a4, a6
  mul a5, a6, a5
  mul a0, a0, a3
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 99461
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 135
.Lloop5:
  bnez a1, .Lskip5_0
  mv a5, a1
.Lskip5_0:
  bnez a3, .Lskip5_1
  mv a3, a1
.Lskip5_1:
  bnez a7, .Lskip5_2
  mv a5, a1
.Lskip5_2:
  bnez a3, .Lskip5_3
  mv a2, a0
.Lskip5_3:
  bnez a3, .Lskip5_4
  mv a5, a1
.Lskip5_4:
  bnez a5, .Lskip5_5
  mv a4, a1
.Lskip5_5:
  bnez a7, .Lskip5_6
  mv a5, a1
.Lskip5_6:
  bnez a4, .Lskip5_7
  mv a5, a1
.Lskip5_7:
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 131772
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
  and a2, a7, a7
  srl a3, a7, a6
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  srl a5, a4, a0
  bnez a7, .Lskip6_5
  mv a7, a6
.Lskip6_5:
  srl a5, a3, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
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
  .word 3730324207
  .word 2089792680
  .word 449261153
  .word 3103696922
  .word 1463165395
  .word 4117601164
  .word 2477069637
  .word 836538110
  .word 3490973879
  .word 1850442352
  .word 209910825
  .word 2864346594
  .word 1223815067
  .word 3878250836
  .word 2237719309
  .word 597187782
  .word 3251623551
  .word 1611092024
  .word 4265527793
  .word 2624996266
  .word 984464739
  .word 3638900508
  .word 1998368981
  .word 357837454
  .word 3012273223
  .word 1371741696
  .word 4026177465
  .word 2385645938
  .word 745114411
  .word 3399550180
  .word 1759018653
  .word 118487126
  .word 2772922895
  .word 1132391368
  .word 3786827137
  .word 2146295610
  .word 505764083
  .word 3160199852
  .word 1519668325
  .word 4174104094
  .word 2533572567
  .word 893041040
  .word 3547476809
  .word 1906945282
  .word 266413755
  .word 2920849524
  .word 1280317997
  .word 3934753766
  .word 2294222239
  .word 653690712
  .word 3308126481
  .word 1667594954
  .word 27063427
  .word 2681499196
  .word 1040967669
  .word 3695403438
  .word 2054871911
  .word 414340384
  .word 3068776153
  .word 1428244626
  .word 4082680395
  .word 2442148868
  .word 801617341
  .word 3456053110
.section .bss
.balign 4
snapshot: .space 32
