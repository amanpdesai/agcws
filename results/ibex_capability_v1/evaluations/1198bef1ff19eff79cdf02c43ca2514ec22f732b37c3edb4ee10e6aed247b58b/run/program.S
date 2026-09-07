.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 17
  li a2, 17
  li a3, 17
  li a4, 4294967295
  li a5, 31
  li a6, 1
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 13857
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 100
.Lloop0:
  mul a5, a6, a0
  mul a2, a3, a0
  mul a7, a7, a0
  mul a7, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 47517
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 376
.Lloop1:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  xor a7, a2, a7
  bnez a6, .Lskip1_2
  mv a0, a6
.Lskip1_2:
  or a5, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 99957
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
  or a3, a3, a4
  add a7, a4, a0
  xor a7, a0, a5
  srl a7, a4, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 105555
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 16
.Lloop3:
  mul a7, a7, a1
  xor a7, a5, a1
  divu a2, a6, a1
  srl a7, a7, a0
  srl a3, a1, a0
  or a5, a6, a1
  sll a7, a2, a0
  sll a3, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 152384
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 444
.Lloop4:
  bnez a1, .Lskip4_0
  mv a2, a7
.Lskip4_0:
  bnez a6, .Lskip4_1
  mv a3, a4
.Lskip4_1:
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 159590
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 72
.Lloop5:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 179125
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 168
.Lloop6:
  divu a2, a1, a0
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
  .word 234785687
  .word 2889221456
  .word 1248689929
  .word 3903125698
  .word 2262594171
  .word 622062644
  .word 3276498413
  .word 1635966886
  .word 4290402655
  .word 2649871128
  .word 1009339601
  .word 3663775370
  .word 2023243843
  .word 382712316
  .word 3037148085
  .word 1396616558
  .word 4051052327
  .word 2410520800
  .word 769989273
  .word 3424425042
  .word 1783893515
  .word 143361988
  .word 2797797757
  .word 1157266230
  .word 3811701999
  .word 2171170472
  .word 530638945
  .word 3185074714
  .word 1544543187
  .word 4198978956
  .word 2558447429
  .word 917915902
  .word 3572351671
  .word 1931820144
  .word 291288617
  .word 2945724386
  .word 1305192859
  .word 3959628628
  .word 2319097101
  .word 678565574
  .word 3333001343
  .word 1692469816
  .word 51938289
  .word 2706374058
  .word 1065842531
  .word 3720278300
  .word 2079746773
  .word 439215246
  .word 3093651015
  .word 1453119488
  .word 4107555257
  .word 2467023730
  .word 826492203
  .word 3480927972
  .word 1840396445
  .word 199864918
  .word 2854300687
  .word 1213769160
  .word 3868204929
  .word 2227673402
  .word 587141875
  .word 3241577644
  .word 1601046117
  .word 4255481886
.section .bss
.balign 4
snapshot: .space 32
