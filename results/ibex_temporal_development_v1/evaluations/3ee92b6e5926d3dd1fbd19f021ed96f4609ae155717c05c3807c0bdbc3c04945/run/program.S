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
  li a4, 128
  li a5, 1
  li a6, 3024829961
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 90063
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 299
.Lloop0:
  bnez a5, .Lskip0_0
  mv a3, a1
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a3, a1
.Lskip0_1:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  and a3, a2, a0
  bnez a3, .Lskip0_4
  mv a6, a1
.Lskip0_4:
  bnez a1, .Lskip0_5
  mv a7, a0
.Lskip0_5:
  bnez a0, .Lskip0_6
  mv a5, a1
.Lskip0_6:
  bnez a1, .Lskip0_7
  mv a2, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 155362
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 426
.Lloop1:
  bnez a3, .Lskip1_0
  mv a4, a0
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a6, a2
.Lskip1_1:
  bnez a7, .Lskip1_2
  mv a3, a2
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a7, a1
.Lskip1_3:
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
  .word 3341289835
  .word 1700758308
  .word 60226781
  .word 2714662550
  .word 1074131023
  .word 3728566792
  .word 2088035265
  .word 447503738
  .word 3101939507
  .word 1461407980
  .word 4115843749
  .word 2475312222
  .word 834780695
  .word 3489216464
  .word 1848684937
  .word 208153410
  .word 2862589179
  .word 1222057652
  .word 3876493421
  .word 2235961894
  .word 595430367
  .word 3249866136
  .word 1609334609
  .word 4263770378
  .word 2623238851
  .word 982707324
  .word 3637143093
  .word 1996611566
  .word 356080039
  .word 3010515808
  .word 1369984281
  .word 4024420050
  .word 2383888523
  .word 743356996
  .word 3397792765
  .word 1757261238
  .word 116729711
  .word 2771165480
  .word 1130633953
  .word 3785069722
  .word 2144538195
  .word 504006668
  .word 3158442437
  .word 1517910910
  .word 4172346679
  .word 2531815152
  .word 891283625
  .word 3545719394
  .word 1905187867
  .word 264656340
  .word 2919092109
  .word 1278560582
  .word 3932996351
  .word 2292464824
  .word 651933297
  .word 3306369066
  .word 1665837539
  .word 25306012
  .word 2679741781
  .word 1039210254
  .word 3693646023
  .word 2053114496
  .word 412582969
  .word 3067018738
.section .bss
.balign 4
snapshot: .space 32
