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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  xor a1, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  srl a3, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  add a4, a1, a0
  xor a5, a3, a2
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  sll a7, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  sll a0, a0, a4
  add a1, a1, a5
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a3, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  srl a4, a4, a0
  add a5, a5, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a7, a7, a2
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
  .word 1000000006
  .word 3654435775
  .word 2013904248
  .word 373372721
  .word 3027808490
  .word 1387276963
  .word 4041712732
  .word 2401181205
  .word 760649678
  .word 3415085447
  .word 1774553920
  .word 134022393
  .word 2788458162
  .word 1147926635
  .word 3802362404
  .word 2161830877
  .word 521299350
  .word 3175735119
  .word 1535203592
  .word 4189639361
  .word 2549107834
  .word 908576307
  .word 3563012076
  .word 1922480549
  .word 281949022
  .word 2936384791
  .word 1295853264
  .word 3950289033
  .word 2309757506
  .word 669225979
  .word 3323661748
  .word 1683130221
  .word 42598694
  .word 2697034463
  .word 1056502936
  .word 3710938705
  .word 2070407178
  .word 429875651
  .word 3084311420
  .word 1443779893
  .word 4098215662
  .word 2457684135
  .word 817152608
  .word 3471588377
  .word 1831056850
  .word 190525323
  .word 2844961092
  .word 1204429565
  .word 3858865334
  .word 2218333807
  .word 577802280
  .word 3232238049
  .word 1591706522
  .word 4246142291
  .word 2605610764
  .word 965079237
  .word 3619515006
  .word 1978983479
  .word 338451952
  .word 2992887721
  .word 1352356194
  .word 4006791963
  .word 2366260436
  .word 725728909
.section .bss
.balign 4
snapshot: .space 32
