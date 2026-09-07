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
  add a0, a0, a1
  add a1, a0, a1
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
  add a6, a0, a1
  add a7, a0, a1
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
  .word 2000000003
  .word 359468476
  .word 3013904245
  .word 1373372718
  .word 4027808487
  .word 2387276960
  .word 746745433
  .word 3401181202
  .word 1760649675
  .word 120118148
  .word 2774553917
  .word 1134022390
  .word 3788458159
  .word 2147926632
  .word 507395105
  .word 3161830874
  .word 1521299347
  .word 4175735116
  .word 2535203589
  .word 894672062
  .word 3549107831
  .word 1908576304
  .word 268044777
  .word 2922480546
  .word 1281949019
  .word 3936384788
  .word 2295853261
  .word 655321734
  .word 3309757503
  .word 1669225976
  .word 28694449
  .word 2683130218
  .word 1042598691
  .word 3697034460
  .word 2056502933
  .word 415971406
  .word 3070407175
  .word 1429875648
  .word 4084311417
  .word 2443779890
  .word 803248363
  .word 3457684132
  .word 1817152605
  .word 176621078
  .word 2831056847
  .word 1190525320
  .word 3844961089
  .word 2204429562
  .word 563898035
  .word 3218333804
  .word 1577802277
  .word 4232238046
  .word 2591706519
  .word 951174992
  .word 3605610761
  .word 1965079234
  .word 324547707
  .word 2978983476
  .word 1338451949
  .word 3992887718
  .word 2352356191
  .word 711824664
  .word 3366260433
  .word 1725728906
.section .bss
.balign 4
snapshot: .space 32
