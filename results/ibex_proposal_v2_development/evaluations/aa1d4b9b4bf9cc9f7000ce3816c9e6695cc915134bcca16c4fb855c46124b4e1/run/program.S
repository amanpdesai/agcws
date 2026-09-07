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
  li t6, 146
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  mul a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  xor a4, a2, a3
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 146
.Lloop1:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  mul a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  add a2, a0, a1
  xor a4, a2, a3
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 146
.Lloop2:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  mul a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  add a2, a0, a1
  xor a4, a2, a3
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 146
.Lloop3:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  mul a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a2, a0, a1
  xor a4, a2, a3
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
  .word 10001
  .word 2654445770
  .word 1013914243
  .word 3668350012
  .word 2027818485
  .word 387286958
  .word 3041722727
  .word 1401191200
  .word 4055626969
  .word 2415095442
  .word 774563915
  .word 3428999684
  .word 1788468157
  .word 147936630
  .word 2802372399
  .word 1161840872
  .word 3816276641
  .word 2175745114
  .word 535213587
  .word 3189649356
  .word 1549117829
  .word 4203553598
  .word 2563022071
  .word 922490544
  .word 3576926313
  .word 1936394786
  .word 295863259
  .word 2950299028
  .word 1309767501
  .word 3964203270
  .word 2323671743
  .word 683140216
  .word 3337575985
  .word 1697044458
  .word 56512931
  .word 2710948700
  .word 1070417173
  .word 3724852942
  .word 2084321415
  .word 443789888
  .word 3098225657
  .word 1457694130
  .word 4112129899
  .word 2471598372
  .word 831066845
  .word 3485502614
  .word 1844971087
  .word 204439560
  .word 2858875329
  .word 1218343802
  .word 3872779571
  .word 2232248044
  .word 591716517
  .word 3246152286
  .word 1605620759
  .word 4260056528
  .word 2619525001
  .word 978993474
  .word 3633429243
  .word 1992897716
  .word 352366189
  .word 3006801958
  .word 1366270431
  .word 4020706200
.section .bss
.balign 4
snapshot: .space 32
