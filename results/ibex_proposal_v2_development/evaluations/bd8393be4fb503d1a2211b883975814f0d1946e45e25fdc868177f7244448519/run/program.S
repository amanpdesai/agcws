.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1
  li a2, 31
  li a3, 1
  li a4, 4294967295
  li a5, 31
  li a6, 1683080375
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 4605
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 244
.Lloop0:
  mul a7, a2, a1
  mul a4, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 38626
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 508
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 95789
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 960
.Lloop2:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 109881
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 816
.Lloop3:
  and a0, a1, a2
  srl a2, a5, a4
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
  .word 1659238919
  .word 18707392
  .word 2673143161
  .word 1032611634
  .word 3687047403
  .word 2046515876
  .word 405984349
  .word 3060420118
  .word 1419888591
  .word 4074324360
  .word 2433792833
  .word 793261306
  .word 3447697075
  .word 1807165548
  .word 166634021
  .word 2821069790
  .word 1180538263
  .word 3834974032
  .word 2194442505
  .word 553910978
  .word 3208346747
  .word 1567815220
  .word 4222250989
  .word 2581719462
  .word 941187935
  .word 3595623704
  .word 1955092177
  .word 314560650
  .word 2968996419
  .word 1328464892
  .word 3982900661
  .word 2342369134
  .word 701837607
  .word 3356273376
  .word 1715741849
  .word 75210322
  .word 2729646091
  .word 1089114564
  .word 3743550333
  .word 2103018806
  .word 462487279
  .word 3116923048
  .word 1476391521
  .word 4130827290
  .word 2490295763
  .word 849764236
  .word 3504200005
  .word 1863668478
  .word 223136951
  .word 2877572720
  .word 1237041193
  .word 3891476962
  .word 2250945435
  .word 610413908
  .word 3264849677
  .word 1624318150
  .word 4278753919
  .word 2638222392
  .word 997690865
  .word 3652126634
  .word 2011595107
  .word 371063580
  .word 3025499349
  .word 1384967822
.section .bss
.balign 4
snapshot: .space 32
