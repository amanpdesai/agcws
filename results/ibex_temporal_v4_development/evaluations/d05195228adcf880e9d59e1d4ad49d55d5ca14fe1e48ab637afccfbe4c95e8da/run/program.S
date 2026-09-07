.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 4294967295
  li a2, 17
  li a3, 31
  li a4, 3019309008
  li a5, 31
  li a6, 31
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 24905
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 127
.Lloop0:
  divu a2, a5, a3
  divu a1, a6, a5
  divu a5, a5, a7
  divu a4, a6, a5
  divu a5, a6, a7
  divu a4, a2, a7
  divu a5, a3, a2
  divu a1, a6, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 39581
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 136
.Lloop1:
  mul a4, a0, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 135796
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 161
.Lloop2:
  mul a4, a7, a1
  and a3, a1, a0
  add a6, a5, a1
  xor a6, a5, a1
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  add a7, a0, a1
  srl a5, a7, a0
  sll a4, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 145012
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 224
.Lloop3:
  mul a6, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 165934
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 40
.Lloop4:
  sll a3, a5, a1
  and a2, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 172173
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 169
.Lloop5:
  or a3, a6, a0
  and a3, a6, a0
  or a4, a5, a0
  or a3, a7, a0
  and a5, a3, a0
  and a6, a2, a1
  add a2, a0, a1
  sll a3, a0, a0
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
  .word 689571866
  .word 3344007635
  .word 1703476108
  .word 62944581
  .word 2717380350
  .word 1076848823
  .word 3731284592
  .word 2090753065
  .word 450221538
  .word 3104657307
  .word 1464125780
  .word 4118561549
  .word 2478030022
  .word 837498495
  .word 3491934264
  .word 1851402737
  .word 210871210
  .word 2865306979
  .word 1224775452
  .word 3879211221
  .word 2238679694
  .word 598148167
  .word 3252583936
  .word 1612052409
  .word 4266488178
  .word 2625956651
  .word 985425124
  .word 3639860893
  .word 1999329366
  .word 358797839
  .word 3013233608
  .word 1372702081
  .word 4027137850
  .word 2386606323
  .word 746074796
  .word 3400510565
  .word 1759979038
  .word 119447511
  .word 2773883280
  .word 1133351753
  .word 3787787522
  .word 2147255995
  .word 506724468
  .word 3161160237
  .word 1520628710
  .word 4175064479
  .word 2534532952
  .word 894001425
  .word 3548437194
  .word 1907905667
  .word 267374140
  .word 2921809909
  .word 1281278382
  .word 3935714151
  .word 2295182624
  .word 654651097
  .word 3309086866
  .word 1668555339
  .word 28023812
  .word 2682459581
  .word 1041928054
  .word 3696363823
  .word 2055832296
  .word 415300769
.section .bss
.balign 4
snapshot: .space 32
