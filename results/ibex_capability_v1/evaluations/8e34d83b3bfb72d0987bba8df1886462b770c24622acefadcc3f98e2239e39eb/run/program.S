.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 1
  li a3, 31
  li a4, 0
  li a5, 1803761090
  li a6, 17
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 9562
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 80
.Lloop0:
  mul a6, a5, a1
  mul a7, a6, a1
  mul a4, a2, a0
  mul a2, a1, a0
  mul a7, a5, a0
  mul a4, a1, a0
  mul a4, a5, a1
  mul a6, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 10896
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 106
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 48747
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 162
.Lloop2:
  divu a5, a7, a1
  divu a5, a3, a1
  divu a7, a1, a1
  divu a6, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 53647
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 656
.Lloop3:
  sll a3, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 82214
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 592
.Lloop4:
  bnez a6, .Lskip4_0
  mv a5, a3
.Lskip4_0:
  bnez a5, .Lskip4_1
  mv a5, a3
.Lskip4_1:
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 95019
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
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
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
  .word 4141944560
  .word 2501413033
  .word 860881506
  .word 3515317275
  .word 1874785748
  .word 234254221
  .word 2888689990
  .word 1248158463
  .word 3902594232
  .word 2262062705
  .word 621531178
  .word 3275966947
  .word 1635435420
  .word 4289871189
  .word 2649339662
  .word 1008808135
  .word 3663243904
  .word 2022712377
  .word 382180850
  .word 3036616619
  .word 1396085092
  .word 4050520861
  .word 2409989334
  .word 769457807
  .word 3423893576
  .word 1783362049
  .word 142830522
  .word 2797266291
  .word 1156734764
  .word 3811170533
  .word 2170639006
  .word 530107479
  .word 3184543248
  .word 1544011721
  .word 4198447490
  .word 2557915963
  .word 917384436
  .word 3571820205
  .word 1931288678
  .word 290757151
  .word 2945192920
  .word 1304661393
  .word 3959097162
  .word 2318565635
  .word 678034108
  .word 3332469877
  .word 1691938350
  .word 51406823
  .word 2705842592
  .word 1065311065
  .word 3719746834
  .word 2079215307
  .word 438683780
  .word 3093119549
  .word 1452588022
  .word 4107023791
  .word 2466492264
  .word 825960737
  .word 3480396506
  .word 1839864979
  .word 199333452
  .word 2853769221
  .word 1213237694
  .word 3867673463
.section .bss
.balign 4
snapshot: .space 32
