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
  li t6, 64
.Lloop0:
  divu a1, a0, a0
  divu a2, a1, a0
  divu a3, a2, a0
  divu a4, a3, a0
  divu a5, a4, a0
  divu a6, a5, a0
  divu a7, a6, a0
  divu a0, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 40000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 128
.Lloop4:
  divu a0, a1, a2
  divu a1, a3, a4
  divu a2, a5, a6
  divu a3, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 1642357890
  .word 1826363
  .word 2656262132
  .word 1015730605
  .word 3670166374
  .word 2029634847
  .word 389103320
  .word 3043539089
  .word 1403007562
  .word 4057443331
  .word 2416911804
  .word 776380277
  .word 3430816046
  .word 1790284519
  .word 149752992
  .word 2804188761
  .word 1163657234
  .word 3818093003
  .word 2177561476
  .word 537029949
  .word 3191465718
  .word 1550934191
  .word 4205369960
  .word 2564838433
  .word 924306906
  .word 3578742675
  .word 1938211148
  .word 297679621
  .word 2952115390
  .word 1311583863
  .word 3966019632
  .word 2325488105
  .word 684956578
  .word 3339392347
  .word 1698860820
  .word 58329293
  .word 2712765062
  .word 1072233535
  .word 3726669304
  .word 2086137777
  .word 445606250
  .word 3100042019
  .word 1459510492
  .word 4113946261
  .word 2473414734
  .word 832883207
  .word 3487318976
  .word 1846787449
  .word 206255922
  .word 2860691691
  .word 1220160164
  .word 3874595933
  .word 2234064406
  .word 593532879
  .word 3247968648
  .word 1607437121
  .word 4261872890
  .word 2621341363
  .word 980809836
  .word 3635245605
  .word 1994714078
  .word 354182551
  .word 3008618320
  .word 1368086793
.section .bss
.balign 4
snapshot: .space 32
