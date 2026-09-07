.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 3503715093
  li a2, 0
  li a3, 0
  li a4, 17
  li a5, 4294967295
  li a6, 4294967295
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 108218
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 4096
.Lloop0:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
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
  .word 1068961710
  .word 3723397479
  .word 2082865952
  .word 442334425
  .word 3096770194
  .word 1456238667
  .word 4110674436
  .word 2470142909
  .word 829611382
  .word 3484047151
  .word 1843515624
  .word 202984097
  .word 2857419866
  .word 1216888339
  .word 3871324108
  .word 2230792581
  .word 590261054
  .word 3244696823
  .word 1604165296
  .word 4258601065
  .word 2618069538
  .word 977538011
  .word 3631973780
  .word 1991442253
  .word 350910726
  .word 3005346495
  .word 1364814968
  .word 4019250737
  .word 2378719210
  .word 738187683
  .word 3392623452
  .word 1752091925
  .word 111560398
  .word 2765996167
  .word 1125464640
  .word 3779900409
  .word 2139368882
  .word 498837355
  .word 3153273124
  .word 1512741597
  .word 4167177366
  .word 2526645839
  .word 886114312
  .word 3540550081
  .word 1900018554
  .word 259487027
  .word 2913922796
  .word 1273391269
  .word 3927827038
  .word 2287295511
  .word 646763984
  .word 3301199753
  .word 1660668226
  .word 20136699
  .word 2674572468
  .word 1034040941
  .word 3688476710
  .word 2047945183
  .word 407413656
  .word 3061849425
  .word 1421317898
  .word 4075753667
  .word 2435222140
  .word 794690613
.section .bss
.balign 4
snapshot: .space 32
