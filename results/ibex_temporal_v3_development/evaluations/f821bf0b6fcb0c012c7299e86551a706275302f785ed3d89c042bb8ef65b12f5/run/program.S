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
  li t6, 280
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  mul a6, a4, a5
  srl a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 280
.Lloop1:
  add a2, a0, a1
  xor a4, a2, a3
  mul a6, a4, a5
  and a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 40000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 259
.Lloop2:
  add a2, a0, a1
  xor a4, a2, a3
  mul a6, a4, a5
  sll a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  add a2, a0, a1
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
  .word 1618033988
  .word 4272469757
  .word 2631938230
  .word 991406703
  .word 3645842472
  .word 2005310945
  .word 364779418
  .word 3019215187
  .word 1378683660
  .word 4033119429
  .word 2392587902
  .word 752056375
  .word 3406492144
  .word 1765960617
  .word 125429090
  .word 2779864859
  .word 1139333332
  .word 3793769101
  .word 2153237574
  .word 512706047
  .word 3167141816
  .word 1526610289
  .word 4181046058
  .word 2540514531
  .word 899983004
  .word 3554418773
  .word 1913887246
  .word 273355719
  .word 2927791488
  .word 1287259961
  .word 3941695730
  .word 2301164203
  .word 660632676
  .word 3315068445
  .word 1674536918
  .word 34005391
  .word 2688441160
  .word 1047909633
  .word 3702345402
  .word 2061813875
  .word 421282348
  .word 3075718117
  .word 1435186590
  .word 4089622359
  .word 2449090832
  .word 808559305
  .word 3462995074
  .word 1822463547
  .word 181932020
  .word 2836367789
  .word 1195836262
  .word 3850272031
  .word 2209740504
  .word 569208977
  .word 3223644746
  .word 1583113219
  .word 4237548988
  .word 2597017461
  .word 956485934
  .word 3610921703
  .word 1970390176
  .word 329858649
  .word 2984294418
  .word 1343762891
.section .bss
.balign 4
snapshot: .space 32
