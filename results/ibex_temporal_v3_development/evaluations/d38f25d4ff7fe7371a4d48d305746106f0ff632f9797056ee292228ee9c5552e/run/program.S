.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
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
  mul a0, a0, a0
  mul a1, a1, a0
  mul a2, a2, a0
  mul a3, a3, a0
  mul a4, a4, a0
  mul a5, a5, a0
  mul a6, a6, a0
  mul a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 5000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  sll a0, a0, a1
  sll a1, a1, a2
  sll a2, a2, a3
  sll a3, a3, a4
  sll a4, a4, a5
  sll a5, a5, a6
  sll a6, a6, a7
  sll a7, a7, a0
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
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  divu a3, a3, a4
  divu a4, a4, a5
  divu a5, a5, a6
  divu a6, a6, a7
  divu a7, a7, a0
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
