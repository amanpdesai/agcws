.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 17
  li a3, 4294967295
  li a4, 0
  li a5, 31
  li a6, 31
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 4299
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 400
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 35017
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 92
.Lloop1:
  bnez a3, .Lskip1_0
  mv a3, a1
.Lskip1_0:
  bnez a0, .Lskip1_1
  mv a3, a1
.Lskip1_1:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 41067
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 22
.Lloop2:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 69217
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 100
.Lloop3:
  bnez a7, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  bnez a4, .Lskip3_1
  mv a5, a0
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 85248
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 1896
.Lloop4:
  add a5, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 90192
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 408
.Lloop5:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 107800
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 344
.Lloop6:
  bnez a5, .Lskip6_0
  mv a4, a0
.Lskip6_0:
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 154582
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 11
.Lloop7:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 990327424
  .word 3644763193
  .word 2004231666
  .word 363700139
  .word 3018135908
  .word 1377604381
  .word 4032040150
  .word 2391508623
  .word 750977096
  .word 3405412865
  .word 1764881338
  .word 124349811
  .word 2778785580
  .word 1138254053
  .word 3792689822
  .word 2152158295
  .word 511626768
  .word 3166062537
  .word 1525531010
  .word 4179966779
  .word 2539435252
  .word 898903725
  .word 3553339494
  .word 1912807967
  .word 272276440
  .word 2926712209
  .word 1286180682
  .word 3940616451
  .word 2300084924
  .word 659553397
  .word 3313989166
  .word 1673457639
  .word 32926112
  .word 2687361881
  .word 1046830354
  .word 3701266123
  .word 2060734596
  .word 420203069
  .word 3074638838
  .word 1434107311
  .word 4088543080
  .word 2448011553
  .word 807480026
  .word 3461915795
  .word 1821384268
  .word 180852741
  .word 2835288510
  .word 1194756983
  .word 3849192752
  .word 2208661225
  .word 568129698
  .word 3222565467
  .word 1582033940
  .word 4236469709
  .word 2595938182
  .word 955406655
  .word 3609842424
  .word 1969310897
  .word 328779370
  .word 2983215139
  .word 1342683612
  .word 3997119381
  .word 2356587854
  .word 716056327
.section .bss
.balign 4
snapshot: .space 32
