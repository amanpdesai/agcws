.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 0
  li a2, 31
  li a3, 0
  li a4, 4294967295
  li a5, 2834643072
  li a6, 31
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 35929
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 376
.Lloop0:
  or a5, a0, a0
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  or a5, a3, a0
  divu a3, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 43009
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
  divu a5, a4, a0
  divu a4, a1, a0
  divu a6, a6, a0
  divu a7, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 55605
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 216
.Lloop2:
  bnez a6, .Lskip2_0
  mv a3, a1
.Lskip2_0:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 70239
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 124
.Lloop3:
  sll a0, a3, a7
  and a5, a2, a6
  xor a5, a3, a3
  or a7, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 105369
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 74
.Lloop4:
  divu a7, a1, a0
  divu a5, a7, a1
  divu a4, a7, a0
  divu a2, a1, a0
  divu a7, a1, a1
  divu a2, a1, a0
  divu a2, a6, a1
  divu a3, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 129012
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 248
.Lloop5:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  srl a7, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 136755
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 37
.Lloop6:
  and a7, a5, a3
  bnez a5, .Lskip6_1
  mv a5, a3
.Lskip6_1:
  mul a6, a6, a5
  or a2, a4, a1
  xor a7, a7, a7
  mul a1, a2, a2
  and a5, a7, a0
  xor a3, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop6
.global agcws_segment_7_setup
agcws_segment_7_setup:
  li s9, 145076
  add s9, s9, s10
.global agcws_segment_7_poll
agcws_segment_7_poll:
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
.global agcws_segment_7_body
agcws_segment_7_body:
  li t6, 48
.Lloop7:
  add a5, a3, a1
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
  .word 1468397598
  .word 4122833367
  .word 2482301840
  .word 841770313
  .word 3496206082
  .word 1855674555
  .word 215143028
  .word 2869578797
  .word 1229047270
  .word 3883483039
  .word 2242951512
  .word 602419985
  .word 3256855754
  .word 1616324227
  .word 4270759996
  .word 2630228469
  .word 989696942
  .word 3644132711
  .word 2003601184
  .word 363069657
  .word 3017505426
  .word 1376973899
  .word 4031409668
  .word 2390878141
  .word 750346614
  .word 3404782383
  .word 1764250856
  .word 123719329
  .word 2778155098
  .word 1137623571
  .word 3792059340
  .word 2151527813
  .word 510996286
  .word 3165432055
  .word 1524900528
  .word 4179336297
  .word 2538804770
  .word 898273243
  .word 3552709012
  .word 1912177485
  .word 271645958
  .word 2926081727
  .word 1285550200
  .word 3939985969
  .word 2299454442
  .word 658922915
  .word 3313358684
  .word 1672827157
  .word 32295630
  .word 2686731399
  .word 1046199872
  .word 3700635641
  .word 2060104114
  .word 419572587
  .word 3074008356
  .word 1433476829
  .word 4087912598
  .word 2447381071
  .word 806849544
  .word 3461285313
  .word 1820753786
  .word 180222259
  .word 2834658028
  .word 1194126501
.section .bss
.balign 4
snapshot: .space 32
