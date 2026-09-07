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
  li t6, 158
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
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  divu a1, a7, a2
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 170
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  divu a5, a6, a1
  and a6, a2, a0
  xor a7, a4, a5
  sll a1, a7, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 210
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
  bnez a2, .Lskip2_4
  mv a6, a0
.Lskip2_4:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 249
.Lloop3:
  or a1, a0, a2
  divu a3, a4, a0
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  srl a7, a1, a3
  add a0, a0, a1
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
  .word 3341289842
  .word 1700758315
  .word 60226788
  .word 2714662557
  .word 1074131030
  .word 3728566799
  .word 2088035272
  .word 447503745
  .word 3101939514
  .word 1461407987
  .word 4115843756
  .word 2475312229
  .word 834780702
  .word 3489216471
  .word 1848684944
  .word 208153417
  .word 2862589186
  .word 1222057659
  .word 3876493428
  .word 2235961901
  .word 595430374
  .word 3249866143
  .word 1609334616
  .word 4263770385
  .word 2623238858
  .word 982707331
  .word 3637143100
  .word 1996611573
  .word 356080046
  .word 3010515815
  .word 1369984288
  .word 4024420057
  .word 2383888530
  .word 743357003
  .word 3397792772
  .word 1757261245
  .word 116729718
  .word 2771165487
  .word 1130633960
  .word 3785069729
  .word 2144538202
  .word 504006675
  .word 3158442444
  .word 1517910917
  .word 4172346686
  .word 2531815159
  .word 891283632
  .word 3545719401
  .word 1905187874
  .word 264656347
  .word 2919092116
  .word 1278560589
  .word 3932996358
  .word 2292464831
  .word 651933304
  .word 3306369073
  .word 1665837546
  .word 25306019
  .word 2679741788
  .word 1039210261
  .word 3693646030
  .word 2053114503
  .word 412582976
  .word 3067018745
.section .bss
.balign 4
snapshot: .space 32
