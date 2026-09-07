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
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  bnez a0, .Lskip0_4
  mv a2, a1
.Lskip0_4:
  bnez a2, .Lskip0_5
  mv a4, a3
.Lskip0_5:
  bnez a4, .Lskip0_6
  mv a6, a5
.Lskip0_6:
  bnez a6, .Lskip0_7
  mv a0, a7
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
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
  .word 1234567901
  .word 3889003670
  .word 2248472143
  .word 607940616
  .word 3262376385
  .word 1621844858
  .word 4276280627
  .word 2635749100
  .word 995217573
  .word 3649653342
  .word 2009121815
  .word 368590288
  .word 3023026057
  .word 1382494530
  .word 4036930299
  .word 2396398772
  .word 755867245
  .word 3410303014
  .word 1769771487
  .word 129239960
  .word 2783675729
  .word 1143144202
  .word 3797579971
  .word 2157048444
  .word 516516917
  .word 3170952686
  .word 1530421159
  .word 4184856928
  .word 2544325401
  .word 903793874
  .word 3558229643
  .word 1917698116
  .word 277166589
  .word 2931602358
  .word 1291070831
  .word 3945506600
  .word 2304975073
  .word 664443546
  .word 3318879315
  .word 1678347788
  .word 37816261
  .word 2692252030
  .word 1051720503
  .word 3706156272
  .word 2065624745
  .word 425093218
  .word 3079528987
  .word 1438997460
  .word 4093433229
  .word 2452901702
  .word 812370175
  .word 3466805944
  .word 1826274417
  .word 185742890
  .word 2840178659
  .word 1199647132
  .word 3854082901
  .word 2213551374
  .word 573019847
  .word 3227455616
  .word 1586924089
  .word 4241359858
  .word 2600828331
  .word 960296804
.section .bss
.balign 4
snapshot: .space 32
