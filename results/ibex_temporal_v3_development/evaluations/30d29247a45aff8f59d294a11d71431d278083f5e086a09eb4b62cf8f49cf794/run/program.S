.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 0
  li a3, 1
  li a4, 0
  li a5, 1
  li a6, 0
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
  li t6, 256
.Lloop0:
  divu a4, a0, a0
  divu a6, a2, a0
  divu a0, a4, a0
  divu a2, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  bnez a1, .Lskip1_0
  mv a5, a0
.Lskip1_0:
  bnez a3, .Lskip1_1
  mv a7, a2
.Lskip1_1:
  bnez a5, .Lskip1_2
  mv a1, a4
.Lskip1_2:
  bnez a7, .Lskip1_3
  mv a3, a6
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 512
.Lloop2:
  xor a0, a0, a0
  xor a1, a1, a1
  xor a2, a2, a2
  xor a3, a3, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
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
