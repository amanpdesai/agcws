.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 3584681151
  li a2, 3102371694
  li a3, 0
  li a4, 1
  li a5, 9260272
  li a6, 1
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 6183
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 16
.Lloop0:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 23923
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 32
.Lloop1:
  sll a5, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 47116
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 346
.Lloop2:
  divu a3, a6, a0
  divu a2, a7, a1
  divu a5, a3, a1
  divu a4, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 63106
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 61
.Lloop3:
  bnez a1, .Lskip3_0
  mv a6, a1
.Lskip3_0:
  bnez a7, .Lskip3_1
  mv a2, a0
.Lskip3_1:
  bnez a7, .Lskip3_2
  mv a4, a1
.Lskip3_2:
  bnez a1, .Lskip3_3
  mv a7, a1
.Lskip3_3:
  bnez a7, .Lskip3_4
  mv a3, a0
.Lskip3_4:
  bnez a5, .Lskip3_5
  mv a6, a0
.Lskip3_5:
  bnez a4, .Lskip3_6
  mv a5, a0
.Lskip3_6:
  bnez a0, .Lskip3_7
  mv a2, a0
.Lskip3_7:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 115652
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 640
.Lloop4:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 122035
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 560
.Lloop5:
  sll a6, a2, a0
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 136559
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 400
.Lloop6:
  divu a6, a4, a1
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
  .word 3153981070
  .word 1513449543
  .word 4167885312
  .word 2527353785
  .word 886822258
  .word 3541258027
  .word 1900726500
  .word 260194973
  .word 2914630742
  .word 1274099215
  .word 3928534984
  .word 2288003457
  .word 647471930
  .word 3301907699
  .word 1661376172
  .word 20844645
  .word 2675280414
  .word 1034748887
  .word 3689184656
  .word 2048653129
  .word 408121602
  .word 3062557371
  .word 1422025844
  .word 4076461613
  .word 2435930086
  .word 795398559
  .word 3449834328
  .word 1809302801
  .word 168771274
  .word 2823207043
  .word 1182675516
  .word 3837111285
  .word 2196579758
  .word 556048231
  .word 3210484000
  .word 1569952473
  .word 4224388242
  .word 2583856715
  .word 943325188
  .word 3597760957
  .word 1957229430
  .word 316697903
  .word 2971133672
  .word 1330602145
  .word 3985037914
  .word 2344506387
  .word 703974860
  .word 3358410629
  .word 1717879102
  .word 77347575
  .word 2731783344
  .word 1091251817
  .word 3745687586
  .word 2105156059
  .word 464624532
  .word 3119060301
  .word 1478528774
  .word 4132964543
  .word 2492433016
  .word 851901489
  .word 3506337258
  .word 1865805731
  .word 225274204
  .word 2879709973
.section .bss
.balign 4
snapshot: .space 32
