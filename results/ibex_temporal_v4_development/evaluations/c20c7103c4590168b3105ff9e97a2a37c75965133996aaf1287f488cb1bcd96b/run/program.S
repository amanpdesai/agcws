.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 17
  li a2, 1
  li a3, 1
  li a4, 17
  li a5, 31
  li a6, 1
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 114401
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 554
.Lloop0:
  mul a6, a4, a6
  mul a1, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
  mul a6, a4, a6
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 165650
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 28
.Lloop1:
  or a6, a4, a2
  xor a2, a3, a2
  xor a3, a2, a0
  or a5, a2, a2
  or a6, a7, a3
  or a5, a6, a1
  sll a6, a6, a6
  sll a3, a5, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
  or a6, a4, a2
  xor a2, a3, a2
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 116397
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 225
.Lloop2:
  bnez a7, .Lskip2_0
  mv a2, a0
.Lskip2_0:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  and a5, a2, a0
  and a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  bnez a7, .Ltail_skip2_0
  mv a2, a0
.Ltail_skip2_0:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 177287
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 159
.Lloop3:
  bnez a3, .Lskip3_0
  mv a5, a0
.Lskip3_0:
  bnez a4, .Lskip3_1
  mv a7, a0
.Lskip3_1:
  bnez a0, .Lskip3_2
  mv a2, a0
.Lskip3_2:
  bnez a3, .Lskip3_3
  mv a4, a1
.Lskip3_3:
  bnez a0, .Lskip3_4
  mv a5, a1
.Lskip3_4:
  bnez a2, .Lskip3_5
  mv a3, a1
.Lskip3_5:
  bnez a0, .Lskip3_6
  mv a2, a1
.Lskip3_6:
  bnez a3, .Lskip3_7
  mv a6, a0
.Lskip3_7:
  addi t6, t6, -1
  bnez t6, .Lloop3
  bnez a3, .Ltail_skip3_0
  mv a5, a0
.Ltail_skip3_0:
  bnez a4, .Ltail_skip3_1
  mv a7, a0
.Ltail_skip3_1:
  bnez a0, .Ltail_skip3_2
  mv a2, a0
.Ltail_skip3_2:
  bnez a3, .Ltail_skip3_3
  mv a4, a1
.Ltail_skip3_3:
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 26813
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 583
.Lloop4:
  xor a6, a6, a0
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
  .word 3585301010
  .word 1944769483
  .word 304237956
  .word 2958673725
  .word 1318142198
  .word 3972577967
  .word 2332046440
  .word 691514913
  .word 3345950682
  .word 1705419155
  .word 64887628
  .word 2719323397
  .word 1078791870
  .word 3733227639
  .word 2092696112
  .word 452164585
  .word 3106600354
  .word 1466068827
  .word 4120504596
  .word 2479973069
  .word 839441542
  .word 3493877311
  .word 1853345784
  .word 212814257
  .word 2867250026
  .word 1226718499
  .word 3881154268
  .word 2240622741
  .word 600091214
  .word 3254526983
  .word 1613995456
  .word 4268431225
  .word 2627899698
  .word 987368171
  .word 3641803940
  .word 2001272413
  .word 360740886
  .word 3015176655
  .word 1374645128
  .word 4029080897
  .word 2388549370
  .word 748017843
  .word 3402453612
  .word 1761922085
  .word 121390558
  .word 2775826327
  .word 1135294800
  .word 3789730569
  .word 2149199042
  .word 508667515
  .word 3163103284
  .word 1522571757
  .word 4177007526
  .word 2536475999
  .word 895944472
  .word 3550380241
  .word 1909848714
  .word 269317187
  .word 2923752956
  .word 1283221429
  .word 3937657198
  .word 2297125671
  .word 656594144
  .word 3311029913
.section .bss
.balign 4
snapshot: .space 32
