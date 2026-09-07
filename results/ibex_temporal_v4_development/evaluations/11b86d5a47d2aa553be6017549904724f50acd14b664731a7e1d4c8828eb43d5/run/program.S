.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 4294967295
  li a2, 1849719653
  li a3, 4294967295
  li a4, 31
  li a5, 17
  li a6, 17
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 3530
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 96
.Lloop0:
  bnez a2, .Lskip0_0
  mv a5, a4
.Lskip0_0:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 33686
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 166
.Lloop1:
  bnez a0, .Lskip1_0
  mv a5, a4
.Lskip1_0:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  xor a7, a4, a6
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 58588
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 128
.Lloop2:
  divu a4, a7, a0
  divu a5, a5, a0
  divu a5, a5, a0
  divu a4, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 110407
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 100
.Lloop3:
  bnez a3, .Lskip3_0
  mv a3, a0
.Lskip3_0:
  bnez a6, .Lskip3_1
  mv a5, a0
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 134226
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 8
.Lloop4:
  divu a5, a0, a0
  divu a2, a4, a1
  divu a2, a0, a1
  divu a6, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 158914
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 420
.Lloop5:
  or a4, a5, a0
  sll a6, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 167738
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 438
.Lloop6:
  divu a7, a0, a1
  divu a6, a0, a1
  divu a5, a1, a0
  divu a2, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 3890001994
  .word 2249470467
  .word 608938940
  .word 3263374709
  .word 1622843182
  .word 4277278951
  .word 2636747424
  .word 996215897
  .word 3650651666
  .word 2010120139
  .word 369588612
  .word 3024024381
  .word 1383492854
  .word 4037928623
  .word 2397397096
  .word 756865569
  .word 3411301338
  .word 1770769811
  .word 130238284
  .word 2784674053
  .word 1144142526
  .word 3798578295
  .word 2158046768
  .word 517515241
  .word 3171951010
  .word 1531419483
  .word 4185855252
  .word 2545323725
  .word 904792198
  .word 3559227967
  .word 1918696440
  .word 278164913
  .word 2932600682
  .word 1292069155
  .word 3946504924
  .word 2305973397
  .word 665441870
  .word 3319877639
  .word 1679346112
  .word 38814585
  .word 2693250354
  .word 1052718827
  .word 3707154596
  .word 2066623069
  .word 426091542
  .word 3080527311
  .word 1439995784
  .word 4094431553
  .word 2453900026
  .word 813368499
  .word 3467804268
  .word 1827272741
  .word 186741214
  .word 2841176983
  .word 1200645456
  .word 3855081225
  .word 2214549698
  .word 574018171
  .word 3228453940
  .word 1587922413
  .word 4242358182
  .word 2601826655
  .word 961295128
  .word 3615730897
.section .bss
.balign 4
snapshot: .space 32
