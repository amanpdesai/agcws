.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 4294967295
  li a3, 4294967295
  li a4, 31
  li a5, 1
  li a6, 1
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 27690
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 253
.Lloop0:
  divu a6, a7, a1
  divu a2, a7, a0
  divu a4, a5, a1
  divu a3, a4, a0
  divu a5, a1, a0
  divu a4, a0, a0
  divu a2, a0, a0
  divu a6, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a6, a7, a1
  divu a2, a7, a0
  divu a4, a5, a1
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30733
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 393
.Lloop1:
  mul a1, a4, a0
  mul a0, a1, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 123584
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 641
.Lloop2:
  bnez a6, .Lskip2_0
  mv a7, a2
.Lskip2_0:
  bnez a3, .Lskip2_1
  mv a4, a3
.Lskip2_1:
  addi t6, t6, -1
  bnez t6, .Lloop2
  bnez a6, .Ltail_skip2_0
  mv a7, a2
.Ltail_skip2_0:
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
  .word 2706724234
  .word 1066192707
  .word 3720628476
  .word 2080096949
  .word 439565422
  .word 3094001191
  .word 1453469664
  .word 4107905433
  .word 2467373906
  .word 826842379
  .word 3481278148
  .word 1840746621
  .word 200215094
  .word 2854650863
  .word 1214119336
  .word 3868555105
  .word 2228023578
  .word 587492051
  .word 3241927820
  .word 1601396293
  .word 4255832062
  .word 2615300535
  .word 974769008
  .word 3629204777
  .word 1988673250
  .word 348141723
  .word 3002577492
  .word 1362045965
  .word 4016481734
  .word 2375950207
  .word 735418680
  .word 3389854449
  .word 1749322922
  .word 108791395
  .word 2763227164
  .word 1122695637
  .word 3777131406
  .word 2136599879
  .word 496068352
  .word 3150504121
  .word 1509972594
  .word 4164408363
  .word 2523876836
  .word 883345309
  .word 3537781078
  .word 1897249551
  .word 256718024
  .word 2911153793
  .word 1270622266
  .word 3925058035
  .word 2284526508
  .word 643994981
  .word 3298430750
  .word 1657899223
  .word 17367696
  .word 2671803465
  .word 1031271938
  .word 3685707707
  .word 2045176180
  .word 404644653
  .word 3059080422
  .word 1418548895
  .word 4072984664
  .word 2432453137
.section .bss
.balign 4
snapshot: .space 32
