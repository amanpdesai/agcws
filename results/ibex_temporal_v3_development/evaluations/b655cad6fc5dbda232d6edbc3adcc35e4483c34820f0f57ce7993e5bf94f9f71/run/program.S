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
  li t6, 250
.Lloop0:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 375
.Lloop1:
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
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 399
.Lloop2:
  bnez a0, .Lskip2_0
  mv a2, a1
.Lskip2_0:
  bnez a2, .Lskip2_1
  mv a4, a3
.Lskip2_1:
  xor a6, a4, a5
  and a0, a6, a7
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
  .word 1234567896
  .word 3889003665
  .word 2248472138
  .word 607940611
  .word 3262376380
  .word 1621844853
  .word 4276280622
  .word 2635749095
  .word 995217568
  .word 3649653337
  .word 2009121810
  .word 368590283
  .word 3023026052
  .word 1382494525
  .word 4036930294
  .word 2396398767
  .word 755867240
  .word 3410303009
  .word 1769771482
  .word 129239955
  .word 2783675724
  .word 1143144197
  .word 3797579966
  .word 2157048439
  .word 516516912
  .word 3170952681
  .word 1530421154
  .word 4184856923
  .word 2544325396
  .word 903793869
  .word 3558229638
  .word 1917698111
  .word 277166584
  .word 2931602353
  .word 1291070826
  .word 3945506595
  .word 2304975068
  .word 664443541
  .word 3318879310
  .word 1678347783
  .word 37816256
  .word 2692252025
  .word 1051720498
  .word 3706156267
  .word 2065624740
  .word 425093213
  .word 3079528982
  .word 1438997455
  .word 4093433224
  .word 2452901697
  .word 812370170
  .word 3466805939
  .word 1826274412
  .word 185742885
  .word 2840178654
  .word 1199647127
  .word 3854082896
  .word 2213551369
  .word 573019842
  .word 3227455611
  .word 1586924084
  .word 4241359853
  .word 2600828326
  .word 960296799
.section .bss
.balign 4
snapshot: .space 32
