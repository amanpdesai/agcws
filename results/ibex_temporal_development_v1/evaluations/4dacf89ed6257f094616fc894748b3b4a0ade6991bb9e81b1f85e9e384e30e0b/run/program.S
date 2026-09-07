.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 1
  li a2, 1076035761
  li a3, 4294967295
  li a4, 1
  li a5, 1
  li a6, 17
  li a7, 4294967295
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
  add a5, a7, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a5, a4, a6
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a0, a6, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  srl a3, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  bnez a5, .Lskip2_0
  mv a3, a0
.Lskip2_0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  xor a4, a0, a3
  srl a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  bnez a4, .Lskip3_0
  mv a2, a5
.Lskip3_0:
  divu a7, a7, a7
  add a2, a3, a3
  xor a0, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop3
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
  .word 100000004
  .word 2754435773
  .word 1113904246
  .word 3768340015
  .word 2127808488
  .word 487276961
  .word 3141712730
  .word 1501181203
  .word 4155616972
  .word 2515085445
  .word 874553918
  .word 3528989687
  .word 1888458160
  .word 247926633
  .word 2902362402
  .word 1261830875
  .word 3916266644
  .word 2275735117
  .word 635203590
  .word 3289639359
  .word 1649107832
  .word 8576305
  .word 2663012074
  .word 1022480547
  .word 3676916316
  .word 2036384789
  .word 395853262
  .word 3050289031
  .word 1409757504
  .word 4064193273
  .word 2423661746
  .word 783130219
  .word 3437565988
  .word 1797034461
  .word 156502934
  .word 2810938703
  .word 1170407176
  .word 3824842945
  .word 2184311418
  .word 543779891
  .word 3198215660
  .word 1557684133
  .word 4212119902
  .word 2571588375
  .word 931056848
  .word 3585492617
  .word 1944961090
  .word 304429563
  .word 2958865332
  .word 1318333805
  .word 3972769574
  .word 2332238047
  .word 691706520
  .word 3346142289
  .word 1705610762
  .word 65079235
  .word 2719515004
  .word 1078983477
  .word 3733419246
  .word 2092887719
  .word 452356192
  .word 3106791961
  .word 1466260434
  .word 4120696203
.section .bss
.balign 4
snapshot: .space 32
