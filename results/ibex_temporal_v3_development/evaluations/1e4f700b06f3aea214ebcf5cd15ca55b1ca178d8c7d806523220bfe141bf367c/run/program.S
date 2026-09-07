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
  add a0, a0, a1
  add a1, a2, a3
  add a2, a4, a5
  add a3, a6, a7
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
  mv a4, a1
.Lskip1_0:
  bnez a2, .Lskip1_1
  mv a5, a3
.Lskip1_1:
  bnez a4, .Lskip1_2
  mv a6, a5
.Lskip1_2:
  bnez a6, .Lskip1_3
  mv a7, a7
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 40000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 80000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  xor a4, a0, a1
  sll a5, a2, a3
  srl a6, a4, a5
  and a7, a6, a7
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
  .word 1234567898
  .word 3889003667
  .word 2248472140
  .word 607940613
  .word 3262376382
  .word 1621844855
  .word 4276280624
  .word 2635749097
  .word 995217570
  .word 3649653339
  .word 2009121812
  .word 368590285
  .word 3023026054
  .word 1382494527
  .word 4036930296
  .word 2396398769
  .word 755867242
  .word 3410303011
  .word 1769771484
  .word 129239957
  .word 2783675726
  .word 1143144199
  .word 3797579968
  .word 2157048441
  .word 516516914
  .word 3170952683
  .word 1530421156
  .word 4184856925
  .word 2544325398
  .word 903793871
  .word 3558229640
  .word 1917698113
  .word 277166586
  .word 2931602355
  .word 1291070828
  .word 3945506597
  .word 2304975070
  .word 664443543
  .word 3318879312
  .word 1678347785
  .word 37816258
  .word 2692252027
  .word 1051720500
  .word 3706156269
  .word 2065624742
  .word 425093215
  .word 3079528984
  .word 1438997457
  .word 4093433226
  .word 2452901699
  .word 812370172
  .word 3466805941
  .word 1826274414
  .word 185742887
  .word 2840178656
  .word 1199647129
  .word 3854082898
  .word 2213551371
  .word 573019844
  .word 3227455613
  .word 1586924086
  .word 4241359855
  .word 2600828328
  .word 960296801
.section .bss
.balign 4
snapshot: .space 32
