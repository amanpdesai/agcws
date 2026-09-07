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
  li t6, 233
.Lloop0:
  add a0, a0, a1
  xor a1, a2, a3
  add a2, a4, a5
  and a3, a6, a7
  bnez a0, .Lskip0_4
  mv a4, a1
.Lskip0_4:
  bnez a2, .Lskip0_5
  mv a5, a3
.Lskip0_5:
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a2, a3
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 233
.Lloop1:
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
  add a0, a0, a2
  xor a1, a4, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 324
.Lloop2:
  sll a0, a0, a1
  srl a1, a2, a3
  add a2, a4, a5
  bnez a6, .Lskip2_3
  mv a3, a7
.Lskip2_3:
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
  .word 1234567900
  .word 3889003669
  .word 2248472142
  .word 607940615
  .word 3262376384
  .word 1621844857
  .word 4276280626
  .word 2635749099
  .word 995217572
  .word 3649653341
  .word 2009121814
  .word 368590287
  .word 3023026056
  .word 1382494529
  .word 4036930298
  .word 2396398771
  .word 755867244
  .word 3410303013
  .word 1769771486
  .word 129239959
  .word 2783675728
  .word 1143144201
  .word 3797579970
  .word 2157048443
  .word 516516916
  .word 3170952685
  .word 1530421158
  .word 4184856927
  .word 2544325400
  .word 903793873
  .word 3558229642
  .word 1917698115
  .word 277166588
  .word 2931602357
  .word 1291070830
  .word 3945506599
  .word 2304975072
  .word 664443545
  .word 3318879314
  .word 1678347787
  .word 37816260
  .word 2692252029
  .word 1051720502
  .word 3706156271
  .word 2065624744
  .word 425093217
  .word 3079528986
  .word 1438997459
  .word 4093433228
  .word 2452901701
  .word 812370174
  .word 3466805943
  .word 1826274416
  .word 185742889
  .word 2840178658
  .word 1199647131
  .word 3854082900
  .word 2213551373
  .word 573019846
  .word 3227455615
  .word 1586924088
  .word 4241359857
  .word 2600828330
  .word 960296803
.section .bss
.balign 4
snapshot: .space 32
