.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 10000
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
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  mul a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 256
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a3, a1, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  bnez a5, .Lskip1_3
  mv a7, a6
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 60000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 256
.Lloop2:
  and a2, a0, a1
  or a4, a2, a3
  srl a6, a4, a5
  divu a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 90000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 170
.Lloop3:
  add a0, a0, a1
  xor a1, a2, a3
  bnez a4, .Lskip3_2
  mv a2, a5
.Lskip3_2:
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  xor a1, a2, a3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 120000
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 128
.Lloop4:
  mul a1, a3, a3
  mul a1, a2, a1
  mul a5, a4, a0
  mul a6, a6, a6
  mul a6, a7, a7
  mul a6, a4, a2
  mul a4, a2, a5
  mul a5, a5, a2
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
  .word 999999999
  .word 3654435768
  .word 2013904241
  .word 373372714
  .word 3027808483
  .word 1387276956
  .word 4041712725
  .word 2401181198
  .word 760649671
  .word 3415085440
  .word 1774553913
  .word 134022386
  .word 2788458155
  .word 1147926628
  .word 3802362397
  .word 2161830870
  .word 521299343
  .word 3175735112
  .word 1535203585
  .word 4189639354
  .word 2549107827
  .word 908576300
  .word 3563012069
  .word 1922480542
  .word 281949015
  .word 2936384784
  .word 1295853257
  .word 3950289026
  .word 2309757499
  .word 669225972
  .word 3323661741
  .word 1683130214
  .word 42598687
  .word 2697034456
  .word 1056502929
  .word 3710938698
  .word 2070407171
  .word 429875644
  .word 3084311413
  .word 1443779886
  .word 4098215655
  .word 2457684128
  .word 817152601
  .word 3471588370
  .word 1831056843
  .word 190525316
  .word 2844961085
  .word 1204429558
  .word 3858865327
  .word 2218333800
  .word 577802273
  .word 3232238042
  .word 1591706515
  .word 4246142284
  .word 2605610757
  .word 965079230
  .word 3619514999
  .word 1978983472
  .word 338451945
  .word 2992887714
  .word 1352356187
  .word 4006791956
  .word 2366260429
  .word 725728902
.section .bss
.balign 4
snapshot: .space 32
