.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 31
  li a3, 31
  li a4, 17
  li a5, 17
  li a6, 31
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 35167
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 50
.Lloop0:
  mul a1, a2, a4
  mul a0, a5, a2
  mul a4, a0, a3
  mul a2, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 106915
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 416
.Lloop1:
  bnez a4, .Lskip1_0
  mv a5, a1
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a6, a0
.Lskip1_1:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 122338
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 984
.Lloop2:
  mul a3, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 149804
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 106
.Lloop3:
  bnez a7, .Lskip3_0
  mv a7, a0
.Lskip3_0:
  bnez a5, .Lskip3_1
  mv a7, a1
.Lskip3_1:
  bnez a3, .Lskip3_2
  mv a3, a0
.Lskip3_2:
  bnez a7, .Lskip3_3
  mv a7, a0
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 158773
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 132
.Lloop4:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 169595
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 348
.Lloop5:
  srl a1, a6, a5
  xor a3, a3, a4
  sll a1, a6, a3
  and a1, a7, a4
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
  .word 3512990835
  .word 1872459308
  .word 231927781
  .word 2886363550
  .word 1245832023
  .word 3900267792
  .word 2259736265
  .word 619204738
  .word 3273640507
  .word 1633108980
  .word 4287544749
  .word 2647013222
  .word 1006481695
  .word 3660917464
  .word 2020385937
  .word 379854410
  .word 3034290179
  .word 1393758652
  .word 4048194421
  .word 2407662894
  .word 767131367
  .word 3421567136
  .word 1781035609
  .word 140504082
  .word 2794939851
  .word 1154408324
  .word 3808844093
  .word 2168312566
  .word 527781039
  .word 3182216808
  .word 1541685281
  .word 4196121050
  .word 2555589523
  .word 915057996
  .word 3569493765
  .word 1928962238
  .word 288430711
  .word 2942866480
  .word 1302334953
  .word 3956770722
  .word 2316239195
  .word 675707668
  .word 3330143437
  .word 1689611910
  .word 49080383
  .word 2703516152
  .word 1062984625
  .word 3717420394
  .word 2076888867
  .word 436357340
  .word 3090793109
  .word 1450261582
  .word 4104697351
  .word 2464165824
  .word 823634297
  .word 3478070066
  .word 1837538539
  .word 197007012
  .word 2851442781
  .word 1210911254
  .word 3865347023
  .word 2224815496
  .word 584283969
  .word 3238719738
.section .bss
.balign 4
snapshot: .space 32
