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
  li t6, 1024
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 2000000000
  .word 359468473
  .word 3013904242
  .word 1373372715
  .word 4027808484
  .word 2387276957
  .word 746745430
  .word 3401181199
  .word 1760649672
  .word 120118145
  .word 2774553914
  .word 1134022387
  .word 3788458156
  .word 2147926629
  .word 507395102
  .word 3161830871
  .word 1521299344
  .word 4175735113
  .word 2535203586
  .word 894672059
  .word 3549107828
  .word 1908576301
  .word 268044774
  .word 2922480543
  .word 1281949016
  .word 3936384785
  .word 2295853258
  .word 655321731
  .word 3309757500
  .word 1669225973
  .word 28694446
  .word 2683130215
  .word 1042598688
  .word 3697034457
  .word 2056502930
  .word 415971403
  .word 3070407172
  .word 1429875645
  .word 4084311414
  .word 2443779887
  .word 803248360
  .word 3457684129
  .word 1817152602
  .word 176621075
  .word 2831056844
  .word 1190525317
  .word 3844961086
  .word 2204429559
  .word 563898032
  .word 3218333801
  .word 1577802274
  .word 4232238043
  .word 2591706516
  .word 951174989
  .word 3605610758
  .word 1965079231
  .word 324547704
  .word 2978983473
  .word 1338451946
  .word 3992887715
  .word 2352356188
  .word 711824661
  .word 3366260430
  .word 1725728903
.section .bss
.balign 4
snapshot: .space 32
