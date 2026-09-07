.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 314310628
  li a1, 17
  li a2, 4294967295
  li a3, 1
  li a4, 17
  li a5, 1
  li a6, 1
  li a7, 4110638436
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 1150
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1896
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 130890
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 76
.Lloop1:
  bnez a6, .Lskip1_0
  mv a6, a0
.Lskip1_0:
  bnez a4, .Lskip1_1
  mv a6, a1
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a3, a0
.Lskip1_2:
  bnez a2, .Lskip1_3
  mv a2, a1
.Lskip1_3:
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
  .word 3701429864
  .word 2060898337
  .word 420366810
  .word 3074802579
  .word 1434271052
  .word 4088706821
  .word 2448175294
  .word 807643767
  .word 3462079536
  .word 1821548009
  .word 181016482
  .word 2835452251
  .word 1194920724
  .word 3849356493
  .word 2208824966
  .word 568293439
  .word 3222729208
  .word 1582197681
  .word 4236633450
  .word 2596101923
  .word 955570396
  .word 3610006165
  .word 1969474638
  .word 328943111
  .word 2983378880
  .word 1342847353
  .word 3997283122
  .word 2356751595
  .word 716220068
  .word 3370655837
  .word 1730124310
  .word 89592783
  .word 2744028552
  .word 1103497025
  .word 3757932794
  .word 2117401267
  .word 476869740
  .word 3131305509
  .word 1490773982
  .word 4145209751
  .word 2504678224
  .word 864146697
  .word 3518582466
  .word 1878050939
  .word 237519412
  .word 2891955181
  .word 1251423654
  .word 3905859423
  .word 2265327896
  .word 624796369
  .word 3279232138
  .word 1638700611
  .word 4293136380
  .word 2652604853
  .word 1012073326
  .word 3666509095
  .word 2025977568
  .word 385446041
  .word 3039881810
  .word 1399350283
  .word 4053786052
  .word 2413254525
  .word 772722998
  .word 3427158767
.section .bss
.balign 4
snapshot: .space 32
