.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 4032293290
  li a3, 0
  li a4, 0
  li a5, 1
  li a6, 3024829961
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 146
.Lloop0:
  bnez a0, .Lskip0_0
  mv a5, a1
.Lskip0_0:
  bnez a1, .Lskip0_1
  mv a2, a0
.Lskip0_1:
  bnez a5, .Lskip0_2
  mv a3, a1
.Lskip0_2:
  bnez a6, .Lskip0_3
  mv a3, a1
.Lskip0_3:
  bnez a5, .Lskip0_4
  mv a6, a0
.Lskip0_4:
  bnez a4, .Lskip0_5
  mv a7, a1
.Lskip0_5:
  bnez a3, .Lskip0_6
  mv a6, a1
.Lskip0_6:
  addi t6, t6, -1
  bnez t6, .Lloop0
  bnez a0, .Ltail_skip0_0
  mv a5, a1
.Ltail_skip0_0:
  bnez a1, .Ltail_skip0_1
  mv a2, a0
.Ltail_skip0_1:
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 146
.Lloop1:
  and a2, a5, a0
  or a2, a5, a3
  and a1, a2, a1
  or a2, a0, a2
  mul a0, a1, a7
  add a4, a5, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  and a2, a5, a0
  or a2, a5, a3
  li s9, 30000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 170
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  xor a7, a0, a2
  sll a1, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a4, a3, a0
  divu a6, a7, a2
  divu a3, a7, a2
  divu a7, a3, a1
  divu a2, a5, a0
  divu a6, a6, a1
  divu a2, a2, a0
  divu a6, a6, a0
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
  .word 3341289845
  .word 1700758318
  .word 60226791
  .word 2714662560
  .word 1074131033
  .word 3728566802
  .word 2088035275
  .word 447503748
  .word 3101939517
  .word 1461407990
  .word 4115843759
  .word 2475312232
  .word 834780705
  .word 3489216474
  .word 1848684947
  .word 208153420
  .word 2862589189
  .word 1222057662
  .word 3876493431
  .word 2235961904
  .word 595430377
  .word 3249866146
  .word 1609334619
  .word 4263770388
  .word 2623238861
  .word 982707334
  .word 3637143103
  .word 1996611576
  .word 356080049
  .word 3010515818
  .word 1369984291
  .word 4024420060
  .word 2383888533
  .word 743357006
  .word 3397792775
  .word 1757261248
  .word 116729721
  .word 2771165490
  .word 1130633963
  .word 3785069732
  .word 2144538205
  .word 504006678
  .word 3158442447
  .word 1517910920
  .word 4172346689
  .word 2531815162
  .word 891283635
  .word 3545719404
  .word 1905187877
  .word 264656350
  .word 2919092119
  .word 1278560592
  .word 3932996361
  .word 2292464834
  .word 651933307
  .word 3306369076
  .word 1665837549
  .word 25306022
  .word 2679741791
  .word 1039210264
  .word 3693646033
  .word 2053114506
  .word 412582979
  .word 3067018748
.section .bss
.balign 4
snapshot: .space 32
