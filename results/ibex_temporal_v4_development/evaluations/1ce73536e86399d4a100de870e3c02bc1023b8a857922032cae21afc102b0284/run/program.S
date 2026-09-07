.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 4294967295
  li a2, 17
  li a3, 4294967295
  li a4, 1
  li a5, 0
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 48013
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 128
.Lloop0:
  or a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 48947
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 840
.Lloop1:
  mul a7, a2, a1
  mul a4, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 56399
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 312
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 79715
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 592
.Lloop3:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 80898
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
  and a0, a1, a2
  srl a2, a5, a4
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 151433
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 115
.Lloop5:
  divu a6, a6, a0
  divu a1, a6, a6
  divu a1, a6, a6
  divu a2, a2, a0
  divu a5, a6, a1
  divu a3, a5, a0
  divu a2, a4, a7
  divu a0, a2, a5
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 613835664
  .word 3268271433
  .word 1627739906
  .word 4282175675
  .word 2641644148
  .word 1001112621
  .word 3655548390
  .word 2015016863
  .word 374485336
  .word 3028921105
  .word 1388389578
  .word 4042825347
  .word 2402293820
  .word 761762293
  .word 3416198062
  .word 1775666535
  .word 135135008
  .word 2789570777
  .word 1149039250
  .word 3803475019
  .word 2162943492
  .word 522411965
  .word 3176847734
  .word 1536316207
  .word 4190751976
  .word 2550220449
  .word 909688922
  .word 3564124691
  .word 1923593164
  .word 283061637
  .word 2937497406
  .word 1296965879
  .word 3951401648
  .word 2310870121
  .word 670338594
  .word 3324774363
  .word 1684242836
  .word 43711309
  .word 2698147078
  .word 1057615551
  .word 3712051320
  .word 2071519793
  .word 430988266
  .word 3085424035
  .word 1444892508
  .word 4099328277
  .word 2458796750
  .word 818265223
  .word 3472700992
  .word 1832169465
  .word 191637938
  .word 2846073707
  .word 1205542180
  .word 3859977949
  .word 2219446422
  .word 578914895
  .word 3233350664
  .word 1592819137
  .word 4247254906
  .word 2606723379
  .word 966191852
  .word 3620627621
  .word 1980096094
  .word 339564567
.section .bss
.balign 4
snapshot: .space 32
