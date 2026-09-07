.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 3342486838
  li a2, 53031830
  li a3, 17
  li a4, 0
  li a5, 17
  li a6, 31
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 46754
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 102
.Lloop0:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 72101
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  and a3, a7, a5
  add a7, a3, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 127254
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 176
.Lloop2:
  mul a4, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 146698
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 21
.Lloop3:
  bnez a7, .Lskip3_0
  mv a5, a0
.Lskip3_0:
  bnez a6, .Lskip3_1
  mv a5, a1
.Lskip3_1:
  bnez a0, .Lskip3_2
  mv a7, a1
.Lskip3_2:
  bnez a2, .Lskip3_3
  mv a3, a1
.Lskip3_3:
  bnez a3, .Lskip3_4
  mv a6, a0
.Lskip3_4:
  bnez a6, .Lskip3_5
  mv a6, a0
.Lskip3_5:
  bnez a1, .Lskip3_6
  mv a2, a0
.Lskip3_6:
  bnez a6, .Lskip3_7
  mv a5, a0
.Lskip3_7:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 166615
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 102
.Lloop4:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  mul a2, a4, a5
  srl a4, a3, a5
  divu a0, a4, a6
  divu a0, a1, a3
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  srl a3, a2, a3
  xor a2, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 169841
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 79
.Lloop5:
  mul a2, a4, a5
  mul a7, a0, a7
  mul a7, a4, a0
  mul a7, a5, a0
  mul a5, a2, a4
  mul a2, a0, a3
  mul a3, a5, a3
  mul a5, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 174241
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 488
.Lloop6:
  mul a1, a1, a4
  mul a3, a3, a2
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
  .word 2344502165
  .word 703970638
  .word 3358406407
  .word 1717874880
  .word 77343353
  .word 2731779122
  .word 1091247595
  .word 3745683364
  .word 2105151837
  .word 464620310
  .word 3119056079
  .word 1478524552
  .word 4132960321
  .word 2492428794
  .word 851897267
  .word 3506333036
  .word 1865801509
  .word 225269982
  .word 2879705751
  .word 1239174224
  .word 3893609993
  .word 2253078466
  .word 612546939
  .word 3266982708
  .word 1626451181
  .word 4280886950
  .word 2640355423
  .word 999823896
  .word 3654259665
  .word 2013728138
  .word 373196611
  .word 3027632380
  .word 1387100853
  .word 4041536622
  .word 2401005095
  .word 760473568
  .word 3414909337
  .word 1774377810
  .word 133846283
  .word 2788282052
  .word 1147750525
  .word 3802186294
  .word 2161654767
  .word 521123240
  .word 3175559009
  .word 1535027482
  .word 4189463251
  .word 2548931724
  .word 908400197
  .word 3562835966
  .word 1922304439
  .word 281772912
  .word 2936208681
  .word 1295677154
  .word 3950112923
  .word 2309581396
  .word 669049869
  .word 3323485638
  .word 1682954111
  .word 42422584
  .word 2696858353
  .word 1056326826
  .word 3710762595
  .word 2070231068
.section .bss
.balign 4
snapshot: .space 32
