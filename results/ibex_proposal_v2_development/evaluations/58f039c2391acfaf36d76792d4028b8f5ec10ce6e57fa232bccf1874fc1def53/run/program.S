.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 381541715
  li a1, 17
  li a2, 0
  li a3, 1520735261
  li a4, 17
  li a5, 31
  li a6, 31
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 11147
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 204
.Lloop0:
  xor a2, a1, a0
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 38646
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 392
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 137458
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 274
.Lloop2:
  xor a3, a3, a0
  sll a6, a3, a1
  sll a4, a1, a0
  and a6, a7, a0
  and a7, a6, a0
  add a2, a5, a0
  or a4, a2, a1
  srl a5, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 160955
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 880
.Lloop3:
  bnez a3, .Lskip3_0
  mv a3, a1
.Lskip3_0:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 176133
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 56
.Lloop4:
  bnez a7, .Lskip4_0
  mv a4, a4
.Lskip4_0:
  bnez a5, .Lskip4_1
  mv a7, a3
.Lskip4_1:
  bnez a2, .Lskip4_2
  mv a1, a5
.Lskip4_2:
  bnez a6, .Lskip4_3
  mv a4, a0
.Lskip4_3:
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
  .word 866767076
  .word 3521202845
  .word 1880671318
  .word 240139791
  .word 2894575560
  .word 1254044033
  .word 3908479802
  .word 2267948275
  .word 627416748
  .word 3281852517
  .word 1641320990
  .word 789463
  .word 2655225232
  .word 1014693705
  .word 3669129474
  .word 2028597947
  .word 388066420
  .word 3042502189
  .word 1401970662
  .word 4056406431
  .word 2415874904
  .word 775343377
  .word 3429779146
  .word 1789247619
  .word 148716092
  .word 2803151861
  .word 1162620334
  .word 3817056103
  .word 2176524576
  .word 535993049
  .word 3190428818
  .word 1549897291
  .word 4204333060
  .word 2563801533
  .word 923270006
  .word 3577705775
  .word 1937174248
  .word 296642721
  .word 2951078490
  .word 1310546963
  .word 3964982732
  .word 2324451205
  .word 683919678
  .word 3338355447
  .word 1697823920
  .word 57292393
  .word 2711728162
  .word 1071196635
  .word 3725632404
  .word 2085100877
  .word 444569350
  .word 3099005119
  .word 1458473592
  .word 4112909361
  .word 2472377834
  .word 831846307
  .word 3486282076
  .word 1845750549
  .word 205219022
  .word 2859654791
  .word 1219123264
  .word 3873559033
  .word 2233027506
  .word 592495979
.section .bss
.balign 4
snapshot: .space 32
