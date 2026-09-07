.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 0
  li a2, 31
  li a3, 17
  li a4, 1
  li a5, 17
  li a6, 4294967295
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 3546
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 117
.Lloop0:
  divu a5, a7, a0
  mul a5, a3, a1
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  mul a5, a6, a0
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  mul a3, a0, a1
  and a6, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 51275
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 112
.Lloop1:
  divu a3, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 69343
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 60
.Lloop2:
  divu a3, a1, a1
  divu a6, a6, a0
  divu a3, a3, a1
  divu a3, a0, a1
  divu a6, a4, a0
  divu a5, a0, a1
  divu a4, a7, a1
  divu a7, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 85369
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 212
.Lloop3:
  divu a6, a4, a7
  divu a6, a4, a3
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 119436
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 56
.Lloop4:
  divu a0, a2, a1
  divu a4, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 171501
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 254
.Lloop5:
  sll a6, a2, a0
  xor a4, a1, a0
  add a2, a4, a1
  and a5, a2, a1
  add a3, a7, a1
  or a5, a2, a1
  and a3, a7, a1
  sll a5, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 3576383773
  .word 1935852246
  .word 295320719
  .word 2949756488
  .word 1309224961
  .word 3963660730
  .word 2323129203
  .word 682597676
  .word 3337033445
  .word 1696501918
  .word 55970391
  .word 2710406160
  .word 1069874633
  .word 3724310402
  .word 2083778875
  .word 443247348
  .word 3097683117
  .word 1457151590
  .word 4111587359
  .word 2471055832
  .word 830524305
  .word 3484960074
  .word 1844428547
  .word 203897020
  .word 2858332789
  .word 1217801262
  .word 3872237031
  .word 2231705504
  .word 591173977
  .word 3245609746
  .word 1605078219
  .word 4259513988
  .word 2618982461
  .word 978450934
  .word 3632886703
  .word 1992355176
  .word 351823649
  .word 3006259418
  .word 1365727891
  .word 4020163660
  .word 2379632133
  .word 739100606
  .word 3393536375
  .word 1753004848
  .word 112473321
  .word 2766909090
  .word 1126377563
  .word 3780813332
  .word 2140281805
  .word 499750278
  .word 3154186047
  .word 1513654520
  .word 4168090289
  .word 2527558762
  .word 887027235
  .word 3541463004
  .word 1900931477
  .word 260399950
  .word 2914835719
  .word 1274304192
  .word 3928739961
  .word 2288208434
  .word 647676907
  .word 3302112676
.section .bss
.balign 4
snapshot: .space 32
