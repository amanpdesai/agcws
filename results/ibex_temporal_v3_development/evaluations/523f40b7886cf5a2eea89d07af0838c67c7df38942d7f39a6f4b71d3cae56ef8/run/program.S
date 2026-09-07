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
  li t6, 195
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
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 39
.Lloop1:
  divu a5, a3, a6
  bnez a5, .Lskip1_1
  mv a6, a7
.Lskip1_1:
  add a7, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 39
.Lloop2:
  xor a0, a7, a1
  srl a1, a0, a2
  mul a2, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 39
.Lloop3:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  add a4, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 120000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 234
.Lloop4:
  xor a5, a4, a1
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
  bnez t6, .Lloop4
  li s9, 150000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 234
.Lloop5:
  divu a1, a0, a2
  bnez a1, .Lskip5_1
  mv a2, a3
.Lskip5_1:
  add a3, a2, a4
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 180000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 234
.Lloop6:
  xor a4, a3, a5
  srl a5, a4, a6
  mul a6, a5, a7
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
  .word 1234567891
  .word 3889003660
  .word 2248472133
  .word 607940606
  .word 3262376375
  .word 1621844848
  .word 4276280617
  .word 2635749090
  .word 995217563
  .word 3649653332
  .word 2009121805
  .word 368590278
  .word 3023026047
  .word 1382494520
  .word 4036930289
  .word 2396398762
  .word 755867235
  .word 3410303004
  .word 1769771477
  .word 129239950
  .word 2783675719
  .word 1143144192
  .word 3797579961
  .word 2157048434
  .word 516516907
  .word 3170952676
  .word 1530421149
  .word 4184856918
  .word 2544325391
  .word 903793864
  .word 3558229633
  .word 1917698106
  .word 277166579
  .word 2931602348
  .word 1291070821
  .word 3945506590
  .word 2304975063
  .word 664443536
  .word 3318879305
  .word 1678347778
  .word 37816251
  .word 2692252020
  .word 1051720493
  .word 3706156262
  .word 2065624735
  .word 425093208
  .word 3079528977
  .word 1438997450
  .word 4093433219
  .word 2452901692
  .word 812370165
  .word 3466805934
  .word 1826274407
  .word 185742880
  .word 2840178649
  .word 1199647122
  .word 3854082891
  .word 2213551364
  .word 573019837
  .word 3227455606
  .word 1586924079
  .word 4241359848
  .word 2600828321
  .word 960296794
.section .bss
.balign 4
snapshot: .space 32
