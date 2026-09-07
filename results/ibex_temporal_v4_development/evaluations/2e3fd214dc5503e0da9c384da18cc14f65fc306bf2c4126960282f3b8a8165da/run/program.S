.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 4032293290
  li a3, 0
  li a4, 0
  li a5, 1
  li a6, 3024829961
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 155362
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 426
.Lloop0:
  bnez a3, .Lskip0_0
  mv a4, a0
.Lskip0_0:
  bnez a7, .Lskip0_1
  mv a6, a2
.Lskip0_1:
  bnez a7, .Lskip0_2
  mv a3, a2
.Lskip0_2:
  bnez a3, .Lskip0_3
  mv a7, a1
.Lskip0_3:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 90063
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 299
.Lloop1:
  bnez a5, .Lskip1_0
  mv a3, a1
.Lskip1_0:
  bnez a6, .Lskip1_1
  mv a3, a1
.Lskip1_1:
  bnez a5, .Lskip1_2
  mv a6, a0
.Lskip1_2:
  bnez a4, .Lskip1_3
  mv a7, a1
.Lskip1_3:
  bnez a3, .Lskip1_4
  mv a6, a1
.Lskip1_4:
  bnez a1, .Lskip1_5
  mv a7, a0
.Lskip1_5:
  bnez a0, .Lskip1_6
  mv a5, a1
.Lskip1_6:
  bnez a1, .Lskip1_7
  mv a2, a0
.Lskip1_7:
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 1079568696
  .word 3734004465
  .word 2093472938
  .word 452941411
  .word 3107377180
  .word 1466845653
  .word 4121281422
  .word 2480749895
  .word 840218368
  .word 3494654137
  .word 1854122610
  .word 213591083
  .word 2868026852
  .word 1227495325
  .word 3881931094
  .word 2241399567
  .word 600868040
  .word 3255303809
  .word 1614772282
  .word 4269208051
  .word 2628676524
  .word 988144997
  .word 3642580766
  .word 2002049239
  .word 361517712
  .word 3015953481
  .word 1375421954
  .word 4029857723
  .word 2389326196
  .word 748794669
  .word 3403230438
  .word 1762698911
  .word 122167384
  .word 2776603153
  .word 1136071626
  .word 3790507395
  .word 2149975868
  .word 509444341
  .word 3163880110
  .word 1523348583
  .word 4177784352
  .word 2537252825
  .word 896721298
  .word 3551157067
  .word 1910625540
  .word 270094013
  .word 2924529782
  .word 1283998255
  .word 3938434024
  .word 2297902497
  .word 657370970
  .word 3311806739
  .word 1671275212
  .word 30743685
  .word 2685179454
  .word 1044647927
  .word 3699083696
  .word 2058552169
  .word 418020642
  .word 3072456411
  .word 1431924884
  .word 4086360653
  .word 2445829126
  .word 805297599
.section .bss
.balign 4
snapshot: .space 32
