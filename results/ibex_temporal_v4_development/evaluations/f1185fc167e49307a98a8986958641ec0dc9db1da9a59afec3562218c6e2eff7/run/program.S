.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 63277335
  li a1, 1
  li a2, 17
  li a3, 4294967295
  li a4, 4294967295
  li a5, 0
  li a6, 4294967295
  li a7, 1932311505
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 84523
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 228
.Lloop0:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 88116
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1712
.Lloop1:
  divu a5, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 132573
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 168
.Lloop2:
  divu a4, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 178368
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 49
.Lloop3:
  mul a4, a4, a2
  mul a4, a5, a5
  mul a5, a1, a3
  mul a3, a7, a2
  mul a6, a1, a0
  mul a7, a7, a1
  mul a3, a2, a3
  mul a6, a3, a5
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
  .word 3953074411
  .word 2312542884
  .word 672011357
  .word 3326447126
  .word 1685915599
  .word 45384072
  .word 2699819841
  .word 1059288314
  .word 3713724083
  .word 2073192556
  .word 432661029
  .word 3087096798
  .word 1446565271
  .word 4101001040
  .word 2460469513
  .word 819937986
  .word 3474373755
  .word 1833842228
  .word 193310701
  .word 2847746470
  .word 1207214943
  .word 3861650712
  .word 2221119185
  .word 580587658
  .word 3235023427
  .word 1594491900
  .word 4248927669
  .word 2608396142
  .word 967864615
  .word 3622300384
  .word 1981768857
  .word 341237330
  .word 2995673099
  .word 1355141572
  .word 4009577341
  .word 2369045814
  .word 728514287
  .word 3382950056
  .word 1742418529
  .word 101887002
  .word 2756322771
  .word 1115791244
  .word 3770227013
  .word 2129695486
  .word 489163959
  .word 3143599728
  .word 1503068201
  .word 4157503970
  .word 2516972443
  .word 876440916
  .word 3530876685
  .word 1890345158
  .word 249813631
  .word 2904249400
  .word 1263717873
  .word 3918153642
  .word 2277622115
  .word 637090588
  .word 3291526357
  .word 1650994830
  .word 10463303
  .word 2664899072
  .word 1024367545
  .word 3678803314
.section .bss
.balign 4
snapshot: .space 32
