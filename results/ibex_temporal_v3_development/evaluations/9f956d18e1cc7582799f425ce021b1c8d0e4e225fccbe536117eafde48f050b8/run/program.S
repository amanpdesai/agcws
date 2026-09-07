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
  li s9, 10284
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 152
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
  add a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 27105
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 240
.Lloop1:
  and a2, a5, a0
  add a5, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 99499
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 45
.Lloop2:
  divu a3, a3, a0
  divu a7, a1, a0
  divu a3, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a3, a3, a0
  li s9, 125616
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 260
.Lloop3:
  or a2, a5, a3
  and a1, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 142089
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 70
.Lloop4:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  bnez a0, .Lskip4_1
  mv a0, a1
.Lskip4_1:
  divu a3, a6, a4
  or a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 150553
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 420
.Lloop5:
  or a2, a0, a2
  add a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 157844
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 270
.Lloop6:
  divu a3, a4, a0
  divu a3, a5, a1
  divu a4, a0, a1
  divu a3, a2, a0
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
  .word 3329196734
  .word 1688665207
  .word 48133680
  .word 2702569449
  .word 1062037922
  .word 3716473691
  .word 2075942164
  .word 435410637
  .word 3089846406
  .word 1449314879
  .word 4103750648
  .word 2463219121
  .word 822687594
  .word 3477123363
  .word 1836591836
  .word 196060309
  .word 2850496078
  .word 1209964551
  .word 3864400320
  .word 2223868793
  .word 583337266
  .word 3237773035
  .word 1597241508
  .word 4251677277
  .word 2611145750
  .word 970614223
  .word 3625049992
  .word 1984518465
  .word 343986938
  .word 2998422707
  .word 1357891180
  .word 4012326949
  .word 2371795422
  .word 731263895
  .word 3385699664
  .word 1745168137
  .word 104636610
  .word 2759072379
  .word 1118540852
  .word 3772976621
  .word 2132445094
  .word 491913567
  .word 3146349336
  .word 1505817809
  .word 4160253578
  .word 2519722051
  .word 879190524
  .word 3533626293
  .word 1893094766
  .word 252563239
  .word 2906999008
  .word 1266467481
  .word 3920903250
  .word 2280371723
  .word 639840196
  .word 3294275965
  .word 1653744438
  .word 13212911
  .word 2667648680
  .word 1027117153
  .word 3681552922
  .word 2041021395
  .word 400489868
  .word 3054925637
.section .bss
.balign 4
snapshot: .space 32
