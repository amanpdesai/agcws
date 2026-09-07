.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 17
  li a2, 4275878552
  li a3, 324508639
  li a4, 2863311530
  li a5, 1431655765
  li a6, 7
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 128
.Lloop0:
  and a2, a2, a1
  or a3, a3, a1
  sll a4, a4, a1
  srl a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  xor a2, a2, a1
  xor a3, a3, a1
  xor a4, a4, a1
  xor a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  mul a2, a2, a1
  mul a3, a3, a1
  mul a4, a4, a1
  mul a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a2, a2, a1
  divu a3, a3, a1
  divu a4, a4, a1
  divu a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 100000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 128
.Lloop4:
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 125000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 128
.Lloop5:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  add a2, a2, a1
  xor a3, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 150000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 128
.Lloop6:
  bnez a0, .Lskip6_0
  mv a2, a1
.Lskip6_0:
  bnez a2, .Lskip6_1
  mv a3, a1
.Lskip6_1:
  xor a2, a2, a1
  bnez a2, .Lskip6_3
  mv a4, a3
.Lskip6_3:
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 175000
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 128
.Lloop7:
  divu a2, a2, a1
  divu a3, a3, a1
  divu a4, a4, a1
  divu a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 305419896
  .word 2959855665
  .word 1319324138
  .word 3973759907
  .word 2333228380
  .word 692696853
  .word 3347132622
  .word 1706601095
  .word 66069568
  .word 2720505337
  .word 1079973810
  .word 3734409579
  .word 2093878052
  .word 453346525
  .word 3107782294
  .word 1467250767
  .word 4121686536
  .word 2481155009
  .word 840623482
  .word 3495059251
  .word 1854527724
  .word 213996197
  .word 2868431966
  .word 1227900439
  .word 3882336208
  .word 2241804681
  .word 601273154
  .word 3255708923
  .word 1615177396
  .word 4269613165
  .word 2629081638
  .word 988550111
  .word 3642985880
  .word 2002454353
  .word 361922826
  .word 3016358595
  .word 1375827068
  .word 4030262837
  .word 2389731310
  .word 749199783
  .word 3403635552
  .word 1763104025
  .word 122572498
  .word 2777008267
  .word 1136476740
  .word 3790912509
  .word 2150380982
  .word 509849455
  .word 3164285224
  .word 1523753697
  .word 4178189466
  .word 2537657939
  .word 897126412
  .word 3551562181
  .word 1911030654
  .word 270499127
  .word 2924934896
  .word 1284403369
  .word 3938839138
  .word 2298307611
  .word 657776084
  .word 3312211853
  .word 1671680326
  .word 31148799
.section .bss
.balign 4
snapshot: .space 32
