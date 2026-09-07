.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 556512538
  li a2, 17
  li a3, 31
  li a4, 4294967295
  li a5, 1
  li a6, 0
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 19554
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 176
.Lloop0:
  or a3, a7, a5
  add a6, a4, a1
  sll a2, a7, a2
  and a6, a0, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 112597
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 175
.Lloop1:
  bnez a7, .Lskip1_0
  mv a7, a7
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a2, a1
.Lskip1_1:
  bnez a3, .Lskip1_2
  mv a1, a1
.Lskip1_2:
  bnez a1, .Lskip1_3
  mv a0, a2
.Lskip1_3:
  bnez a5, .Lskip1_4
  mv a5, a5
.Lskip1_4:
  bnez a4, .Lskip1_5
  mv a1, a4
.Lskip1_5:
  bnez a3, .Lskip1_6
  mv a6, a1
.Lskip1_6:
  bnez a7, .Lskip1_7
  mv a3, a4
.Lskip1_7:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 117853
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 204
.Lloop2:
  sll a7, a1, a1
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 170693
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 1584
.Lloop3:
  and a6, a3, a6
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
  .word 1336022935
  .word 3990458704
  .word 2349927177
  .word 709395650
  .word 3363831419
  .word 1723299892
  .word 82768365
  .word 2737204134
  .word 1096672607
  .word 3751108376
  .word 2110576849
  .word 470045322
  .word 3124481091
  .word 1483949564
  .word 4138385333
  .word 2497853806
  .word 857322279
  .word 3511758048
  .word 1871226521
  .word 230694994
  .word 2885130763
  .word 1244599236
  .word 3899035005
  .word 2258503478
  .word 617971951
  .word 3272407720
  .word 1631876193
  .word 4286311962
  .word 2645780435
  .word 1005248908
  .word 3659684677
  .word 2019153150
  .word 378621623
  .word 3033057392
  .word 1392525865
  .word 4046961634
  .word 2406430107
  .word 765898580
  .word 3420334349
  .word 1779802822
  .word 139271295
  .word 2793707064
  .word 1153175537
  .word 3807611306
  .word 2167079779
  .word 526548252
  .word 3180984021
  .word 1540452494
  .word 4194888263
  .word 2554356736
  .word 913825209
  .word 3568260978
  .word 1927729451
  .word 287197924
  .word 2941633693
  .word 1301102166
  .word 3955537935
  .word 2315006408
  .word 674474881
  .word 3328910650
  .word 1688379123
  .word 47847596
  .word 2702283365
  .word 1061751838
.section .bss
.balign 4
snapshot: .space 32
