.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1
  li a2, 219909678
  li a3, 31
  li a4, 205214907
  li a5, 0
  li a6, 2219884213
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 24728
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 784
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 48537
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 76
.Lloop1:
  bnez a7, .Lskip1_0
  mv a6, a0
.Lskip1_0:
  xor a6, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 69053
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 288
.Lloop2:
  mul a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 80727
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 228
.Lloop3:
  bnez a5, .Lskip3_0
  mv a4, a1
.Lskip3_0:
  bnez a4, .Lskip3_1
  mv a5, a1
.Lskip3_1:
  bnez a2, .Lskip3_2
  mv a7, a0
.Lskip3_2:
  bnez a3, .Lskip3_3
  mv a7, a1
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 88235
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 68
.Lloop4:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 112840
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 96
.Lloop5:
  or a7, a5, a0
  srl a2, a2, a0
  xor a6, a2, a0
  sll a5, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 127877
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 130
.Lloop6:
  divu a4, a5, a7
  divu a5, a6, a4
  divu a1, a5, a1
  divu a2, a1, a2
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
  .word 1565191766
  .word 4219627535
  .word 2579096008
  .word 938564481
  .word 3593000250
  .word 1952468723
  .word 311937196
  .word 2966372965
  .word 1325841438
  .word 3980277207
  .word 2339745680
  .word 699214153
  .word 3353649922
  .word 1713118395
  .word 72586868
  .word 2727022637
  .word 1086491110
  .word 3740926879
  .word 2100395352
  .word 459863825
  .word 3114299594
  .word 1473768067
  .word 4128203836
  .word 2487672309
  .word 847140782
  .word 3501576551
  .word 1861045024
  .word 220513497
  .word 2874949266
  .word 1234417739
  .word 3888853508
  .word 2248321981
  .word 607790454
  .word 3262226223
  .word 1621694696
  .word 4276130465
  .word 2635598938
  .word 995067411
  .word 3649503180
  .word 2008971653
  .word 368440126
  .word 3022875895
  .word 1382344368
  .word 4036780137
  .word 2396248610
  .word 755717083
  .word 3410152852
  .word 1769621325
  .word 129089798
  .word 2783525567
  .word 1142994040
  .word 3797429809
  .word 2156898282
  .word 516366755
  .word 3170802524
  .word 1530270997
  .word 4184706766
  .word 2544175239
  .word 903643712
  .word 3558079481
  .word 1917547954
  .word 277016427
  .word 2931452196
  .word 1290920669
.section .bss
.balign 4
snapshot: .space 32
