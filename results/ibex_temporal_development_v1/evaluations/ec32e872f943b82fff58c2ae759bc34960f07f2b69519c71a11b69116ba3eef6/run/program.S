.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 4294967295
  li a2, 0
  li a3, 31
  li a4, 2560846708
  li a5, 4294967295
  li a6, 0
  li a7, 2604164434
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 5622
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 340
.Lloop0:
  bnez a5, .Lskip0_0
  mv a4, a0
.Lskip0_0:
  bnez a4, .Lskip0_1
  mv a3, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 63912
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 854
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 1236831796
  .word 3891267565
  .word 2250736038
  .word 610204511
  .word 3264640280
  .word 1624108753
  .word 4278544522
  .word 2638012995
  .word 997481468
  .word 3651917237
  .word 2011385710
  .word 370854183
  .word 3025289952
  .word 1384758425
  .word 4039194194
  .word 2398662667
  .word 758131140
  .word 3412566909
  .word 1772035382
  .word 131503855
  .word 2785939624
  .word 1145408097
  .word 3799843866
  .word 2159312339
  .word 518780812
  .word 3173216581
  .word 1532685054
  .word 4187120823
  .word 2546589296
  .word 906057769
  .word 3560493538
  .word 1919962011
  .word 279430484
  .word 2933866253
  .word 1293334726
  .word 3947770495
  .word 2307238968
  .word 666707441
  .word 3321143210
  .word 1680611683
  .word 40080156
  .word 2694515925
  .word 1053984398
  .word 3708420167
  .word 2067888640
  .word 427357113
  .word 3081792882
  .word 1441261355
  .word 4095697124
  .word 2455165597
  .word 814634070
  .word 3469069839
  .word 1828538312
  .word 188006785
  .word 2842442554
  .word 1201911027
  .word 3856346796
  .word 2215815269
  .word 575283742
  .word 3229719511
  .word 1589187984
  .word 4243623753
  .word 2603092226
  .word 962560699
.section .bss
.balign 4
snapshot: .space 32
