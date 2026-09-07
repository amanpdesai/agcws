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
  li t6, 256
.Lloop0:
  srl a0, a0, a1
  add a1, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a3, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  srl a4, a7, a0
  add a5, a1, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a7, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  srl a0, a6, a7
  add a1, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a3, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  srl a4, a5, a6
  add a5, a7, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a7, a2, a3
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
  .word 1000000004
  .word 3654435773
  .word 2013904246
  .word 373372719
  .word 3027808488
  .word 1387276961
  .word 4041712730
  .word 2401181203
  .word 760649676
  .word 3415085445
  .word 1774553918
  .word 134022391
  .word 2788458160
  .word 1147926633
  .word 3802362402
  .word 2161830875
  .word 521299348
  .word 3175735117
  .word 1535203590
  .word 4189639359
  .word 2549107832
  .word 908576305
  .word 3563012074
  .word 1922480547
  .word 281949020
  .word 2936384789
  .word 1295853262
  .word 3950289031
  .word 2309757504
  .word 669225977
  .word 3323661746
  .word 1683130219
  .word 42598692
  .word 2697034461
  .word 1056502934
  .word 3710938703
  .word 2070407176
  .word 429875649
  .word 3084311418
  .word 1443779891
  .word 4098215660
  .word 2457684133
  .word 817152606
  .word 3471588375
  .word 1831056848
  .word 190525321
  .word 2844961090
  .word 1204429563
  .word 3858865332
  .word 2218333805
  .word 577802278
  .word 3232238047
  .word 1591706520
  .word 4246142289
  .word 2605610762
  .word 965079235
  .word 3619515004
  .word 1978983477
  .word 338451950
  .word 2992887719
  .word 1352356192
  .word 4006791961
  .word 2366260434
  .word 725728907
.section .bss
.balign 4
snapshot: .space 32
