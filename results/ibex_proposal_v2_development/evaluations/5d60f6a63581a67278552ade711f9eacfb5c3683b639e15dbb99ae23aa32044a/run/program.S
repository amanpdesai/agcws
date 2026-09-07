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
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 166
.Lloop0:
  divu a0, a1, a0
  divu a1, a2, a0
  divu a3, a4, a0
  divu a4, a5, a0
  divu a5, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a0, a1, a0
  divu a1, a2, a0
  divu a3, a4, a0
  divu a4, a5, a0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 133
.Lloop1:
  add a0, a0, a1
  add a1, a1, a2
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  add a0, a0, a1
  add a1, a1, a2
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 200
.Lloop2:
  bnez a0, .Lskip2_0
  mv a0, a1
.Lskip2_0:
  bnez a1, .Lskip2_1
  mv a1, a2
.Lskip2_1:
  bnez a3, .Lskip2_2
  mv a3, a4
.Lskip2_2:
  bnez a4, .Lskip2_3
  mv a4, a5
.Lskip2_3:
  bnez a5, .Lskip2_4
  mv a5, a6
.Lskip2_4:
  bnez a7, .Lskip2_5
  mv a7, a0
.Lskip2_5:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 182
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
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
  .word 3341289837
  .word 1700758310
  .word 60226783
  .word 2714662552
  .word 1074131025
  .word 3728566794
  .word 2088035267
  .word 447503740
  .word 3101939509
  .word 1461407982
  .word 4115843751
  .word 2475312224
  .word 834780697
  .word 3489216466
  .word 1848684939
  .word 208153412
  .word 2862589181
  .word 1222057654
  .word 3876493423
  .word 2235961896
  .word 595430369
  .word 3249866138
  .word 1609334611
  .word 4263770380
  .word 2623238853
  .word 982707326
  .word 3637143095
  .word 1996611568
  .word 356080041
  .word 3010515810
  .word 1369984283
  .word 4024420052
  .word 2383888525
  .word 743356998
  .word 3397792767
  .word 1757261240
  .word 116729713
  .word 2771165482
  .word 1130633955
  .word 3785069724
  .word 2144538197
  .word 504006670
  .word 3158442439
  .word 1517910912
  .word 4172346681
  .word 2531815154
  .word 891283627
  .word 3545719396
  .word 1905187869
  .word 264656342
  .word 2919092111
  .word 1278560584
  .word 3932996353
  .word 2292464826
  .word 651933299
  .word 3306369068
  .word 1665837541
  .word 25306014
  .word 2679741783
  .word 1039210256
  .word 3693646025
  .word 2053114498
  .word 412582971
  .word 3067018740
.section .bss
.balign 4
snapshot: .space 32
