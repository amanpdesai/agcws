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
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 128
.Lloop0:
  xor a0, a1, a2
  xor a1, a2, a3
  xor a2, a3, a4
  xor a3, a4, a5
  xor a4, a5, a6
  xor a5, a6, a7
  xor a6, a7, a0
  xor a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  divu a0, a1, a3
  divu a1, a2, a4
  divu a2, a3, a5
  divu a3, a4, a6
  divu a4, a5, a7
  divu a5, a6, a0
  divu a6, a7, a1
  divu a7, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  sll a0, a1, a2
  sll a1, a2, a3
  sll a2, a3, a4
  sll a3, a4, a5
  sll a4, a5, a6
  sll a5, a6, a7
  sll a6, a7, a0
  sll a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  divu a1, a1, a3
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  divu a4, a4, a6
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
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
  .word 1000000013
  .word 3654435782
  .word 2013904255
  .word 373372728
  .word 3027808497
  .word 1387276970
  .word 4041712739
  .word 2401181212
  .word 760649685
  .word 3415085454
  .word 1774553927
  .word 134022400
  .word 2788458169
  .word 1147926642
  .word 3802362411
  .word 2161830884
  .word 521299357
  .word 3175735126
  .word 1535203599
  .word 4189639368
  .word 2549107841
  .word 908576314
  .word 3563012083
  .word 1922480556
  .word 281949029
  .word 2936384798
  .word 1295853271
  .word 3950289040
  .word 2309757513
  .word 669225986
  .word 3323661755
  .word 1683130228
  .word 42598701
  .word 2697034470
  .word 1056502943
  .word 3710938712
  .word 2070407185
  .word 429875658
  .word 3084311427
  .word 1443779900
  .word 4098215669
  .word 2457684142
  .word 817152615
  .word 3471588384
  .word 1831056857
  .word 190525330
  .word 2844961099
  .word 1204429572
  .word 3858865341
  .word 2218333814
  .word 577802287
  .word 3232238056
  .word 1591706529
  .word 4246142298
  .word 2605610771
  .word 965079244
  .word 3619515013
  .word 1978983486
  .word 338451959
  .word 2992887728
  .word 1352356201
  .word 4006791970
  .word 2366260443
  .word 725728916
.section .bss
.balign 4
snapshot: .space 32
