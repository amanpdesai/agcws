.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 7
  li a1, 6
  li a2, 5
  li a3, 4
  li a4, 3
  li a5, 2
  li a6, 1
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 15000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 233
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  and a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  li s9, 35000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 200
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 55000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 233
.Lloop2:
  sll a2, a0, a1
  srl a4, a2, a3
  mul a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a2, a0, a1
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 200
.Lloop3:
  bnez a0, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  bnez a3, .Lskip3_1
  mv a5, a4
.Lskip3_1:
  bnez a5, .Lskip3_2
  mv a7, a6
.Lskip3_2:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 95000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 266
.Lloop4:
  divu a6, a7, a2
  divu a3, a5, a1
  divu a0, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  divu a6, a7, a2
  divu a3, a5, a1
  li s9, 115000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 232
.Lloop5:
  add a2, a0, a1
  xor a5, a3, a4
  or a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 2233445566
  .word 592914039
  .word 3247349808
  .word 1606818281
  .word 4261254050
  .word 2620722523
  .word 980190996
  .word 3634626765
  .word 1994095238
  .word 353563711
  .word 3007999480
  .word 1367467953
  .word 4021903722
  .word 2381372195
  .word 740840668
  .word 3395276437
  .word 1754744910
  .word 114213383
  .word 2768649152
  .word 1128117625
  .word 3782553394
  .word 2142021867
  .word 501490340
  .word 3155926109
  .word 1515394582
  .word 4169830351
  .word 2529298824
  .word 888767297
  .word 3543203066
  .word 1902671539
  .word 262140012
  .word 2916575781
  .word 1276044254
  .word 3930480023
  .word 2289948496
  .word 649416969
  .word 3303852738
  .word 1663321211
  .word 22789684
  .word 2677225453
  .word 1036693926
  .word 3691129695
  .word 2050598168
  .word 410066641
  .word 3064502410
  .word 1423970883
  .word 4078406652
  .word 2437875125
  .word 797343598
  .word 3451779367
  .word 1811247840
  .word 170716313
  .word 2825152082
  .word 1184620555
  .word 3839056324
  .word 2198524797
  .word 557993270
  .word 3212429039
  .word 1571897512
  .word 4226333281
  .word 2585801754
  .word 945270227
  .word 3599705996
  .word 1959174469
.section .bss
.balign 4
snapshot: .space 32
