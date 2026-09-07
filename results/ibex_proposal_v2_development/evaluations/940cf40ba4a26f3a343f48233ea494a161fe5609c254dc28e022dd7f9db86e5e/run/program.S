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
  li t6, 237
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  divu a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  xor a4, a2, a3
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 268
.Lloop1:
  sll a2, a0, a1
  srl a4, a2, a3
  and a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  sll a2, a0, a1
  srl a4, a2, a3
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  or a5, a7, a6
  add a3, a5, a4
  mul a1, a3, a2
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 262
.Lloop3:
  bnez a0, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  xor a4, a2, a3
  sll a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
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
  .word 1122334456
  .word 3776770225
  .word 2136238698
  .word 495707171
  .word 3150142940
  .word 1509611413
  .word 4164047182
  .word 2523515655
  .word 882984128
  .word 3537419897
  .word 1896888370
  .word 256356843
  .word 2910792612
  .word 1270261085
  .word 3924696854
  .word 2284165327
  .word 643633800
  .word 3298069569
  .word 1657538042
  .word 17006515
  .word 2671442284
  .word 1030910757
  .word 3685346526
  .word 2044814999
  .word 404283472
  .word 3058719241
  .word 1418187714
  .word 4072623483
  .word 2432091956
  .word 791560429
  .word 3445996198
  .word 1805464671
  .word 164933144
  .word 2819368913
  .word 1178837386
  .word 3833273155
  .word 2192741628
  .word 552210101
  .word 3206645870
  .word 1566114343
  .word 4220550112
  .word 2580018585
  .word 939487058
  .word 3593922827
  .word 1953391300
  .word 312859773
  .word 2967295542
  .word 1326764015
  .word 3981199784
  .word 2340668257
  .word 700136730
  .word 3354572499
  .word 1714040972
  .word 73509445
  .word 2727945214
  .word 1087413687
  .word 3741849456
  .word 2101317929
  .word 460786402
  .word 3115222171
  .word 1474690644
  .word 4129126413
  .word 2488594886
  .word 848063359
.section .bss
.balign 4
snapshot: .space 32
