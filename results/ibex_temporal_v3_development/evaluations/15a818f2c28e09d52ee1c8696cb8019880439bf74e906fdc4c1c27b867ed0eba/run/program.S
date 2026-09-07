.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 0
  li a3, 2662913795
  li a4, 0
  li a5, 4294967295
  li a6, 0
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 26942
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 77
.Lloop0:
  xor a2, a6, a1
  srl a4, a2, a1
  xor a6, a2, a0
  mul a2, a7, a0
  mul a3, a4, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  bnez a6, .Lskip0_6
  mv a5, a1
.Lskip0_6:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 102374
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 400
.Lloop1:
  sll a7, a2, a0
  srl a1, a1, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 105645
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 196
.Lloop2:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 116314
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 196
.Lloop3:
  bnez a2, .Lskip3_0
  mv a5, a1
.Lskip3_0:
  bnez a0, .Lskip3_1
  mv a6, a0
.Lskip3_1:
  bnez a2, .Lskip3_2
  mv a4, a1
.Lskip3_2:
  bnez a2, .Lskip3_3
  mv a5, a0
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 158118
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 188
.Lloop4:
  divu a1, a3, a3
  divu a1, a2, a1
  divu a5, a4, a0
  divu a6, a6, a6
  divu a6, a7, a7
  divu a6, a4, a2
  divu a4, a2, a5
  divu a5, a5, a2
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
  .word 2139098885
  .word 498567358
  .word 3153003127
  .word 1512471600
  .word 4166907369
  .word 2526375842
  .word 885844315
  .word 3540280084
  .word 1899748557
  .word 259217030
  .word 2913652799
  .word 1273121272
  .word 3927557041
  .word 2287025514
  .word 646493987
  .word 3300929756
  .word 1660398229
  .word 19866702
  .word 2674302471
  .word 1033770944
  .word 3688206713
  .word 2047675186
  .word 407143659
  .word 3061579428
  .word 1421047901
  .word 4075483670
  .word 2434952143
  .word 794420616
  .word 3448856385
  .word 1808324858
  .word 167793331
  .word 2822229100
  .word 1181697573
  .word 3836133342
  .word 2195601815
  .word 555070288
  .word 3209506057
  .word 1568974530
  .word 4223410299
  .word 2582878772
  .word 942347245
  .word 3596783014
  .word 1956251487
  .word 315719960
  .word 2970155729
  .word 1329624202
  .word 3984059971
  .word 2343528444
  .word 702996917
  .word 3357432686
  .word 1716901159
  .word 76369632
  .word 2730805401
  .word 1090273874
  .word 3744709643
  .word 2104178116
  .word 463646589
  .word 3118082358
  .word 1477550831
  .word 4131986600
  .word 2491455073
  .word 850923546
  .word 3505359315
  .word 1864827788
.section .bss
.balign 4
snapshot: .space 32
