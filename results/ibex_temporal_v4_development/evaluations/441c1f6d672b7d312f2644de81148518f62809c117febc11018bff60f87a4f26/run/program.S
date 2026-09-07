.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 1
  li a3, 3280444934
  li a4, 4294967295
  li a5, 4118948352
  li a6, 1774413610
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 34182
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 377
.Lloop0:
  mul a5, a3, a0
  mul a3, a2, a1
  srl a7, a2, a0
  xor a7, a3, a1
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  mul a7, a6, a0
  bnez a3, .Lskip0_7
  mv a2, a1
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 70280
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1016
.Lloop1:
  srl a3, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 110125
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 32
.Lloop2:
  divu a3, a2, a1
  divu a3, a0, a4
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
  .word 292232593
  .word 2946668362
  .word 1306136835
  .word 3960572604
  .word 2320041077
  .word 679509550
  .word 3333945319
  .word 1693413792
  .word 52882265
  .word 2707318034
  .word 1066786507
  .word 3721222276
  .word 2080690749
  .word 440159222
  .word 3094594991
  .word 1454063464
  .word 4108499233
  .word 2467967706
  .word 827436179
  .word 3481871948
  .word 1841340421
  .word 200808894
  .word 2855244663
  .word 1214713136
  .word 3869148905
  .word 2228617378
  .word 588085851
  .word 3242521620
  .word 1601990093
  .word 4256425862
  .word 2615894335
  .word 975362808
  .word 3629798577
  .word 1989267050
  .word 348735523
  .word 3003171292
  .word 1362639765
  .word 4017075534
  .word 2376544007
  .word 736012480
  .word 3390448249
  .word 1749916722
  .word 109385195
  .word 2763820964
  .word 1123289437
  .word 3777725206
  .word 2137193679
  .word 496662152
  .word 3151097921
  .word 1510566394
  .word 4165002163
  .word 2524470636
  .word 883939109
  .word 3538374878
  .word 1897843351
  .word 257311824
  .word 2911747593
  .word 1271216066
  .word 3925651835
  .word 2285120308
  .word 644588781
  .word 3299024550
  .word 1658493023
  .word 17961496
.section .bss
.balign 4
snapshot: .space 32
