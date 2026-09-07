.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 10000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 192
.Lloop0:
  add a0, a0, a1
  xor a1, a2, a3
  sll a2, a4, a5
  mul a3, a6, a7
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
  li t6, 192
.Lloop1:
  and a4, a0, a1
  or a5, a2, a3
  srl a6, a4, a5
  divu a7, a6, a7
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
  li t6, 213
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  bnez a2, .Lskip2_2
  mv a2, a3
.Lskip2_2:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  add a5, a5, a4
  bnez a6, .Lskip2_5
  mv a6, a7
.Lskip2_5:
  addi t6, t6, -1
  bnez t6, .Lloop2
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
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
  li t6, 160
.Lloop3:
  add a0, a0, a1
  xor a1, a0, a1
  mul a2, a1, a2
  sll a3, a2, a3
  srl a4, a3, a4
  and a5, a4, a5
  or a6, a5, a6
  bnez a6, .Lskip3_7
  mv a7, a7
.Lskip3_7:
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
  .word 735735735
  .word 3390171504
  .word 1749639977
  .word 109108450
  .word 2763544219
  .word 1123012692
  .word 3777448461
  .word 2136916934
  .word 496385407
  .word 3150821176
  .word 1510289649
  .word 4164725418
  .word 2524193891
  .word 883662364
  .word 3538098133
  .word 1897566606
  .word 257035079
  .word 2911470848
  .word 1270939321
  .word 3925375090
  .word 2284843563
  .word 644312036
  .word 3298747805
  .word 1658216278
  .word 17684751
  .word 2672120520
  .word 1031588993
  .word 3686024762
  .word 2045493235
  .word 404961708
  .word 3059397477
  .word 1418865950
  .word 4073301719
  .word 2432770192
  .word 792238665
  .word 3446674434
  .word 1806142907
  .word 165611380
  .word 2820047149
  .word 1179515622
  .word 3833951391
  .word 2193419864
  .word 552888337
  .word 3207324106
  .word 1566792579
  .word 4221228348
  .word 2580696821
  .word 940165294
  .word 3594601063
  .word 1954069536
  .word 313538009
  .word 2967973778
  .word 1327442251
  .word 3981878020
  .word 2341346493
  .word 700814966
  .word 3355250735
  .word 1714719208
  .word 74187681
  .word 2728623450
  .word 1088091923
  .word 3742527692
  .word 2101996165
  .word 461464638
.section .bss
.balign 4
snapshot: .space 32
