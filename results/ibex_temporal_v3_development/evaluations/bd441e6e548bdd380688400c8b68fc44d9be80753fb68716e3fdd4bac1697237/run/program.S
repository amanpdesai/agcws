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
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 512
.Lloop0:
  divu a7, a5, a0
  divu a5, a6, a0
  divu a3, a3, a0
  divu a7, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 512
.Lloop1:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
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
