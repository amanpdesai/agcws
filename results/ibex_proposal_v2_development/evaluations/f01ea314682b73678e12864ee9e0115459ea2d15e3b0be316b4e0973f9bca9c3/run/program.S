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
  li t6, 200
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  divu a1, a7, a2
  or a2, a3, a5
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  bnez a6, .Lskip0_4
  mv a3, a1
.Lskip0_4:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 266
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  divu a5, a6, a1
  and a6, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  divu a5, a6, a1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 300
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  bnez a1, .Lskip2_2
  mv a0, a0
.Lskip2_2:
  divu a2, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 365
.Lloop3:
  or a1, a0, a2
  divu a3, a4, a0
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  or a1, a0, a2
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
  .word 3341289836
  .word 1700758309
  .word 60226782
  .word 2714662551
  .word 1074131024
  .word 3728566793
  .word 2088035266
  .word 447503739
  .word 3101939508
  .word 1461407981
  .word 4115843750
  .word 2475312223
  .word 834780696
  .word 3489216465
  .word 1848684938
  .word 208153411
  .word 2862589180
  .word 1222057653
  .word 3876493422
  .word 2235961895
  .word 595430368
  .word 3249866137
  .word 1609334610
  .word 4263770379
  .word 2623238852
  .word 982707325
  .word 3637143094
  .word 1996611567
  .word 356080040
  .word 3010515809
  .word 1369984282
  .word 4024420051
  .word 2383888524
  .word 743356997
  .word 3397792766
  .word 1757261239
  .word 116729712
  .word 2771165481
  .word 1130633954
  .word 3785069723
  .word 2144538196
  .word 504006669
  .word 3158442438
  .word 1517910911
  .word 4172346680
  .word 2531815153
  .word 891283626
  .word 3545719395
  .word 1905187868
  .word 264656341
  .word 2919092110
  .word 1278560583
  .word 3932996352
  .word 2292464825
  .word 651933298
  .word 3306369067
  .word 1665837540
  .word 25306013
  .word 2679741782
  .word 1039210255
  .word 3693646024
  .word 2053114497
  .word 412582970
  .word 3067018739
.section .bss
.balign 4
snapshot: .space 32
