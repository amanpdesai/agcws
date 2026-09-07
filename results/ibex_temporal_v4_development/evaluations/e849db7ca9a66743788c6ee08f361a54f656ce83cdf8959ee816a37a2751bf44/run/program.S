.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1524070095
  li a1, 2878198791
  li a2, 17
  li a3, 17
  li a4, 4269281453
  li a5, 0
  li a6, 1
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 17908
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 582
.Lloop0:
  and a1, a3, a1
  mul a5, a2, a7
  sll a0, a1, a3
  srl a6, a2, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 93289
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 10
.Lloop1:
  bnez a0, .Lskip1_0
  mv a7, a0
.Lskip1_0:
  bnez a2, .Lskip1_1
  mv a3, a0
.Lskip1_1:
  bnez a1, .Lskip1_2
  mv a7, a1
.Lskip1_2:
  bnez a0, .Lskip1_3
  mv a4, a0
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 142979
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 178
.Lloop2:
  and a4, a2, a2
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  divu a7, a6, a4
  mul a3, a3, a5
  srl a5, a3, a3
  srl a5, a4, a5
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  and a7, a5, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 156543
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 76
.Lloop3:
  bnez a0, .Lskip3_0
  mv a7, a5
.Lskip3_0:
  bnez a3, .Lskip3_1
  mv a2, a4
.Lskip3_1:
  bnez a5, .Lskip3_2
  mv a0, a7
.Lskip3_2:
  bnez a4, .Lskip3_3
  mv a5, a1
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
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
  .word 3178046806
  .word 1537515279
  .word 4191951048
  .word 2551419521
  .word 910887994
  .word 3565323763
  .word 1924792236
  .word 284260709
  .word 2938696478
  .word 1298164951
  .word 3952600720
  .word 2312069193
  .word 671537666
  .word 3325973435
  .word 1685441908
  .word 44910381
  .word 2699346150
  .word 1058814623
  .word 3713250392
  .word 2072718865
  .word 432187338
  .word 3086623107
  .word 1446091580
  .word 4100527349
  .word 2459995822
  .word 819464295
  .word 3473900064
  .word 1833368537
  .word 192837010
  .word 2847272779
  .word 1206741252
  .word 3861177021
  .word 2220645494
  .word 580113967
  .word 3234549736
  .word 1594018209
  .word 4248453978
  .word 2607922451
  .word 967390924
  .word 3621826693
  .word 1981295166
  .word 340763639
  .word 2995199408
  .word 1354667881
  .word 4009103650
  .word 2368572123
  .word 728040596
  .word 3382476365
  .word 1741944838
  .word 101413311
  .word 2755849080
  .word 1115317553
  .word 3769753322
  .word 2129221795
  .word 488690268
  .word 3143126037
  .word 1502594510
  .word 4157030279
  .word 2516498752
  .word 875967225
  .word 3530402994
  .word 1889871467
  .word 249339940
  .word 2903775709
.section .bss
.balign 4
snapshot: .space 32
