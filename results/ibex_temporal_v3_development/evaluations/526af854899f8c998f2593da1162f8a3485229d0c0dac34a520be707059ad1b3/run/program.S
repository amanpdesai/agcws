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
  li t6, 256
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  add a6, a4, a5
  xor a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  bnez a0, .Lskip1_0
  mv a2, a1
.Lskip1_0:
  bnez a2, .Lskip1_1
  mv a4, a3
.Lskip1_1:
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 40000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 512
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 1234567895
  .word 3889003664
  .word 2248472137
  .word 607940610
  .word 3262376379
  .word 1621844852
  .word 4276280621
  .word 2635749094
  .word 995217567
  .word 3649653336
  .word 2009121809
  .word 368590282
  .word 3023026051
  .word 1382494524
  .word 4036930293
  .word 2396398766
  .word 755867239
  .word 3410303008
  .word 1769771481
  .word 129239954
  .word 2783675723
  .word 1143144196
  .word 3797579965
  .word 2157048438
  .word 516516911
  .word 3170952680
  .word 1530421153
  .word 4184856922
  .word 2544325395
  .word 903793868
  .word 3558229637
  .word 1917698110
  .word 277166583
  .word 2931602352
  .word 1291070825
  .word 3945506594
  .word 2304975067
  .word 664443540
  .word 3318879309
  .word 1678347782
  .word 37816255
  .word 2692252024
  .word 1051720497
  .word 3706156266
  .word 2065624739
  .word 425093212
  .word 3079528981
  .word 1438997454
  .word 4093433223
  .word 2452901696
  .word 812370169
  .word 3466805938
  .word 1826274411
  .word 185742884
  .word 2840178653
  .word 1199647126
  .word 3854082895
  .word 2213551368
  .word 573019841
  .word 3227455610
  .word 1586924083
  .word 4241359852
  .word 2600828325
  .word 960296798
.section .bss
.balign 4
snapshot: .space 32
