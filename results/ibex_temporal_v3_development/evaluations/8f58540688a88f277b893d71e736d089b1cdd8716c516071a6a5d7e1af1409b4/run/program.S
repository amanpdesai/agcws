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
  li t6, 341
.Lloop0:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  bnez a0, .Lskip0_4
  mv a2, a1
.Lskip0_4:
  bnez a2, .Lskip0_5
  mv a4, a3
.Lskip0_5:
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  add a4, a2, a3
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 341
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
  .word 1234567890
  .word 3889003659
  .word 2248472132
  .word 607940605
  .word 3262376374
  .word 1621844847
  .word 4276280616
  .word 2635749089
  .word 995217562
  .word 3649653331
  .word 2009121804
  .word 368590277
  .word 3023026046
  .word 1382494519
  .word 4036930288
  .word 2396398761
  .word 755867234
  .word 3410303003
  .word 1769771476
  .word 129239949
  .word 2783675718
  .word 1143144191
  .word 3797579960
  .word 2157048433
  .word 516516906
  .word 3170952675
  .word 1530421148
  .word 4184856917
  .word 2544325390
  .word 903793863
  .word 3558229632
  .word 1917698105
  .word 277166578
  .word 2931602347
  .word 1291070820
  .word 3945506589
  .word 2304975062
  .word 664443535
  .word 3318879304
  .word 1678347777
  .word 37816250
  .word 2692252019
  .word 1051720492
  .word 3706156261
  .word 2065624734
  .word 425093207
  .word 3079528976
  .word 1438997449
  .word 4093433218
  .word 2452901691
  .word 812370164
  .word 3466805933
  .word 1826274406
  .word 185742879
  .word 2840178648
  .word 1199647121
  .word 3854082890
  .word 2213551363
  .word 573019836
  .word 3227455605
  .word 1586924078
  .word 4241359847
  .word 2600828320
  .word 960296793
.section .bss
.balign 4
snapshot: .space 32
