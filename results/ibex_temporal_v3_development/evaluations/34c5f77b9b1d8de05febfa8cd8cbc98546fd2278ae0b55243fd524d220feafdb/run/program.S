.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
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
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  divu a0, a0, a1
  sll a1, a1, a2
  mul a2, a2, a3
  and a3, a3, a4
  or a4, a4, a5
  srl a5, a5, a6
  xor a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  mul a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  srl a4, a4, a5
  add a5, a5, a6
  xor a6, a6, a7
  sll a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
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
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
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
  .word 1122334490
  .word 3776770259
  .word 2136238732
  .word 495707205
  .word 3150142974
  .word 1509611447
  .word 4164047216
  .word 2523515689
  .word 882984162
  .word 3537419931
  .word 1896888404
  .word 256356877
  .word 2910792646
  .word 1270261119
  .word 3924696888
  .word 2284165361
  .word 643633834
  .word 3298069603
  .word 1657538076
  .word 17006549
  .word 2671442318
  .word 1030910791
  .word 3685346560
  .word 2044815033
  .word 404283506
  .word 3058719275
  .word 1418187748
  .word 4072623517
  .word 2432091990
  .word 791560463
  .word 3445996232
  .word 1805464705
  .word 164933178
  .word 2819368947
  .word 1178837420
  .word 3833273189
  .word 2192741662
  .word 552210135
  .word 3206645904
  .word 1566114377
  .word 4220550146
  .word 2580018619
  .word 939487092
  .word 3593922861
  .word 1953391334
  .word 312859807
  .word 2967295576
  .word 1326764049
  .word 3981199818
  .word 2340668291
  .word 700136764
  .word 3354572533
  .word 1714041006
  .word 73509479
  .word 2727945248
  .word 1087413721
  .word 3741849490
  .word 2101317963
  .word 460786436
  .word 3115222205
  .word 1474690678
  .word 4129126447
  .word 2488594920
  .word 848063393
.section .bss
.balign 4
snapshot: .space 32
