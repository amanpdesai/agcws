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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  divu a1, a0, a1
  add a2, a2, a1
  divu a3, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  add a4, a4, a1
  divu a5, a4, a1
  add a6, a6, a1
  divu a7, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  add a0, a0, a1
  divu a1, a0, a1
  add a2, a2, a1
  divu a3, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a4, a4, a1
  divu a5, a4, a1
  add a6, a6, a1
  divu a7, a6, a1
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
  .word 1000000011
  .word 3654435780
  .word 2013904253
  .word 373372726
  .word 3027808495
  .word 1387276968
  .word 4041712737
  .word 2401181210
  .word 760649683
  .word 3415085452
  .word 1774553925
  .word 134022398
  .word 2788458167
  .word 1147926640
  .word 3802362409
  .word 2161830882
  .word 521299355
  .word 3175735124
  .word 1535203597
  .word 4189639366
  .word 2549107839
  .word 908576312
  .word 3563012081
  .word 1922480554
  .word 281949027
  .word 2936384796
  .word 1295853269
  .word 3950289038
  .word 2309757511
  .word 669225984
  .word 3323661753
  .word 1683130226
  .word 42598699
  .word 2697034468
  .word 1056502941
  .word 3710938710
  .word 2070407183
  .word 429875656
  .word 3084311425
  .word 1443779898
  .word 4098215667
  .word 2457684140
  .word 817152613
  .word 3471588382
  .word 1831056855
  .word 190525328
  .word 2844961097
  .word 1204429570
  .word 3858865339
  .word 2218333812
  .word 577802285
  .word 3232238054
  .word 1591706527
  .word 4246142296
  .word 2605610769
  .word 965079242
  .word 3619515011
  .word 1978983484
  .word 338451957
  .word 2992887726
  .word 1352356199
  .word 4006791968
  .word 2366260441
  .word 725728914
.section .bss
.balign 4
snapshot: .space 32
