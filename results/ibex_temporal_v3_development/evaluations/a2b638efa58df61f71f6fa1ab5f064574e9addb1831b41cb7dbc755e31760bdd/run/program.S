.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 0
  li a2, 4294967295
  li a3, 0
  li a4, 4294967295
  li a5, 0
  li a6, 4294967295
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
  li t6, 433
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 183
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 150
.Lloop2:
  bnez a0, .Lskip2_0
  mv a2, a1
.Lskip2_0:
  bnez a2, .Lskip2_1
  mv a4, a3
.Lskip2_1:
  bnez a4, .Lskip2_2
  mv a6, a5
.Lskip2_2:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a2, a0, a1
  divu a4, a2, a3
  divu a6, a4, a5
  mul a0, a6, a7
  mul a2, a0, a1
  mul a4, a2, a3
  divu a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
  divu a2, a0, a1
  divu a4, a2, a3
  divu a6, a4, a5
  mul a0, a6, a7
  mul a2, a0, a1
  mul a4, a2, a3
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
  .word 998877665
  .word 3653313434
  .word 2012781907
  .word 372250380
  .word 3026686149
  .word 1386154622
  .word 4040590391
  .word 2400058864
  .word 759527337
  .word 3413963106
  .word 1773431579
  .word 132900052
  .word 2787335821
  .word 1146804294
  .word 3801240063
  .word 2160708536
  .word 520177009
  .word 3174612778
  .word 1534081251
  .word 4188517020
  .word 2547985493
  .word 907453966
  .word 3561889735
  .word 1921358208
  .word 280826681
  .word 2935262450
  .word 1294730923
  .word 3949166692
  .word 2308635165
  .word 668103638
  .word 3322539407
  .word 1682007880
  .word 41476353
  .word 2695912122
  .word 1055380595
  .word 3709816364
  .word 2069284837
  .word 428753310
  .word 3083189079
  .word 1442657552
  .word 4097093321
  .word 2456561794
  .word 816030267
  .word 3470466036
  .word 1829934509
  .word 189402982
  .word 2843838751
  .word 1203307224
  .word 3857742993
  .word 2217211466
  .word 576679939
  .word 3231115708
  .word 1590584181
  .word 4245019950
  .word 2604488423
  .word 963956896
  .word 3618392665
  .word 1977861138
  .word 337329611
  .word 2991765380
  .word 1351233853
  .word 4005669622
  .word 2365138095
  .word 724606568
.section .bss
.balign 4
snapshot: .space 32
