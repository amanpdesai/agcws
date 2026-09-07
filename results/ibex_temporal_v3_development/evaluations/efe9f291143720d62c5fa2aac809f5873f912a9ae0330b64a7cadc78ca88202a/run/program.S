.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 331158070
  li a2, 1167452314
  li a3, 4294967295
  li a4, 1
  li a5, 0
  li a6, 4294967295
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 1126
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 42
.Lloop0:
  divu a2, a7, a7
  divu a3, a2, a5
  divu a7, a4, a4
  divu a2, a1, a4
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 121530
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 244
.Lloop1:
  or a2, a7, a0
  bnez a0, .Lskip1_1
  mv a2, a1
.Lskip1_1:
  sll a7, a7, a1
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  srl a6, a4, a0
  and a5, a6, a1
  xor a5, a0, a0
  add a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 169286
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 988
.Lloop2:
  bnez a4, .Lskip2_0
  mv a7, a0
.Lskip2_0:
  bnez a6, .Lskip2_1
  mv a4, a6
.Lskip2_1:
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 2035265940
  .word 394734413
  .word 3049170182
  .word 1408638655
  .word 4063074424
  .word 2422542897
  .word 782011370
  .word 3436447139
  .word 1795915612
  .word 155384085
  .word 2809819854
  .word 1169288327
  .word 3823724096
  .word 2183192569
  .word 542661042
  .word 3197096811
  .word 1556565284
  .word 4211001053
  .word 2570469526
  .word 929937999
  .word 3584373768
  .word 1943842241
  .word 303310714
  .word 2957746483
  .word 1317214956
  .word 3971650725
  .word 2331119198
  .word 690587671
  .word 3345023440
  .word 1704491913
  .word 63960386
  .word 2718396155
  .word 1077864628
  .word 3732300397
  .word 2091768870
  .word 451237343
  .word 3105673112
  .word 1465141585
  .word 4119577354
  .word 2479045827
  .word 838514300
  .word 3492950069
  .word 1852418542
  .word 211887015
  .word 2866322784
  .word 1225791257
  .word 3880227026
  .word 2239695499
  .word 599163972
  .word 3253599741
  .word 1613068214
  .word 4267503983
  .word 2626972456
  .word 986440929
  .word 3640876698
  .word 2000345171
  .word 359813644
  .word 3014249413
  .word 1373717886
  .word 4028153655
  .word 2387622128
  .word 747090601
  .word 3401526370
  .word 1760994843
.section .bss
.balign 4
snapshot: .space 32
