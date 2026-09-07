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
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  and a2, a5, a0
  or a2, a5, a3
  and a1, a2, a1
  or a2, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  divu a3, a5, a1
  divu a7, a5, a0
  divu a4, a6, a1
  divu a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  bnez a0, .Lskip3_1
  mv a0, a1
.Lskip3_1:
  divu a3, a6, a4
  or a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 40000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 192
.Lloop4:
  bnez a0, .Lskip4_0
  mv a5, a1
.Lskip4_0:
  bnez a1, .Lskip4_1
  mv a2, a0
.Lskip4_1:
  bnez a5, .Lskip4_2
  mv a3, a1
.Lskip4_2:
  bnez a6, .Lskip4_3
  mv a3, a1
.Lskip4_3:
  bnez a5, .Lskip4_4
  mv a6, a0
.Lskip4_4:
  bnez a4, .Lskip4_5
  mv a7, a1
.Lskip4_5:
  bnez a3, .Lskip4_6
  mv a6, a1
.Lskip4_6:
  bnez a1, .Lskip4_7
  mv a7, a0
.Lskip4_7:
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 3329196735
  .word 1688665208
  .word 48133681
  .word 2702569450
  .word 1062037923
  .word 3716473692
  .word 2075942165
  .word 435410638
  .word 3089846407
  .word 1449314880
  .word 4103750649
  .word 2463219122
  .word 822687595
  .word 3477123364
  .word 1836591837
  .word 196060310
  .word 2850496079
  .word 1209964552
  .word 3864400321
  .word 2223868794
  .word 583337267
  .word 3237773036
  .word 1597241509
  .word 4251677278
  .word 2611145751
  .word 970614224
  .word 3625049993
  .word 1984518466
  .word 343986939
  .word 2998422708
  .word 1357891181
  .word 4012326950
  .word 2371795423
  .word 731263896
  .word 3385699665
  .word 1745168138
  .word 104636611
  .word 2759072380
  .word 1118540853
  .word 3772976622
  .word 2132445095
  .word 491913568
  .word 3146349337
  .word 1505817810
  .word 4160253579
  .word 2519722052
  .word 879190525
  .word 3533626294
  .word 1893094767
  .word 252563240
  .word 2906999009
  .word 1266467482
  .word 3920903251
  .word 2280371724
  .word 639840197
  .word 3294275966
  .word 1653744439
  .word 13212912
  .word 2667648681
  .word 1027117154
  .word 3681552923
  .word 2041021396
  .word 400489869
  .word 3054925638
.section .bss
.balign 4
snapshot: .space 32
