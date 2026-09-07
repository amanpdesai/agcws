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
  li t6, 512
.Lloop0:
  bnez a0, .Lskip0_0
  mv a0, a1
.Lskip0_0:
  bnez a0, .Lskip0_1
  mv a1, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 512
.Lloop1:
  divu a2, a0, a1
  divu a3, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 512
.Lloop2:
  divu a4, a0, a1
  divu a5, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 512
.Lloop3:
  bnez a0, .Lskip3_0
  mv a6, a1
.Lskip3_0:
  bnez a0, .Lskip3_1
  mv a7, a1
.Lskip3_1:
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
  .word 1000000003
  .word 3654435772
  .word 2013904245
  .word 373372718
  .word 3027808487
  .word 1387276960
  .word 4041712729
  .word 2401181202
  .word 760649675
  .word 3415085444
  .word 1774553917
  .word 134022390
  .word 2788458159
  .word 1147926632
  .word 3802362401
  .word 2161830874
  .word 521299347
  .word 3175735116
  .word 1535203589
  .word 4189639358
  .word 2549107831
  .word 908576304
  .word 3563012073
  .word 1922480546
  .word 281949019
  .word 2936384788
  .word 1295853261
  .word 3950289030
  .word 2309757503
  .word 669225976
  .word 3323661745
  .word 1683130218
  .word 42598691
  .word 2697034460
  .word 1056502933
  .word 3710938702
  .word 2070407175
  .word 429875648
  .word 3084311417
  .word 1443779890
  .word 4098215659
  .word 2457684132
  .word 817152605
  .word 3471588374
  .word 1831056847
  .word 190525320
  .word 2844961089
  .word 1204429562
  .word 3858865331
  .word 2218333804
  .word 577802277
  .word 3232238046
  .word 1591706519
  .word 4246142288
  .word 2605610761
  .word 965079234
  .word 3619515003
  .word 1978983476
  .word 338451949
  .word 2992887718
  .word 1352356191
  .word 4006791960
  .word 2366260433
  .word 725728906
.section .bss
.balign 4
snapshot: .space 32
