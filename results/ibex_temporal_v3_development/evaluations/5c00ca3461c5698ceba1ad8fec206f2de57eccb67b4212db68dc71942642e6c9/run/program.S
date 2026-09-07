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
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 170
.Lloop0:
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 512
.Lloop2:
  sll a0, a0, a1
  srl a0, a0, a1
  add a0, a0, a1
  xor a0, a0, a1
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
  .word 54321
  .word 2654490090
  .word 1013958563
  .word 3668394332
  .word 2027862805
  .word 387331278
  .word 3041767047
  .word 1401235520
  .word 4055671289
  .word 2415139762
  .word 774608235
  .word 3429044004
  .word 1788512477
  .word 147980950
  .word 2802416719
  .word 1161885192
  .word 3816320961
  .word 2175789434
  .word 535257907
  .word 3189693676
  .word 1549162149
  .word 4203597918
  .word 2563066391
  .word 922534864
  .word 3576970633
  .word 1936439106
  .word 295907579
  .word 2950343348
  .word 1309811821
  .word 3964247590
  .word 2323716063
  .word 683184536
  .word 3337620305
  .word 1697088778
  .word 56557251
  .word 2710993020
  .word 1070461493
  .word 3724897262
  .word 2084365735
  .word 443834208
  .word 3098269977
  .word 1457738450
  .word 4112174219
  .word 2471642692
  .word 831111165
  .word 3485546934
  .word 1845015407
  .word 204483880
  .word 2858919649
  .word 1218388122
  .word 3872823891
  .word 2232292364
  .word 591760837
  .word 3246196606
  .word 1605665079
  .word 4260100848
  .word 2619569321
  .word 979037794
  .word 3633473563
  .word 1992942036
  .word 352410509
  .word 3006846278
  .word 1366314751
  .word 4020750520
.section .bss
.balign 4
snapshot: .space 32
