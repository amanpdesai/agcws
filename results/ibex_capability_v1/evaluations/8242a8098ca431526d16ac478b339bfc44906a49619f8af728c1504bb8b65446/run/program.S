.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 17
  li a3, 4294967295
  li a4, 1076035761
  li a5, 4294967295
  li a6, 1
  li a7, 4294967295
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
  li t6, 350
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 20000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 250
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  mul a2, a2, a3
  sll a4, a4, a1
  srl a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 30000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 150
.Lloop2:
  divu a0, a0, a7
  bnez a1, .Lskip2_1
  mv a1, a0
.Lskip2_1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 40000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 274
.Lloop3:
  add a6, a6, a7
  or a0, a0, a1
  bnez a2, .Lskip3_2
  mv a2, a3
.Lskip3_2:
  mul a4, a4, a5
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
  .word 1000000000
  .word 3654435769
  .word 2013904242
  .word 373372715
  .word 3027808484
  .word 1387276957
  .word 4041712726
  .word 2401181199
  .word 760649672
  .word 3415085441
  .word 1774553914
  .word 134022387
  .word 2788458156
  .word 1147926629
  .word 3802362398
  .word 2161830871
  .word 521299344
  .word 3175735113
  .word 1535203586
  .word 4189639355
  .word 2549107828
  .word 908576301
  .word 3563012070
  .word 1922480543
  .word 281949016
  .word 2936384785
  .word 1295853258
  .word 3950289027
  .word 2309757500
  .word 669225973
  .word 3323661742
  .word 1683130215
  .word 42598688
  .word 2697034457
  .word 1056502930
  .word 3710938699
  .word 2070407172
  .word 429875645
  .word 3084311414
  .word 1443779887
  .word 4098215656
  .word 2457684129
  .word 817152602
  .word 3471588371
  .word 1831056844
  .word 190525317
  .word 2844961086
  .word 1204429559
  .word 3858865328
  .word 2218333801
  .word 577802274
  .word 3232238043
  .word 1591706516
  .word 4246142285
  .word 2605610758
  .word 965079231
  .word 3619515000
  .word 1978983473
  .word 338451946
  .word 2992887715
  .word 1352356188
  .word 4006791957
  .word 2366260430
  .word 725728903
.section .bss
.balign 4
snapshot: .space 32
