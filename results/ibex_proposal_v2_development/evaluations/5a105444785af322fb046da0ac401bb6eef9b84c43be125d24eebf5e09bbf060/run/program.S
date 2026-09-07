.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
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
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  mul a3, a3, a4
  mul a4, a4, a5
  add a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 112
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a1, a2
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a2, a3
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a3, a4
.Lskip1_3:
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a0, .Ltail_skip1_0
  mv a0, a1
.Ltail_skip1_0:
  bnez a1, .Ltail_skip1_1
  mv a1, a2
.Ltail_skip1_1:
  bnez a2, .Ltail_skip1_2
  mv a2, a3
.Ltail_skip1_2:
  bnez a3, .Ltail_skip1_3
  mv a3, a4
.Ltail_skip1_3:
  li s9, 70000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 125
.Lloop2:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  mul a4, a4, a5
  divu a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 130000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 124
.Lloop3:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
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
  .word 1516171819
  .word 4170607588
  .word 2530076061
  .word 889544534
  .word 3543980303
  .word 1903448776
  .word 262917249
  .word 2917353018
  .word 1276821491
  .word 3931257260
  .word 2290725733
  .word 650194206
  .word 3304629975
  .word 1664098448
  .word 23566921
  .word 2678002690
  .word 1037471163
  .word 3691906932
  .word 2051375405
  .word 410843878
  .word 3065279647
  .word 1424748120
  .word 4079183889
  .word 2438652362
  .word 798120835
  .word 3452556604
  .word 1812025077
  .word 171493550
  .word 2825929319
  .word 1185397792
  .word 3839833561
  .word 2199302034
  .word 558770507
  .word 3213206276
  .word 1572674749
  .word 4227110518
  .word 2586578991
  .word 946047464
  .word 3600483233
  .word 1959951706
  .word 319420179
  .word 2973855948
  .word 1333324421
  .word 3987760190
  .word 2347228663
  .word 706697136
  .word 3361132905
  .word 1720601378
  .word 80069851
  .word 2734505620
  .word 1093974093
  .word 3748409862
  .word 2107878335
  .word 467346808
  .word 3121782577
  .word 1481251050
  .word 4135686819
  .word 2495155292
  .word 854623765
  .word 3509059534
  .word 1868528007
  .word 227996480
  .word 2882432249
  .word 1241900722
.section .bss
.balign 4
snapshot: .space 32
