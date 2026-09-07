.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1425764691
  li a1, 977567979
  li a2, 4294967295
  li a3, 0
  li a4, 3794713127
  li a5, 1
  li a6, 0
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 63322
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 196
.Lloop0:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 63520
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 1116
.Lloop1:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 93005
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 134
.Lloop2:
  and a3, a5, a0
  xor a3, a3, a1
  divu a5, a5, a0
  sll a2, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 99007
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 74
.Lloop3:
  and a4, a5, a1
  xor a4, a3, a1
  xor a7, a6, a1
  xor a6, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 160955
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 68
.Lloop4:
  mul a2, a2, a2
  mul a6, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 163767
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 63
.Lloop5:
  divu a6, a3, a0
  divu a3, a7, a0
  divu a5, a7, a1
  divu a2, a4, a1
  divu a3, a6, a0
  divu a7, a1, a1
  divu a7, a1, a1
  divu a3, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 1066022571
  .word 3720458340
  .word 2079926813
  .word 439395286
  .word 3093831055
  .word 1453299528
  .word 4107735297
  .word 2467203770
  .word 826672243
  .word 3481108012
  .word 1840576485
  .word 200044958
  .word 2854480727
  .word 1213949200
  .word 3868384969
  .word 2227853442
  .word 587321915
  .word 3241757684
  .word 1601226157
  .word 4255661926
  .word 2615130399
  .word 974598872
  .word 3629034641
  .word 1988503114
  .word 347971587
  .word 3002407356
  .word 1361875829
  .word 4016311598
  .word 2375780071
  .word 735248544
  .word 3389684313
  .word 1749152786
  .word 108621259
  .word 2763057028
  .word 1122525501
  .word 3776961270
  .word 2136429743
  .word 495898216
  .word 3150333985
  .word 1509802458
  .word 4164238227
  .word 2523706700
  .word 883175173
  .word 3537610942
  .word 1897079415
  .word 256547888
  .word 2910983657
  .word 1270452130
  .word 3924887899
  .word 2284356372
  .word 643824845
  .word 3298260614
  .word 1657729087
  .word 17197560
  .word 2671633329
  .word 1031101802
  .word 3685537571
  .word 2045006044
  .word 404474517
  .word 3058910286
  .word 1418378759
  .word 4072814528
  .word 2432283001
  .word 791751474
.section .bss
.balign 4
snapshot: .space 32
