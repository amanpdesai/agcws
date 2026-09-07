.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 1
  li a2, 31
  li a3, 1374255437
  li a4, 4294967295
  li a5, 17
  li a6, 0
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 21446
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 32
.Lloop0:
  sll a5, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 46821
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 16
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 68320
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 121
.Lloop2:
  divu a0, a1, a4
  divu a5, a6, a7
  divu a5, a6, a4
  divu a7, a5, a7
  divu a6, a3, a7
  divu a3, a1, a7
  divu a3, a4, a4
  divu a5, a3, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 87016
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 36
.Lloop3:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 114071
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 332
.Lloop4:
  add a7, a7, a2
  srl a0, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 126818
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 812
.Lloop5:
  and a2, a0, a0
  bnez a2, .Lskip5_1
  mv a3, a1
.Lskip5_1:
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 161399
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 184
.Lloop6:
  divu a2, a3, a0
  divu a4, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop6
.global agcws_segment_7_setup
agcws_segment_7_setup:
  li s9, 176295
  add s9, s9, s10
.global agcws_segment_7_poll
agcws_segment_7_poll:
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
.global agcws_segment_7_body
agcws_segment_7_body:
  li t6, 15
.Lloop7:
  divu a6, a6, a0
  divu a7, a6, a0
  divu a3, a0, a0
  divu a6, a3, a1
  divu a3, a6, a0
  divu a5, a0, a0
  divu a7, a3, a0
  divu a3, a5, a0
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
  .word 1480914156
  .word 4135349925
  .word 2494818398
  .word 854286871
  .word 3508722640
  .word 1868191113
  .word 227659586
  .word 2882095355
  .word 1241563828
  .word 3895999597
  .word 2255468070
  .word 614936543
  .word 3269372312
  .word 1628840785
  .word 4283276554
  .word 2642745027
  .word 1002213500
  .word 3656649269
  .word 2016117742
  .word 375586215
  .word 3030021984
  .word 1389490457
  .word 4043926226
  .word 2403394699
  .word 762863172
  .word 3417298941
  .word 1776767414
  .word 136235887
  .word 2790671656
  .word 1150140129
  .word 3804575898
  .word 2164044371
  .word 523512844
  .word 3177948613
  .word 1537417086
  .word 4191852855
  .word 2551321328
  .word 910789801
  .word 3565225570
  .word 1924694043
  .word 284162516
  .word 2938598285
  .word 1298066758
  .word 3952502527
  .word 2311971000
  .word 671439473
  .word 3325875242
  .word 1685343715
  .word 44812188
  .word 2699247957
  .word 1058716430
  .word 3713152199
  .word 2072620672
  .word 432089145
  .word 3086524914
  .word 1445993387
  .word 4100429156
  .word 2459897629
  .word 819366102
  .word 3473801871
  .word 1833270344
  .word 192738817
  .word 2847174586
  .word 1206643059
.section .bss
.balign 4
snapshot: .space 32
