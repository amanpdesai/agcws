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
  li a5, 4294967295
  li a6, 4294967295
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 42911
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 376
.Lloop0:
  bnez a1, .Lskip0_0
  mv a3, a0
.Lskip0_0:
  bnez a3, .Lskip0_1
  mv a4, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 68521
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 46
.Lloop1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 74609
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 192
.Lloop2:
  sll a3, a6, a0
  srl a2, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 102693
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 208
.Lloop3:
  srl a6, a1, a1
  xor a5, a0, a3
  srl a2, a4, a7
  add a0, a2, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 117607
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 88
.Lloop4:
  sll a5, a1, a5
  xor a1, a0, a3
  add a2, a6, a2
  srl a5, a7, a2
  xor a6, a1, a6
  add a2, a7, a0
  sll a5, a0, a2
  and a0, a6, a5
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 159752
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 80
.Lloop5:
  bnez a4, .Lskip5_0
  mv a2, a3
.Lskip5_0:
  bnez a7, .Lskip5_1
  mv a1, a2
.Lskip5_1:
  bnez a6, .Lskip5_2
  mv a4, a7
.Lskip5_2:
  bnez a2, .Lskip5_3
  mv a7, a5
.Lskip5_3:
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 178318
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 736
.Lloop6:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 1755103660
  .word 114572133
  .word 2769007902
  .word 1128476375
  .word 3782912144
  .word 2142380617
  .word 501849090
  .word 3156284859
  .word 1515753332
  .word 4170189101
  .word 2529657574
  .word 889126047
  .word 3543561816
  .word 1903030289
  .word 262498762
  .word 2916934531
  .word 1276403004
  .word 3930838773
  .word 2290307246
  .word 649775719
  .word 3304211488
  .word 1663679961
  .word 23148434
  .word 2677584203
  .word 1037052676
  .word 3691488445
  .word 2050956918
  .word 410425391
  .word 3064861160
  .word 1424329633
  .word 4078765402
  .word 2438233875
  .word 797702348
  .word 3452138117
  .word 1811606590
  .word 171075063
  .word 2825510832
  .word 1184979305
  .word 3839415074
  .word 2198883547
  .word 558352020
  .word 3212787789
  .word 1572256262
  .word 4226692031
  .word 2586160504
  .word 945628977
  .word 3600064746
  .word 1959533219
  .word 319001692
  .word 2973437461
  .word 1332905934
  .word 3987341703
  .word 2346810176
  .word 706278649
  .word 3360714418
  .word 1720182891
  .word 79651364
  .word 2734087133
  .word 1093555606
  .word 3747991375
  .word 2107459848
  .word 466928321
  .word 3121364090
  .word 1480832563
.section .bss
.balign 4
snapshot: .space 32
