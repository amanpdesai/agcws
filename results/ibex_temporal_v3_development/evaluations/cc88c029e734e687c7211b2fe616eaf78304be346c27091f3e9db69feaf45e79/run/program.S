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
  divu a0, a1, a2
  divu a1, a2, a3
  divu a2, a3, a4
  divu a3, a4, a5
  divu a4, a5, a6
  divu a5, a6, a7
  divu a6, a7, a0
  divu a7, a0, a1
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
  divu a1, a1, a2
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  divu a4, a4, a5
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
  .word 1000000012
  .word 3654435781
  .word 2013904254
  .word 373372727
  .word 3027808496
  .word 1387276969
  .word 4041712738
  .word 2401181211
  .word 760649684
  .word 3415085453
  .word 1774553926
  .word 134022399
  .word 2788458168
  .word 1147926641
  .word 3802362410
  .word 2161830883
  .word 521299356
  .word 3175735125
  .word 1535203598
  .word 4189639367
  .word 2549107840
  .word 908576313
  .word 3563012082
  .word 1922480555
  .word 281949028
  .word 2936384797
  .word 1295853270
  .word 3950289039
  .word 2309757512
  .word 669225985
  .word 3323661754
  .word 1683130227
  .word 42598700
  .word 2697034469
  .word 1056502942
  .word 3710938711
  .word 2070407184
  .word 429875657
  .word 3084311426
  .word 1443779899
  .word 4098215668
  .word 2457684141
  .word 817152614
  .word 3471588383
  .word 1831056856
  .word 190525329
  .word 2844961098
  .word 1204429571
  .word 3858865340
  .word 2218333813
  .word 577802286
  .word 3232238055
  .word 1591706528
  .word 4246142297
  .word 2605610770
  .word 965079243
  .word 3619515012
  .word 1978983485
  .word 338451958
  .word 2992887727
  .word 1352356200
  .word 4006791969
  .word 2366260442
  .word 725728915
.section .bss
.balign 4
snapshot: .space 32
