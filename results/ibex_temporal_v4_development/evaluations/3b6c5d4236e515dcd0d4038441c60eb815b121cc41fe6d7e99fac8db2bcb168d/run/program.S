.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 0
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 512
.Lloop0:
  sll a2, a0, a1
  srl a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  xor a0, a0, a1
  and a2, a2, a3
  or a4, a4, a5
  add a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 4294967295
  .word 2654435768
  .word 1013904241
  .word 3668340010
  .word 2027808483
  .word 387276956
  .word 3041712725
  .word 1401181198
  .word 4055616967
  .word 2415085440
  .word 774553913
  .word 3428989682
  .word 1788458155
  .word 147926628
  .word 2802362397
  .word 1161830870
  .word 3816266639
  .word 2175735112
  .word 535203585
  .word 3189639354
  .word 1549107827
  .word 4203543596
  .word 2563012069
  .word 922480542
  .word 3576916311
  .word 1936384784
  .word 295853257
  .word 2950289026
  .word 1309757499
  .word 3964193268
  .word 2323661741
  .word 683130214
  .word 3337565983
  .word 1697034456
  .word 56502929
  .word 2710938698
  .word 1070407171
  .word 3724842940
  .word 2084311413
  .word 443779886
  .word 3098215655
  .word 1457684128
  .word 4112119897
  .word 2471588370
  .word 831056843
  .word 3485492612
  .word 1844961085
  .word 204429558
  .word 2858865327
  .word 1218333800
  .word 3872769569
  .word 2232238042
  .word 591706515
  .word 3246142284
  .word 1605610757
  .word 4260046526
  .word 2619514999
  .word 978983472
  .word 3633419241
  .word 1992887714
  .word 352356187
  .word 3006791956
  .word 1366260429
  .word 4020696198
.section .bss
.balign 4
snapshot: .space 32
