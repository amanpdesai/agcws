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
  li t6, 128
.Lloop0:
  bnez a5, .Lskip0_0
  mv a3, a1
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a3, a1
.Lskip0_1:
  bnez a5, .Lskip0_2
  mv a6, a0
.Lskip0_2:
  bnez a4, .Lskip0_3
  mv a7, a1
.Lskip0_3:
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
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  and a2, a5, a0
  or a2, a5, a3
  and a1, a2, a1
  or a2, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  divu a4, a3, a0
  divu a6, a7, a2
  divu a3, a7, a2
  divu a7, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 204
.Lloop3:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  li s9, 150000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 128
.Lloop4:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 3341289838
  .word 1700758311
  .word 60226784
  .word 2714662553
  .word 1074131026
  .word 3728566795
  .word 2088035268
  .word 447503741
  .word 3101939510
  .word 1461407983
  .word 4115843752
  .word 2475312225
  .word 834780698
  .word 3489216467
  .word 1848684940
  .word 208153413
  .word 2862589182
  .word 1222057655
  .word 3876493424
  .word 2235961897
  .word 595430370
  .word 3249866139
  .word 1609334612
  .word 4263770381
  .word 2623238854
  .word 982707327
  .word 3637143096
  .word 1996611569
  .word 356080042
  .word 3010515811
  .word 1369984284
  .word 4024420053
  .word 2383888526
  .word 743356999
  .word 3397792768
  .word 1757261241
  .word 116729714
  .word 2771165483
  .word 1130633956
  .word 3785069725
  .word 2144538198
  .word 504006671
  .word 3158442440
  .word 1517910913
  .word 4172346682
  .word 2531815155
  .word 891283628
  .word 3545719397
  .word 1905187870
  .word 264656343
  .word 2919092112
  .word 1278560585
  .word 3932996354
  .word 2292464827
  .word 651933300
  .word 3306369069
  .word 1665837542
  .word 25306015
  .word 2679741784
  .word 1039210257
  .word 3693646026
  .word 2053114499
  .word 412582972
  .word 3067018741
.section .bss
.balign 4
snapshot: .space 32
