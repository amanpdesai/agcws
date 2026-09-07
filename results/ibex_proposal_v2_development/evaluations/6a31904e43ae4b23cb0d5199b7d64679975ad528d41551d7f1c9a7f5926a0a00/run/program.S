.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 270
.Lloop0:
  xor a0, a0, a1
  sll a1, a1, a0
  add a6, a6, a7
  and a7, a7, a6
  mul a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 15000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 40
.Lloop1:
  srl a2, a2, a3
  xor a3, a3, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 30000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 40
.Lloop2:
  srl a4, a4, a5
  xor a5, a5, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 250
.Lloop3:
  xor a0, a0, a1
  sll a1, a1, a0
  add a6, a6, a7
  and a7, a7, a6
  mul a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 100000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 267
.Lloop4:
  xor a0, a0, a1
  sll a1, a1, a0
  add a6, a6, a7
  and a7, a7, a6
  mul a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  xor a0, a0, a1
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
  .word 987654321
  .word 3642090090
  .word 2001558563
  .word 361027036
  .word 3015462805
  .word 1374931278
  .word 4029367047
  .word 2388835520
  .word 748303993
  .word 3402739762
  .word 1762208235
  .word 121676708
  .word 2776112477
  .word 1135580950
  .word 3790016719
  .word 2149485192
  .word 508953665
  .word 3163389434
  .word 1522857907
  .word 4177293676
  .word 2536762149
  .word 896230622
  .word 3550666391
  .word 1910134864
  .word 269603337
  .word 2924039106
  .word 1283507579
  .word 3937943348
  .word 2297411821
  .word 656880294
  .word 3311316063
  .word 1670784536
  .word 30253009
  .word 2684688778
  .word 1044157251
  .word 3698593020
  .word 2058061493
  .word 417529966
  .word 3071965735
  .word 1431434208
  .word 4085869977
  .word 2445338450
  .word 804806923
  .word 3459242692
  .word 1818711165
  .word 178179638
  .word 2832615407
  .word 1192083880
  .word 3846519649
  .word 2205988122
  .word 565456595
  .word 3219892364
  .word 1579360837
  .word 4233796606
  .word 2593265079
  .word 952733552
  .word 3607169321
  .word 1966637794
  .word 326106267
  .word 2980542036
  .word 1340010509
  .word 3994446278
  .word 2353914751
  .word 713383224
.section .bss
.balign 4
snapshot: .space 32
