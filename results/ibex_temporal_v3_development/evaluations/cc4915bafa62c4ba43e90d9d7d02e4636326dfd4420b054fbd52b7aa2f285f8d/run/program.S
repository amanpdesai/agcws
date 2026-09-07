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
  li a4, 4294967295
  li a5, 4294967295
  li a6, 17
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 26549
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 880
.Lloop0:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 148152
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 584
.Lloop1:
  and a4, a0, a0
  and a5, a2, a0
  sll a6, a2, a1
  and a4, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 1724528791
  .word 83997264
  .word 2738433033
  .word 1097901506
  .word 3752337275
  .word 2111805748
  .word 471274221
  .word 3125709990
  .word 1485178463
  .word 4139614232
  .word 2499082705
  .word 858551178
  .word 3512986947
  .word 1872455420
  .word 231923893
  .word 2886359662
  .word 1245828135
  .word 3900263904
  .word 2259732377
  .word 619200850
  .word 3273636619
  .word 1633105092
  .word 4287540861
  .word 2647009334
  .word 1006477807
  .word 3660913576
  .word 2020382049
  .word 379850522
  .word 3034286291
  .word 1393754764
  .word 4048190533
  .word 2407659006
  .word 767127479
  .word 3421563248
  .word 1781031721
  .word 140500194
  .word 2794935963
  .word 1154404436
  .word 3808840205
  .word 2168308678
  .word 527777151
  .word 3182212920
  .word 1541681393
  .word 4196117162
  .word 2555585635
  .word 915054108
  .word 3569489877
  .word 1928958350
  .word 288426823
  .word 2942862592
  .word 1302331065
  .word 3956766834
  .word 2316235307
  .word 675703780
  .word 3330139549
  .word 1689608022
  .word 49076495
  .word 2703512264
  .word 1062980737
  .word 3717416506
  .word 2076884979
  .word 436353452
  .word 3090789221
  .word 1450257694
.section .bss
.balign 4
snapshot: .space 32
