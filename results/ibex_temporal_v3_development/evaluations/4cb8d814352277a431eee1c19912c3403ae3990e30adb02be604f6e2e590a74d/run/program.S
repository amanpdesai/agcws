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
  li t6, 341
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 341
.Lloop1:
  mul a3, a3, a4
  or a4, a4, a5
  srl a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  mul a3, a3, a4
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 341
.Lloop2:
  divu a6, a6, a7
  add a7, a0, a1
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a6, a6, a7
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 341
.Lloop3:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  add a4, a4, a5
  mul a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
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
  .word 789123456
  .word 3443559225
  .word 1803027698
  .word 162496171
  .word 2816931940
  .word 1176400413
  .word 3830836182
  .word 2190304655
  .word 549773128
  .word 3204208897
  .word 1563677370
  .word 4218113139
  .word 2577581612
  .word 937050085
  .word 3591485854
  .word 1950954327
  .word 310422800
  .word 2964858569
  .word 1324327042
  .word 3978762811
  .word 2338231284
  .word 697699757
  .word 3352135526
  .word 1711603999
  .word 71072472
  .word 2725508241
  .word 1084976714
  .word 3739412483
  .word 2098880956
  .word 458349429
  .word 3112785198
  .word 1472253671
  .word 4126689440
  .word 2486157913
  .word 845626386
  .word 3500062155
  .word 1859530628
  .word 218999101
  .word 2873434870
  .word 1232903343
  .word 3887339112
  .word 2246807585
  .word 606276058
  .word 3260711827
  .word 1620180300
  .word 4274616069
  .word 2634084542
  .word 993553015
  .word 3647988784
  .word 2007457257
  .word 366925730
  .word 3021361499
  .word 1380829972
  .word 4035265741
  .word 2394734214
  .word 754202687
  .word 3408638456
  .word 1768106929
  .word 127575402
  .word 2782011171
  .word 1141479644
  .word 3795915413
  .word 2155383886
  .word 514852359
.section .bss
.balign 4
snapshot: .space 32
