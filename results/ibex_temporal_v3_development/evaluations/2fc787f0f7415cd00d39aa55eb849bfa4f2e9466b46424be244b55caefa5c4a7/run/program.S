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
  li t6, 161
.Lloop0:
  add a0, a0, a1
  xor a1, a0, a2
  mul a2, a1, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  sll a4, a2, a5
  divu a5, a3, a6
  bnez a5, .Lskip0_7
  mv a6, a7
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a0, a2
  mul a2, a1, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 27
.Lloop1:
  add a7, a6, a0
  xor a0, a7, a1
  srl a1, a0, a2
  mul a2, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 27
.Lloop2:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  add a4, a3, a0
  xor a5, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 27
.Lloop3:
  mul a6, a5, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  sll a0, a6, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 120000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 323
.Lloop4:
  divu a1, a0, a2
  bnez a1, .Lskip4_1
  mv a2, a3
.Lskip4_1:
  add a3, a2, a4
  xor a4, a3, a5
  addi t6, t6, -1
  bnez t6, .Lloop4
  divu a1, a0, a2
  li s9, 150000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 161
.Lloop5:
  srl a5, a4, a6
  mul a6, a5, a7
  add a7, a6, a0
  xor a0, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
  srl a5, a4, a6
  mul a6, a5, a7
  add a7, a6, a0
  li s9, 180000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 134
.Lloop6:
  sll a1, a0, a2
  divu a2, a1, a3
  bnez a2, .Lskip6_2
  mv a3, a4
.Lskip6_2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
  sll a1, a0, a2
  divu a2, a1, a3
  bnez a2, .Ltail_skip6_2
  mv a3, a4
.Ltail_skip6_2:
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
  .word 111222333
  .word 2765658102
  .word 1125126575
  .word 3779562344
  .word 2139030817
  .word 498499290
  .word 3152935059
  .word 1512403532
  .word 4166839301
  .word 2526307774
  .word 885776247
  .word 3540212016
  .word 1899680489
  .word 259148962
  .word 2913584731
  .word 1273053204
  .word 3927488973
  .word 2286957446
  .word 646425919
  .word 3300861688
  .word 1660330161
  .word 19798634
  .word 2674234403
  .word 1033702876
  .word 3688138645
  .word 2047607118
  .word 407075591
  .word 3061511360
  .word 1420979833
  .word 4075415602
  .word 2434884075
  .word 794352548
  .word 3448788317
  .word 1808256790
  .word 167725263
  .word 2822161032
  .word 1181629505
  .word 3836065274
  .word 2195533747
  .word 555002220
  .word 3209437989
  .word 1568906462
  .word 4223342231
  .word 2582810704
  .word 942279177
  .word 3596714946
  .word 1956183419
  .word 315651892
  .word 2970087661
  .word 1329556134
  .word 3983991903
  .word 2343460376
  .word 702928849
  .word 3357364618
  .word 1716833091
  .word 76301564
  .word 2730737333
  .word 1090205806
  .word 3744641575
  .word 2104110048
  .word 463578521
  .word 3118014290
  .word 1477482763
  .word 4131918532
.section .bss
.balign 4
snapshot: .space 32
