.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 17
  li a2, 4294967295
  li a3, 0
  li a4, 31
  li a5, 31
  li a6, 17
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 30483
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 328
.Lloop0:
  bnez a1, .Lskip0_0
  mv a5, a1
.Lskip0_0:
  bnez a4, .Lskip0_1
  mv a4, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 84526
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
  xor a4, a0, a0
  and a4, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 104132
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 290
.Lloop2:
  divu a2, a5, a1
  or a6, a4, a1
  and a2, a7, a1
  add a6, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 130545
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 944
.Lloop3:
  and a4, a2, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 139478
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
  mul a3, a7, a1
  mul a6, a4, a0
  mul a4, a5, a1
  mul a5, a0, a1
  mul a2, a1, a0
  mul a3, a0, a1
  mul a4, a3, a1
  mul a4, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 157922
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 19
.Lloop5:
  mul a5, a6, a4
  mul a4, a2, a4
  mul a5, a2, a1
  mul a1, a6, a5
  mul a4, a7, a4
  mul a4, a1, a4
  mul a4, a5, a7
  mul a2, a5, a7
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
  .word 1854400092
  .word 213868565
  .word 2868304334
  .word 1227772807
  .word 3882208576
  .word 2241677049
  .word 601145522
  .word 3255581291
  .word 1615049764
  .word 4269485533
  .word 2628954006
  .word 988422479
  .word 3642858248
  .word 2002326721
  .word 361795194
  .word 3016230963
  .word 1375699436
  .word 4030135205
  .word 2389603678
  .word 749072151
  .word 3403507920
  .word 1762976393
  .word 122444866
  .word 2776880635
  .word 1136349108
  .word 3790784877
  .word 2150253350
  .word 509721823
  .word 3164157592
  .word 1523626065
  .word 4178061834
  .word 2537530307
  .word 896998780
  .word 3551434549
  .word 1910903022
  .word 270371495
  .word 2924807264
  .word 1284275737
  .word 3938711506
  .word 2298179979
  .word 657648452
  .word 3312084221
  .word 1671552694
  .word 31021167
  .word 2685456936
  .word 1044925409
  .word 3699361178
  .word 2058829651
  .word 418298124
  .word 3072733893
  .word 1432202366
  .word 4086638135
  .word 2446106608
  .word 805575081
  .word 3460010850
  .word 1819479323
  .word 178947796
  .word 2833383565
  .word 1192852038
  .word 3847287807
  .word 2206756280
  .word 566224753
  .word 3220660522
  .word 1580128995
.section .bss
.balign 4
snapshot: .space 32
