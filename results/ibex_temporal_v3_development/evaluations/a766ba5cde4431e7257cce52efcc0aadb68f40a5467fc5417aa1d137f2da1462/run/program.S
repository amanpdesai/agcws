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
  li t6, 163
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  add a5, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 39
.Lloop1:
  xor a6, a5, a2
  divu a7, a6, a1
  bnez a7, .Lskip1_2
  mv a0, a3
.Lskip1_2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 38
.Lloop2:
  add a1, a0, a1
  xor a2, a1, a3
  srl a3, a2, a4
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  add a1, a0, a1
  xor a2, a1, a3
  srl a3, a2, a4
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 38
.Lloop3:
  mul a4, a3, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  add a6, a5, a0
  xor a7, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  mul a4, a3, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  add a6, a5, a0
  li s9, 100000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 285
.Lloop4:
  sll a0, a7, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a2, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
  sll a0, a7, a2
  li s9, 125000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 168
.Lloop5:
  xor a3, a2, a3
  mul a4, a3, a4
  sll a5, a4, a5
  divu a6, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop5
  xor a3, a2, a3
  mul a4, a3, a4
  li s9, 150000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 168
.Lloop6:
  bnez a6, .Lskip6_0
  mv a7, a7
.Lskip6_0:
  add a0, a7, a0
  xor a1, a0, a1
  srl a2, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop6
  bnez a6, .Ltail_skip6_0
  mv a7, a7
.Ltail_skip6_0:
  add a0, a7, a0
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
  .word 444555666
  .word 3098991435
  .word 1458459908
  .word 4112895677
  .word 2472364150
  .word 831832623
  .word 3486268392
  .word 1845736865
  .word 205205338
  .word 2859641107
  .word 1219109580
  .word 3873545349
  .word 2233013822
  .word 592482295
  .word 3246918064
  .word 1606386537
  .word 4260822306
  .word 2620290779
  .word 979759252
  .word 3634195021
  .word 1993663494
  .word 353131967
  .word 3007567736
  .word 1367036209
  .word 4021471978
  .word 2380940451
  .word 740408924
  .word 3394844693
  .word 1754313166
  .word 113781639
  .word 2768217408
  .word 1127685881
  .word 3782121650
  .word 2141590123
  .word 501058596
  .word 3155494365
  .word 1514962838
  .word 4169398607
  .word 2528867080
  .word 888335553
  .word 3542771322
  .word 1902239795
  .word 261708268
  .word 2916144037
  .word 1275612510
  .word 3930048279
  .word 2289516752
  .word 648985225
  .word 3303420994
  .word 1662889467
  .word 22357940
  .word 2676793709
  .word 1036262182
  .word 3690697951
  .word 2050166424
  .word 409634897
  .word 3064070666
  .word 1423539139
  .word 4077974908
  .word 2437443381
  .word 796911854
  .word 3451347623
  .word 1810816096
  .word 170284569
.section .bss
.balign 4
snapshot: .space 32
