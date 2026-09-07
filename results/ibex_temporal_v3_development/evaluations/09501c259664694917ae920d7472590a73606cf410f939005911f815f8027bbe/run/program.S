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
  li t6, 300
.Lloop0:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 350
.Lloop1:
  bnez a0, .Lskip1_0
  mv a1, a2
.Lskip1_0:
  bnez a2, .Lskip1_1
  mv a3, a4
.Lskip1_1:
  bnez a4, .Lskip1_2
  mv a5, a6
.Lskip1_2:
  bnez a6, .Lskip1_3
  mv a7, a0
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 374
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
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
  .word 1234567897
  .word 3889003666
  .word 2248472139
  .word 607940612
  .word 3262376381
  .word 1621844854
  .word 4276280623
  .word 2635749096
  .word 995217569
  .word 3649653338
  .word 2009121811
  .word 368590284
  .word 3023026053
  .word 1382494526
  .word 4036930295
  .word 2396398768
  .word 755867241
  .word 3410303010
  .word 1769771483
  .word 129239956
  .word 2783675725
  .word 1143144198
  .word 3797579967
  .word 2157048440
  .word 516516913
  .word 3170952682
  .word 1530421155
  .word 4184856924
  .word 2544325397
  .word 903793870
  .word 3558229639
  .word 1917698112
  .word 277166585
  .word 2931602354
  .word 1291070827
  .word 3945506596
  .word 2304975069
  .word 664443542
  .word 3318879311
  .word 1678347784
  .word 37816257
  .word 2692252026
  .word 1051720499
  .word 3706156268
  .word 2065624741
  .word 425093214
  .word 3079528983
  .word 1438997456
  .word 4093433225
  .word 2452901698
  .word 812370171
  .word 3466805940
  .word 1826274413
  .word 185742886
  .word 2840178655
  .word 1199647128
  .word 3854082897
  .word 2213551370
  .word 573019843
  .word 3227455612
  .word 1586924085
  .word 4241359854
  .word 2600828327
  .word 960296800
.section .bss
.balign 4
snapshot: .space 32
