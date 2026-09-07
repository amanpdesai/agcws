.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
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
  li t6, 200
.Lloop0:
  add a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  mul a5, a3, a4
  xor a7, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30000
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
  sll a1, a7, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  bnez a3, .Lskip1_2
  mv a5, a4
.Lskip1_2:
  divu a7, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 60000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 240
.Lloop2:
  add a2, a0, a1
  mul a4, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  srl a7, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 90000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 219
.Lloop3:
  and a3, a1, a2
  or a5, a3, a4
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  sll a0, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  and a3, a1, a2
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
  .word 123456790
  .word 2777892559
  .word 1137361032
  .word 3791796801
  .word 2151265274
  .word 510733747
  .word 3165169516
  .word 1524637989
  .word 4179073758
  .word 2538542231
  .word 898010704
  .word 3552446473
  .word 1911914946
  .word 271383419
  .word 2925819188
  .word 1285287661
  .word 3939723430
  .word 2299191903
  .word 658660376
  .word 3313096145
  .word 1672564618
  .word 32033091
  .word 2686468860
  .word 1045937333
  .word 3700373102
  .word 2059841575
  .word 419310048
  .word 3073745817
  .word 1433214290
  .word 4087650059
  .word 2447118532
  .word 806587005
  .word 3461022774
  .word 1820491247
  .word 179959720
  .word 2834395489
  .word 1193863962
  .word 3848299731
  .word 2207768204
  .word 567236677
  .word 3221672446
  .word 1581140919
  .word 4235576688
  .word 2595045161
  .word 954513634
  .word 3608949403
  .word 1968417876
  .word 327886349
  .word 2982322118
  .word 1341790591
  .word 3996226360
  .word 2355694833
  .word 715163306
  .word 3369599075
  .word 1729067548
  .word 88536021
  .word 2742971790
  .word 1102440263
  .word 3756876032
  .word 2116344505
  .word 475812978
  .word 3130248747
  .word 1489717220
  .word 4144152989
.section .bss
.balign 4
snapshot: .space 32
