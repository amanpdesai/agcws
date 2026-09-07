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
  li t6, 150
.Lloop0:
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 100
.Lloop1:
  divu a3, a3, a1
  srl a4, a4, a3
  bnez a5, .Lskip1_2
  mv a5, a4
.Lskip1_2:
  divu a1, a1, a2
  divu a3, a3, a0
  divu a5, a5, a5
  divu a4, a4, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 114
.Lloop2:
  divu a6, a6, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  divu a7, a7, a0
  divu a1, a1, a6
  divu a0, a0, a7
  divu a2, a2, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a6, a6, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 180
.Lloop3:
  add a7, a7, a0
  sll a0, a0, a7
  mul a7, a7, a0
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 175000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 132
.Lloop4:
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
  add a7, a7, a1
  xor a0, a0, a7
  sll a7, a7, a1
  mul a7, a7, a0
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
  .word 161803398
  .word 2816239167
  .word 1175707640
  .word 3830143409
  .word 2189611882
  .word 549080355
  .word 3203516124
  .word 1562984597
  .word 4217420366
  .word 2576888839
  .word 936357312
  .word 3590793081
  .word 1950261554
  .word 309730027
  .word 2964165796
  .word 1323634269
  .word 3978070038
  .word 2337538511
  .word 697006984
  .word 3351442753
  .word 1710911226
  .word 70379699
  .word 2724815468
  .word 1084283941
  .word 3738719710
  .word 2098188183
  .word 457656656
  .word 3112092425
  .word 1471560898
  .word 4125996667
  .word 2485465140
  .word 844933613
  .word 3499369382
  .word 1858837855
  .word 218306328
  .word 2872742097
  .word 1232210570
  .word 3886646339
  .word 2246114812
  .word 605583285
  .word 3260019054
  .word 1619487527
  .word 4273923296
  .word 2633391769
  .word 992860242
  .word 3647296011
  .word 2006764484
  .word 366232957
  .word 3020668726
  .word 1380137199
  .word 4034572968
  .word 2394041441
  .word 753509914
  .word 3407945683
  .word 1767414156
  .word 126882629
  .word 2781318398
  .word 1140786871
  .word 3795222640
  .word 2154691113
  .word 514159586
  .word 3168595355
  .word 1528063828
  .word 4182499597
.section .bss
.balign 4
snapshot: .space 32
