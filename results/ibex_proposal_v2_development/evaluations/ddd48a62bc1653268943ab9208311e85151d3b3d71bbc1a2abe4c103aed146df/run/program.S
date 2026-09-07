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
  li s9, 1000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 225
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  and a6, a4, a5
  or a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 204
.Lloop1:
  sll a2, a0, a1
  srl a4, a2, a3
  mul a6, a4, a5
  bnez a6, .Lskip1_3
  mv a7, a1
.Lskip1_3:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  sll a2, a0, a1
  srl a4, a2, a3
  mul a6, a4, a5
  bnez a6, .Ltail_skip1_3
  mv a7, a1
.Ltail_skip1_3:
  li s9, 70000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 153
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  divu a4, a2, a1
  divu a6, a4, a0
  divu a2, a7, a1
  divu a1, a0, a0
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
