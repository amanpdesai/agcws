.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
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
  add a0, a0, a1
  xor a1, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  srl a3, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  mul a4, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  srl a3, a5, a6
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 170
.Lloop1:
  add a4, a1, a0
  xor a5, a3, a2
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  sll a7, a7, a4
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  divu a2, a4, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  add a4, a1, a0
  xor a5, a3, a2
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  sll a7, a7, a4
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 170
.Lloop2:
  sll a0, a0, a4
  add a1, a1, a5
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a3, a3, a6
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  and a7, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a0, a0, a4
  add a1, a1, a5
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a3, a3, a6
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 170
.Lloop3:
  srl a4, a4, a0
  add a5, a5, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a7, a7, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  or a1, a0, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
  srl a4, a4, a0
  add a5, a5, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a7, a7, a2
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
  .word 1000000008
  .word 3654435777
  .word 2013904250
  .word 373372723
  .word 3027808492
  .word 1387276965
  .word 4041712734
  .word 2401181207
  .word 760649680
  .word 3415085449
  .word 1774553922
  .word 134022395
  .word 2788458164
  .word 1147926637
  .word 3802362406
  .word 2161830879
  .word 521299352
  .word 3175735121
  .word 1535203594
  .word 4189639363
  .word 2549107836
  .word 908576309
  .word 3563012078
  .word 1922480551
  .word 281949024
  .word 2936384793
  .word 1295853266
  .word 3950289035
  .word 2309757508
  .word 669225981
  .word 3323661750
  .word 1683130223
  .word 42598696
  .word 2697034465
  .word 1056502938
  .word 3710938707
  .word 2070407180
  .word 429875653
  .word 3084311422
  .word 1443779895
  .word 4098215664
  .word 2457684137
  .word 817152610
  .word 3471588379
  .word 1831056852
  .word 190525325
  .word 2844961094
  .word 1204429567
  .word 3858865336
  .word 2218333809
  .word 577802282
  .word 3232238051
  .word 1591706524
  .word 4246142293
  .word 2605610766
  .word 965079239
  .word 3619515008
  .word 1978983481
  .word 338451954
  .word 2992887723
  .word 1352356196
  .word 4006791965
  .word 2366260438
  .word 725728911
.section .bss
.balign 4
snapshot: .space 32
