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
  li t6, 143
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  mul a4, a4, a5
  divu a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  mul a4, a4, a5
  divu a5, a5, a6
  li s9, 15000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 118
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a1, a2
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a2, a3
.Lskip1_2:
  add a3, a3, a4
  xor a4, a4, a5
  sll a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a0, .Ltail_skip1_0
  mv a0, a1
.Ltail_skip1_0:
  bnez a1, .Ltail_skip1_1
  mv a1, a2
.Ltail_skip1_1:
  bnez a2, .Ltail_skip1_2
  mv a2, a3
.Ltail_skip1_2:
  add a3, a3, a4
  xor a4, a4, a5
  sll a5, a5, a6
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 112
.Lloop2:
  divu a0, a0, a1
  divu a1, a1, a2
  mul a2, a2, a3
  mul a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a1
  divu a1, a1, a2
  mul a2, a2, a3
  mul a3, a3, a4
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 137
.Lloop3:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
  .word 1618033989
  .word 4272469758
  .word 2631938231
  .word 991406704
  .word 3645842473
  .word 2005310946
  .word 364779419
  .word 3019215188
  .word 1378683661
  .word 4033119430
  .word 2392587903
  .word 752056376
  .word 3406492145
  .word 1765960618
  .word 125429091
  .word 2779864860
  .word 1139333333
  .word 3793769102
  .word 2153237575
  .word 512706048
  .word 3167141817
  .word 1526610290
  .word 4181046059
  .word 2540514532
  .word 899983005
  .word 3554418774
  .word 1913887247
  .word 273355720
  .word 2927791489
  .word 1287259962
  .word 3941695731
  .word 2301164204
  .word 660632677
  .word 3315068446
  .word 1674536919
  .word 34005392
  .word 2688441161
  .word 1047909634
  .word 3702345403
  .word 2061813876
  .word 421282349
  .word 3075718118
  .word 1435186591
  .word 4089622360
  .word 2449090833
  .word 808559306
  .word 3462995075
  .word 1822463548
  .word 181932021
  .word 2836367790
  .word 1195836263
  .word 3850272032
  .word 2209740505
  .word 569208978
  .word 3223644747
  .word 1583113220
  .word 4237548989
  .word 2597017462
  .word 956485935
  .word 3610921704
  .word 1970390177
  .word 329858650
  .word 2984294419
  .word 1343762892
.section .bss
.balign 4
snapshot: .space 32
