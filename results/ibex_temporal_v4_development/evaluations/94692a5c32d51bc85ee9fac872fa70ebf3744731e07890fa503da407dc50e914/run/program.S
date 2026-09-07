.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1108300482
  li a1, 978658013
  li a2, 31
  li a3, 1
  li a4, 0
  li a5, 17
  li a6, 17
  li a7, 1765682813
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 5000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 250
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 40000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 250
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  mul a3, a1, a2
  and a5, a3, a4
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 80000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 250
.Lloop2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  add a2, a0, a1
  xor a4, a2, a3
  or a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 120000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 274
.Lloop3:
  add a0, a6, a7
  xor a2, a0, a1
  srl a4, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
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
  .word 1234567
  .word 2655670336
  .word 1015138809
  .word 3669574578
  .word 2029043051
  .word 388511524
  .word 3042947293
  .word 1402415766
  .word 4056851535
  .word 2416320008
  .word 775788481
  .word 3430224250
  .word 1789692723
  .word 149161196
  .word 2803596965
  .word 1163065438
  .word 3817501207
  .word 2176969680
  .word 536438153
  .word 3190873922
  .word 1550342395
  .word 4204778164
  .word 2564246637
  .word 923715110
  .word 3578150879
  .word 1937619352
  .word 297087825
  .word 2951523594
  .word 1310992067
  .word 3965427836
  .word 2324896309
  .word 684364782
  .word 3338800551
  .word 1698269024
  .word 57737497
  .word 2712173266
  .word 1071641739
  .word 3726077508
  .word 2085545981
  .word 445014454
  .word 3099450223
  .word 1458918696
  .word 4113354465
  .word 2472822938
  .word 832291411
  .word 3486727180
  .word 1846195653
  .word 205664126
  .word 2860099895
  .word 1219568368
  .word 3874004137
  .word 2233472610
  .word 592941083
  .word 3247376852
  .word 1606845325
  .word 4261281094
  .word 2620749567
  .word 980218040
  .word 3634653809
  .word 1994122282
  .word 353590755
  .word 3008026524
  .word 1367494997
  .word 4021930766
.section .bss
.balign 4
snapshot: .space 32
