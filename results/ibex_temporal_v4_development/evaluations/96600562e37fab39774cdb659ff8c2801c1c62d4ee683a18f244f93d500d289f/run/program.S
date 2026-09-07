.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1838657908
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 1316259065
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 45500
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1236
.Lloop0:
  sll a6, a0, a1
  and a5, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 61169
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 111
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 111418
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 30
.Lloop2:
  bnez a4, .Lskip2_0
  mv a2, a0
.Lskip2_0:
  bnez a3, .Lskip2_1
  mv a3, a1
.Lskip2_1:
  bnez a5, .Lskip2_2
  mv a6, a0
.Lskip2_2:
  bnez a0, .Lskip2_3
  mv a3, a1
.Lskip2_3:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 145461
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 308
.Lloop3:
  add a2, a2, a1
  or a7, a1, a1
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
  .word 1690189602
  .word 49658075
  .word 2704093844
  .word 1063562317
  .word 3717998086
  .word 2077466559
  .word 436935032
  .word 3091370801
  .word 1450839274
  .word 4105275043
  .word 2464743516
  .word 824211989
  .word 3478647758
  .word 1838116231
  .word 197584704
  .word 2852020473
  .word 1211488946
  .word 3865924715
  .word 2225393188
  .word 584861661
  .word 3239297430
  .word 1598765903
  .word 4253201672
  .word 2612670145
  .word 972138618
  .word 3626574387
  .word 1986042860
  .word 345511333
  .word 2999947102
  .word 1359415575
  .word 4013851344
  .word 2373319817
  .word 732788290
  .word 3387224059
  .word 1746692532
  .word 106161005
  .word 2760596774
  .word 1120065247
  .word 3774501016
  .word 2133969489
  .word 493437962
  .word 3147873731
  .word 1507342204
  .word 4161777973
  .word 2521246446
  .word 880714919
  .word 3535150688
  .word 1894619161
  .word 254087634
  .word 2908523403
  .word 1267991876
  .word 3922427645
  .word 2281896118
  .word 641364591
  .word 3295800360
  .word 1655268833
  .word 14737306
  .word 2669173075
  .word 1028641548
  .word 3683077317
  .word 2042545790
  .word 402014263
  .word 3056450032
  .word 1415918505
.section .bss
.balign 4
snapshot: .space 32
