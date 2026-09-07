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
  li a7, 8
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 204
.Lloop0:
  add a0, a0, a1
  srl a1, a1, a2
  xor a2, a2, a3
  and a3, a3, a4
  mul a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  srl a1, a1, a2
  xor a2, a2, a3
  and a3, a3, a4
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 204
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  divu a6, a6, a7
  bnez a0, .Lskip1_3
  mv a7, a7
.Lskip1_3:
  add a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  divu a6, a6, a7
  bnez a0, .Ltail_skip1_3
  mv a7, a7
.Ltail_skip1_3:
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 204
.Lloop2:
  sll a1, a1, a2
  or a2, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a1, a1, a2
  or a2, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 204
.Lloop3:
  add a5, a5, a6
  xor a6, a6, a7
  srl a7, a7, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a5, a5, a6
  xor a6, a6, a7
  srl a7, a7, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
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
  .word 1000000009
  .word 3654435778
  .word 2013904251
  .word 373372724
  .word 3027808493
  .word 1387276966
  .word 4041712735
  .word 2401181208
  .word 760649681
  .word 3415085450
  .word 1774553923
  .word 134022396
  .word 2788458165
  .word 1147926638
  .word 3802362407
  .word 2161830880
  .word 521299353
  .word 3175735122
  .word 1535203595
  .word 4189639364
  .word 2549107837
  .word 908576310
  .word 3563012079
  .word 1922480552
  .word 281949025
  .word 2936384794
  .word 1295853267
  .word 3950289036
  .word 2309757509
  .word 669225982
  .word 3323661751
  .word 1683130224
  .word 42598697
  .word 2697034466
  .word 1056502939
  .word 3710938708
  .word 2070407181
  .word 429875654
  .word 3084311423
  .word 1443779896
  .word 4098215665
  .word 2457684138
  .word 817152611
  .word 3471588380
  .word 1831056853
  .word 190525326
  .word 2844961095
  .word 1204429568
  .word 3858865337
  .word 2218333810
  .word 577802283
  .word 3232238052
  .word 1591706525
  .word 4246142294
  .word 2605610767
  .word 965079240
  .word 3619515009
  .word 1978983482
  .word 338451955
  .word 2992887724
  .word 1352356197
  .word 4006791966
  .word 2366260439
  .word 725728912
.section .bss
.balign 4
snapshot: .space 32
