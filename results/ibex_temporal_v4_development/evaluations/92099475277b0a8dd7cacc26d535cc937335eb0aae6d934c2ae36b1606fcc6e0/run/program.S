.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 3597095772
  li a2, 2603784974
  li a3, 4098290256
  li a4, 1
  li a5, 3382691666
  li a6, 31
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 3864
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 84
.Lloop0:
  divu a4, a6, a6
  divu a7, a0, a3
  divu a2, a7, a1
  divu a7, a2, a4
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 9915
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 328
.Lloop1:
  bnez a5, .Lskip1_0
  mv a4, a0
.Lskip1_0:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 47811
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 148
.Lloop2:
  divu a3, a0, a0
  divu a2, a3, a1
  divu a2, a3, a1
  divu a5, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 69422
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 544
.Lloop3:
  divu a1, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 94410
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 32
.Lloop4:
  divu a4, a4, a7
  divu a4, a6, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 130266
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 76
.Lloop5:
  divu a7, a1, a0
  divu a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 171756
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 1040
.Lloop6:
  add a7, a0, a0
  add a2, a1, a0
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
  .word 2567679106
  .word 927147579
  .word 3581583348
  .word 1941051821
  .word 300520294
  .word 2954956063
  .word 1314424536
  .word 3968860305
  .word 2328328778
  .word 687797251
  .word 3342233020
  .word 1701701493
  .word 61169966
  .word 2715605735
  .word 1075074208
  .word 3729509977
  .word 2088978450
  .word 448446923
  .word 3102882692
  .word 1462351165
  .word 4116786934
  .word 2476255407
  .word 835723880
  .word 3490159649
  .word 1849628122
  .word 209096595
  .word 2863532364
  .word 1223000837
  .word 3877436606
  .word 2236905079
  .word 596373552
  .word 3250809321
  .word 1610277794
  .word 4264713563
  .word 2624182036
  .word 983650509
  .word 3638086278
  .word 1997554751
  .word 357023224
  .word 3011458993
  .word 1370927466
  .word 4025363235
  .word 2384831708
  .word 744300181
  .word 3398735950
  .word 1758204423
  .word 117672896
  .word 2772108665
  .word 1131577138
  .word 3786012907
  .word 2145481380
  .word 504949853
  .word 3159385622
  .word 1518854095
  .word 4173289864
  .word 2532758337
  .word 892226810
  .word 3546662579
  .word 1906131052
  .word 265599525
  .word 2920035294
  .word 1279503767
  .word 3933939536
  .word 2293408009
.section .bss
.balign 4
snapshot: .space 32
