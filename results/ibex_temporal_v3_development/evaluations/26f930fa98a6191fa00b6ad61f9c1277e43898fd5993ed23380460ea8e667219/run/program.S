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
  li t6, 128
.Lloop0:
  bnez a0, .Lskip0_0
  mv a0, a0
.Lskip0_0:
  bnez a1, .Lskip0_1
  mv a1, a1
.Lskip0_1:
  bnez a2, .Lskip0_2
  mv a2, a2
.Lskip0_2:
  bnez a3, .Lskip0_3
  mv a3, a3
.Lskip0_3:
  bnez a4, .Lskip0_4
  mv a4, a4
.Lskip0_4:
  bnez a5, .Lskip0_5
  mv a5, a5
.Lskip0_5:
  bnez a6, .Lskip0_6
  mv a6, a6
.Lskip0_6:
  bnez a7, .Lskip0_7
  mv a7, a7
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 5000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  mul a0, a0, a1
  mul a1, a1, a2
  mul a2, a2, a3
  mul a3, a3, a4
  mul a4, a4, a5
  mul a5, a5, a6
  mul a6, a6, a7
  mul a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 10000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  xor a0, a0, a1
  xor a1, a1, a2
  xor a2, a2, a3
  xor a3, a3, a4
  xor a4, a4, a5
  xor a5, a5, a6
  xor a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 15000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  sll a0, a0, a1
  sll a1, a1, a2
  sll a2, a2, a3
  sll a3, a3, a4
  sll a4, a4, a5
  sll a5, a5, a6
  sll a6, a6, a7
  sll a7, a7, a0
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
  .word 1000000000
  .word 3654435769
  .word 2013904242
  .word 373372715
  .word 3027808484
  .word 1387276957
  .word 4041712726
  .word 2401181199
  .word 760649672
  .word 3415085441
  .word 1774553914
  .word 134022387
  .word 2788458156
  .word 1147926629
  .word 3802362398
  .word 2161830871
  .word 521299344
  .word 3175735113
  .word 1535203586
  .word 4189639355
  .word 2549107828
  .word 908576301
  .word 3563012070
  .word 1922480543
  .word 281949016
  .word 2936384785
  .word 1295853258
  .word 3950289027
  .word 2309757500
  .word 669225973
  .word 3323661742
  .word 1683130215
  .word 42598688
  .word 2697034457
  .word 1056502930
  .word 3710938699
  .word 2070407172
  .word 429875645
  .word 3084311414
  .word 1443779887
  .word 4098215656
  .word 2457684129
  .word 817152602
  .word 3471588371
  .word 1831056844
  .word 190525317
  .word 2844961086
  .word 1204429559
  .word 3858865328
  .word 2218333801
  .word 577802274
  .word 3232238043
  .word 1591706516
  .word 4246142285
  .word 2605610758
  .word 965079231
  .word 3619515000
  .word 1978983473
  .word 338451946
  .word 2992887715
  .word 1352356188
  .word 4006791957
  .word 2366260430
  .word 725728903
.section .bss
.balign 4
snapshot: .space 32
