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
  li t6, 150
.Lloop0:
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 100
.Lloop1:
  divu a3, a3, a1
  srl a4, a4, a3
  bnez a5, .Lskip1_2
  mv a5, a4
.Lskip1_2:
  divu a1, a1, a2
  divu a3, a3, a0
  divu a5, a5, a5
  divu a4, a4, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 114
.Lloop2:
  divu a6, a6, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  divu a7, a7, a0
  divu a1, a1, a6
  divu a0, a0, a7
  divu a2, a2, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a6, a6, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 180
.Lloop3:
  add a7, a7, a0
  sll a0, a0, a7
  mul a7, a7, a0
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 175000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 132
.Lloop4:
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
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
  .word 314159265
  .word 2968595034
  .word 1328063507
  .word 3982499276
  .word 2341967749
  .word 701436222
  .word 3355871991
  .word 1715340464
  .word 74808937
  .word 2729244706
  .word 1088713179
  .word 3743148948
  .word 2102617421
  .word 462085894
  .word 3116521663
  .word 1475990136
  .word 4130425905
  .word 2489894378
  .word 849362851
  .word 3503798620
  .word 1863267093
  .word 222735566
  .word 2877171335
  .word 1236639808
  .word 3891075577
  .word 2250544050
  .word 610012523
  .word 3264448292
  .word 1623916765
  .word 4278352534
  .word 2637821007
  .word 997289480
  .word 3651725249
  .word 2011193722
  .word 370662195
  .word 3025097964
  .word 1384566437
  .word 4039002206
  .word 2398470679
  .word 757939152
  .word 3412374921
  .word 1771843394
  .word 131311867
  .word 2785747636
  .word 1145216109
  .word 3799651878
  .word 2159120351
  .word 518588824
  .word 3173024593
  .word 1532493066
  .word 4186928835
  .word 2546397308
  .word 905865781
  .word 3560301550
  .word 1919770023
  .word 279238496
  .word 2933674265
  .word 1293142738
  .word 3947578507
  .word 2307046980
  .word 666515453
  .word 3320951222
  .word 1680419695
  .word 39888168
.section .bss
.balign 4
snapshot: .space 32
