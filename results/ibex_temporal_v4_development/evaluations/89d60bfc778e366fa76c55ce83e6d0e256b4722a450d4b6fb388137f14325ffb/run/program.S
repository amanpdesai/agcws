.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 4294967295
  li a2, 0
  li a3, 0
  li a4, 17
  li a5, 0
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 55519
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 62
.Lloop0:
  add a4, a4, a0
  sll a4, a1, a0
  srl a3, a1, a0
  or a7, a0, a1
  and a6, a7, a1
  sll a6, a3, a1
  and a2, a6, a0
  sll a5, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 84608
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1272
.Lloop1:
  mul a5, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 108148
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 1152
.Lloop2:
  mul a6, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 174745
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 1176
.Lloop3:
  mul a4, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop3
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
  .word 3242618203
  .word 1602086676
  .word 4256522445
  .word 2615990918
  .word 975459391
  .word 3629895160
  .word 1989363633
  .word 348832106
  .word 3003267875
  .word 1362736348
  .word 4017172117
  .word 2376640590
  .word 736109063
  .word 3390544832
  .word 1750013305
  .word 109481778
  .word 2763917547
  .word 1123386020
  .word 3777821789
  .word 2137290262
  .word 496758735
  .word 3151194504
  .word 1510662977
  .word 4165098746
  .word 2524567219
  .word 884035692
  .word 3538471461
  .word 1897939934
  .word 257408407
  .word 2911844176
  .word 1271312649
  .word 3925748418
  .word 2285216891
  .word 644685364
  .word 3299121133
  .word 1658589606
  .word 18058079
  .word 2672493848
  .word 1031962321
  .word 3686398090
  .word 2045866563
  .word 405335036
  .word 3059770805
  .word 1419239278
  .word 4073675047
  .word 2433143520
  .word 792611993
  .word 3447047762
  .word 1806516235
  .word 165984708
  .word 2820420477
  .word 1179888950
  .word 3834324719
  .word 2193793192
  .word 553261665
  .word 3207697434
  .word 1567165907
  .word 4221601676
  .word 2581070149
  .word 940538622
  .word 3594974391
  .word 1954442864
  .word 313911337
  .word 2968347106
.section .bss
.balign 4
snapshot: .space 32
