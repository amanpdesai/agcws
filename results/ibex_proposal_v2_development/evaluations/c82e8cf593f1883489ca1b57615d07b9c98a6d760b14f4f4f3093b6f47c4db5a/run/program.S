.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 0
  li a2, 4294967295
  li a3, 0
  li a4, 4294967295
  li a5, 0
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 26942
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 100
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
  li t6, 116
.Lloop1:
  sll a7, a2, a0
  srl a1, a1, a4
  divu a3, a3, a3
  divu a5, a5, a5
  xor a0, a0, a0
  sll a1, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  sll a7, a2, a0
  srl a1, a1, a4
  divu a3, a3, a3
  divu a5, a5, a5
  li s9, 105645
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 100
.Lloop2:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  divu a0, a0, a0
  divu a1, a1, a1
  divu a2, a2, a2
  xor a3, a3, a3
  sll a4, a4, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 116314
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
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
  divu a7, a7, a7
  divu a6, a6, a6
  divu a5, a5, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
  bnez a2, .Ltail_skip3_0
  mv a5, a1
.Ltail_skip3_0:
  bnez a0, .Ltail_skip3_1
  mv a6, a0
.Ltail_skip3_1:
  bnez a2, .Ltail_skip3_2
  mv a4, a1
.Ltail_skip3_2:
  bnez a2, .Ltail_skip3_3
  mv a5, a0
.Ltail_skip3_3:
  li s9, 158118
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 124
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
  divu a1, a3, a3
  divu a1, a2, a1
  divu a5, a4, a0
  divu a6, a6, a6
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
  .word 271828182
  .word 2926263951
  .word 1285732424
  .word 3940168193
  .word 2299636666
  .word 659105139
  .word 3313540908
  .word 1673009381
  .word 32477854
  .word 2686913623
  .word 1046382096
  .word 3700817865
  .word 2060286338
  .word 419754811
  .word 3074190580
  .word 1433659053
  .word 4088094822
  .word 2447563295
  .word 807031768
  .word 3461467537
  .word 1820936010
  .word 180404483
  .word 2834840252
  .word 1194308725
  .word 3848744494
  .word 2208212967
  .word 567681440
  .word 3222117209
  .word 1581585682
  .word 4236021451
  .word 2595489924
  .word 954958397
  .word 3609394166
  .word 1968862639
  .word 328331112
  .word 2982766881
  .word 1342235354
  .word 3996671123
  .word 2356139596
  .word 715608069
  .word 3370043838
  .word 1729512311
  .word 88980784
  .word 2743416553
  .word 1102885026
  .word 3757320795
  .word 2116789268
  .word 476257741
  .word 3130693510
  .word 1490161983
  .word 4144597752
  .word 2504066225
  .word 863534698
  .word 3517970467
  .word 1877438940
  .word 236907413
  .word 2891343182
  .word 1250811655
  .word 3905247424
  .word 2264715897
  .word 624184370
  .word 3278620139
  .word 1638088612
  .word 4292524381
.section .bss
.balign 4
snapshot: .space 32
