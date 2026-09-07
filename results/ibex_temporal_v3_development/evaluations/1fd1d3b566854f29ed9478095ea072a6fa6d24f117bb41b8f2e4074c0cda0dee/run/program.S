.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 3391942914
  li a2, 4294967295
  li a3, 1553030968
  li a4, 17
  li a5, 17
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 128
.Lloop0:
  bnez a0, .Lskip0_0
  mv a5, a1
.Lskip0_0:
  bnez a1, .Lskip0_1
  mv a2, a0
.Lskip0_1:
  bnez a5, .Lskip0_2
  mv a3, a1
.Lskip0_2:
  bnez a6, .Lskip0_3
  mv a3, a1
.Lskip0_3:
  bnez a5, .Lskip0_4
  mv a6, a0
.Lskip0_4:
  bnez a4, .Lskip0_5
  mv a7, a1
.Lskip0_5:
  bnez a3, .Lskip0_6
  mv a6, a1
.Lskip0_6:
  bnez a1, .Lskip0_7
  mv a7, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 15000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  and a2, a5, a0
  or a2, a5, a3
  and a1, a2, a1
  or a2, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 204
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  divu a3, a5, a1
  divu a7, a5, a0
  divu a4, a6, a1
  divu a7, a5, a0
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
  .word 3329196736
  .word 1688665209
  .word 48133682
  .word 2702569451
  .word 1062037924
  .word 3716473693
  .word 2075942166
  .word 435410639
  .word 3089846408
  .word 1449314881
  .word 4103750650
  .word 2463219123
  .word 822687596
  .word 3477123365
  .word 1836591838
  .word 196060311
  .word 2850496080
  .word 1209964553
  .word 3864400322
  .word 2223868795
  .word 583337268
  .word 3237773037
  .word 1597241510
  .word 4251677279
  .word 2611145752
  .word 970614225
  .word 3625049994
  .word 1984518467
  .word 343986940
  .word 2998422709
  .word 1357891182
  .word 4012326951
  .word 2371795424
  .word 731263897
  .word 3385699666
  .word 1745168139
  .word 104636612
  .word 2759072381
  .word 1118540854
  .word 3772976623
  .word 2132445096
  .word 491913569
  .word 3146349338
  .word 1505817811
  .word 4160253580
  .word 2519722053
  .word 879190526
  .word 3533626295
  .word 1893094768
  .word 252563241
  .word 2906999010
  .word 1266467483
  .word 3920903252
  .word 2280371725
  .word 639840198
  .word 3294275967
  .word 1653744440
  .word 13212913
  .word 2667648682
  .word 1027117155
  .word 3681552924
  .word 2041021397
  .word 400489870
  .word 3054925639
.section .bss
.balign 4
snapshot: .space 32
