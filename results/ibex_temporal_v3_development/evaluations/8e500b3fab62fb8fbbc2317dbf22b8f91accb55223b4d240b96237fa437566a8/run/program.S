.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
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
  li t6, 200
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  mul a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 516
.Lloop1:
  divu a4, a4, a1
  divu a5, a5, a2
  divu a6, a6, a3
  divu a7, a7, a4
  divu a0, a0, a5
  divu a1, a1, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 246813579
  .word 2901249348
  .word 1260717821
  .word 3915153590
  .word 2274622063
  .word 634090536
  .word 3288526305
  .word 1647994778
  .word 7463251
  .word 2661899020
  .word 1021367493
  .word 3675803262
  .word 2035271735
  .word 394740208
  .word 3049175977
  .word 1408644450
  .word 4063080219
  .word 2422548692
  .word 782017165
  .word 3436452934
  .word 1795921407
  .word 155389880
  .word 2809825649
  .word 1169294122
  .word 3823729891
  .word 2183198364
  .word 542666837
  .word 3197102606
  .word 1556571079
  .word 4211006848
  .word 2570475321
  .word 929943794
  .word 3584379563
  .word 1943848036
  .word 303316509
  .word 2957752278
  .word 1317220751
  .word 3971656520
  .word 2331124993
  .word 690593466
  .word 3345029235
  .word 1704497708
  .word 63966181
  .word 2718401950
  .word 1077870423
  .word 3732306192
  .word 2091774665
  .word 451243138
  .word 3105678907
  .word 1465147380
  .word 4119583149
  .word 2479051622
  .word 838520095
  .word 3492955864
  .word 1852424337
  .word 211892810
  .word 2866328579
  .word 1225797052
  .word 3880232821
  .word 2239701294
  .word 599169767
  .word 3253605536
  .word 1613074009
  .word 4267509778
.section .bss
.balign 4
snapshot: .space 32
