.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 17
  li a2, 1
  li a3, 0
  li a4, 4233433920
  li a5, 17
  li a6, 4294967295
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 96926
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 3752
.Lloop0:
  and a7, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 103116
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 43
.Lloop1:
  add a7, a2, a1
  sll a4, a2, a0
  add a2, a1, a1
  sll a6, a3, a0
  add a4, a3, a1
  add a7, a6, a1
  add a5, a3, a1
  add a5, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 2240243770
  .word 599712243
  .word 3254148012
  .word 1613616485
  .word 4268052254
  .word 2627520727
  .word 986989200
  .word 3641424969
  .word 2000893442
  .word 360361915
  .word 3014797684
  .word 1374266157
  .word 4028701926
  .word 2388170399
  .word 747638872
  .word 3402074641
  .word 1761543114
  .word 121011587
  .word 2775447356
  .word 1134915829
  .word 3789351598
  .word 2148820071
  .word 508288544
  .word 3162724313
  .word 1522192786
  .word 4176628555
  .word 2536097028
  .word 895565501
  .word 3550001270
  .word 1909469743
  .word 268938216
  .word 2923373985
  .word 1282842458
  .word 3937278227
  .word 2296746700
  .word 656215173
  .word 3310650942
  .word 1670119415
  .word 29587888
  .word 2684023657
  .word 1043492130
  .word 3697927899
  .word 2057396372
  .word 416864845
  .word 3071300614
  .word 1430769087
  .word 4085204856
  .word 2444673329
  .word 804141802
  .word 3458577571
  .word 1818046044
  .word 177514517
  .word 2831950286
  .word 1191418759
  .word 3845854528
  .word 2205323001
  .word 564791474
  .word 3219227243
  .word 1578695716
  .word 4233131485
  .word 2592599958
  .word 952068431
  .word 3606504200
  .word 1965972673
.section .bss
.balign 4
snapshot: .space 32
