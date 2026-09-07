.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 422118591
  li a3, 4294967295
  li a4, 1
  li a5, 0
  li a6, 17
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 83771
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 380
.Lloop0:
  bnez a3, .Lskip0_0
  mv a6, a1
.Lskip0_0:
  bnez a2, .Lskip0_1
  mv a2, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 84982
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
  bnez a7, .Lskip1_0
  mv a5, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a6, a0
.Lskip1_1:
  bnez a6, .Lskip1_2
  mv a4, a0
.Lskip1_2:
  bnez a4, .Lskip1_3
  mv a2, a1
.Lskip1_3:
  bnez a6, .Lskip1_4
  mv a6, a0
.Lskip1_4:
  bnez a7, .Lskip1_5
  mv a2, a1
.Lskip1_5:
  bnez a3, .Lskip1_6
  mv a2, a0
.Lskip1_6:
  bnez a7, .Lskip1_7
  mv a7, a1
.Lskip1_7:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 105835
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 1220
.Lloop2:
  bnez a2, .Lskip2_0
  mv a7, a3
.Lskip2_0:
  bnez a5, .Lskip2_1
  mv a4, a1
.Lskip2_1:
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 1715344686
  .word 74813159
  .word 2729248928
  .word 1088717401
  .word 3743153170
  .word 2102621643
  .word 462090116
  .word 3116525885
  .word 1475994358
  .word 4130430127
  .word 2489898600
  .word 849367073
  .word 3503802842
  .word 1863271315
  .word 222739788
  .word 2877175557
  .word 1236644030
  .word 3891079799
  .word 2250548272
  .word 610016745
  .word 3264452514
  .word 1623920987
  .word 4278356756
  .word 2637825229
  .word 997293702
  .word 3651729471
  .word 2011197944
  .word 370666417
  .word 3025102186
  .word 1384570659
  .word 4039006428
  .word 2398474901
  .word 757943374
  .word 3412379143
  .word 1771847616
  .word 131316089
  .word 2785751858
  .word 1145220331
  .word 3799656100
  .word 2159124573
  .word 518593046
  .word 3173028815
  .word 1532497288
  .word 4186933057
  .word 2546401530
  .word 905870003
  .word 3560305772
  .word 1919774245
  .word 279242718
  .word 2933678487
  .word 1293146960
  .word 3947582729
  .word 2307051202
  .word 666519675
  .word 3320955444
  .word 1680423917
  .word 39892390
  .word 2694328159
  .word 1053796632
  .word 3708232401
  .word 2067700874
  .word 427169347
  .word 3081605116
  .word 1441073589
.section .bss
.balign 4
snapshot: .space 32
