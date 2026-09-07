.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4144141048
  li a1, 0
  li a2, 4294967295
  li a3, 0
  li a4, 31
  li a5, 17
  li a6, 1
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 10764
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 94
.Lloop0:
  or a6, a5, a0
  bnez a3, .Lskip0_1
  mv a7, a0
.Lskip0_1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  xor a6, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 27910
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1576
.Lloop1:
  divu a7, a7, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 33755
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 28
.Lloop2:
  srl a6, a5, a4
  xor a4, a0, a7
  or a5, a1, a7
  srl a2, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 42729
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 106
.Lloop3:
  bnez a4, .Lskip3_0
  mv a6, a4
.Lskip3_0:
  bnez a0, .Lskip3_1
  mv a3, a5
.Lskip3_1:
  bnez a5, .Lskip3_2
  mv a1, a7
.Lskip3_2:
  bnez a1, .Lskip3_3
  mv a1, a4
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 108069
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 76
.Lloop4:
  divu a4, a0, a0
  divu a3, a2, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 125957
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 127
.Lloop5:
  mul a7, a6, a7
  mul a5, a5, a1
  mul a2, a5, a2
  mul a7, a5, a2
  mul a2, a1, a1
  mul a1, a4, a2
  mul a1, a4, a6
  mul a6, a3, a3
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 125975
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 264
.Lloop6:
  srl a2, a6, a5
  addi t6, t6, -1
  bnez t6, .Lloop6
.global agcws_segment_7_setup
agcws_segment_7_setup:
  li s9, 171123
  add s9, s9, s10
.global agcws_segment_7_poll
agcws_segment_7_poll:
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
.global agcws_segment_7_body
agcws_segment_7_body:
  li t6, 44
.Lloop7:
  xor a2, a5, a1
  or a2, a6, a1
  sll a6, a2, a0
  srl a3, a0, a0
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
  .word 1196901424
  .word 3851337193
  .word 2210805666
  .word 570274139
  .word 3224709908
  .word 1584178381
  .word 4238614150
  .word 2598082623
  .word 957551096
  .word 3611986865
  .word 1971455338
  .word 330923811
  .word 2985359580
  .word 1344828053
  .word 3999263822
  .word 2358732295
  .word 718200768
  .word 3372636537
  .word 1732105010
  .word 91573483
  .word 2746009252
  .word 1105477725
  .word 3759913494
  .word 2119381967
  .word 478850440
  .word 3133286209
  .word 1492754682
  .word 4147190451
  .word 2506658924
  .word 866127397
  .word 3520563166
  .word 1880031639
  .word 239500112
  .word 2893935881
  .word 1253404354
  .word 3907840123
  .word 2267308596
  .word 626777069
  .word 3281212838
  .word 1640681311
  .word 149784
  .word 2654585553
  .word 1014054026
  .word 3668489795
  .word 2027958268
  .word 387426741
  .word 3041862510
  .word 1401330983
  .word 4055766752
  .word 2415235225
  .word 774703698
  .word 3429139467
  .word 1788607940
  .word 148076413
  .word 2802512182
  .word 1161980655
  .word 3816416424
  .word 2175884897
  .word 535353370
  .word 3189789139
  .word 1549257612
  .word 4203693381
  .word 2563161854
  .word 922630327
.section .bss
.balign 4
snapshot: .space 32
