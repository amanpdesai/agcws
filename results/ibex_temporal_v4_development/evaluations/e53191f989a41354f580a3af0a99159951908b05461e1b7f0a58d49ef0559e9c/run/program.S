.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 17
  li a2, 17
  li a3, 0
  li a4, 31
  li a5, 1
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 30713
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 232
.Lloop0:
  divu a2, a1, a1
  divu a6, a4, a1
  divu a6, a1, a0
  divu a6, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 64827
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 99
.Lloop1:
  mul a4, a3, a1
  mul a4, a7, a0
  mul a6, a1, a1
  mul a4, a6, a0
  mul a2, a3, a0
  mul a7, a0, a0
  mul a3, a4, a1
  mul a3, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 65496
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 416
.Lloop2:
  srl a2, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 70632
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 5
.Lloop3:
  sll a6, a4, a4
  sll a2, a0, a0
  or a6, a0, a6
  add a3, a5, a3
  and a2, a0, a6
  or a7, a0, a5
  add a7, a7, a3
  and a6, a0, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 106136
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 6
.Lloop4:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 150478
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 296
.Lloop5:
  mul a7, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 177260
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 146
.Lloop6:
  bnez a0, .Lskip6_0
  mv a3, a1
.Lskip6_0:
  bnez a1, .Lskip6_1
  mv a4, a1
.Lskip6_1:
  bnez a2, .Lskip6_2
  mv a3, a1
.Lskip6_2:
  bnez a2, .Lskip6_3
  mv a3, a0
.Lskip6_3:
  bnez a4, .Lskip6_4
  mv a7, a0
.Lskip6_4:
  bnez a3, .Lskip6_5
  mv a5, a1
.Lskip6_5:
  bnez a4, .Lskip6_6
  mv a4, a0
.Lskip6_6:
  bnez a0, .Lskip6_7
  mv a2, a1
.Lskip6_7:
  addi t6, t6, -1
  bnez t6, .Lloop6
.global agcws_segment_7_setup
agcws_segment_7_setup:
  li s9, 177855
  add s9, s9, s10
.global agcws_segment_7_poll
agcws_segment_7_poll:
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
.global agcws_segment_7_body
agcws_segment_7_body:
  li t6, 204
.Lloop7:
  mul a2, a0, a0
  mul a3, a0, a1
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
  .word 3116152389
  .word 1475620862
  .word 4130056631
  .word 2489525104
  .word 848993577
  .word 3503429346
  .word 1862897819
  .word 222366292
  .word 2876802061
  .word 1236270534
  .word 3890706303
  .word 2250174776
  .word 609643249
  .word 3264079018
  .word 1623547491
  .word 4277983260
  .word 2637451733
  .word 996920206
  .word 3651355975
  .word 2010824448
  .word 370292921
  .word 3024728690
  .word 1384197163
  .word 4038632932
  .word 2398101405
  .word 757569878
  .word 3412005647
  .word 1771474120
  .word 130942593
  .word 2785378362
  .word 1144846835
  .word 3799282604
  .word 2158751077
  .word 518219550
  .word 3172655319
  .word 1532123792
  .word 4186559561
  .word 2546028034
  .word 905496507
  .word 3559932276
  .word 1919400749
  .word 278869222
  .word 2933304991
  .word 1292773464
  .word 3947209233
  .word 2306677706
  .word 666146179
  .word 3320581948
  .word 1680050421
  .word 39518894
  .word 2693954663
  .word 1053423136
  .word 3707858905
  .word 2067327378
  .word 426795851
  .word 3081231620
  .word 1440700093
  .word 4095135862
  .word 2454604335
  .word 814072808
  .word 3468508577
  .word 1827977050
  .word 187445523
  .word 2841881292
.section .bss
.balign 4
snapshot: .space 32
