.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 17
  li a2, 17
  li a3, 1
  li a4, 31
  li a5, 4294967295
  li a6, 3704985945
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 6891
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 432
.Lloop0:
  mul a1, a4, a3
  mul a1, a3, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 16397
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 36
.Lloop1:
  sll a3, a4, a5
  xor a7, a0, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 28219
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 180
.Lloop2:
  add a1, a2, a4
  sll a5, a0, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  add a7, a2, a2
  mul a5, a2, a1
  divu a3, a0, a0
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  xor a4, a4, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 46345
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 452
.Lloop3:
  and a1, a0, a0
  xor a7, a7, a6
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 68821
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 288
.Lloop4:
  divu a2, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 173699
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 66
.Lloop5:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
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
  .word 214233943
  .word 2868669712
  .word 1228138185
  .word 3882573954
  .word 2242042427
  .word 601510900
  .word 3255946669
  .word 1615415142
  .word 4269850911
  .word 2629319384
  .word 988787857
  .word 3643223626
  .word 2002692099
  .word 362160572
  .word 3016596341
  .word 1376064814
  .word 4030500583
  .word 2389969056
  .word 749437529
  .word 3403873298
  .word 1763341771
  .word 122810244
  .word 2777246013
  .word 1136714486
  .word 3791150255
  .word 2150618728
  .word 510087201
  .word 3164522970
  .word 1523991443
  .word 4178427212
  .word 2537895685
  .word 897364158
  .word 3551799927
  .word 1911268400
  .word 270736873
  .word 2925172642
  .word 1284641115
  .word 3939076884
  .word 2298545357
  .word 658013830
  .word 3312449599
  .word 1671918072
  .word 31386545
  .word 2685822314
  .word 1045290787
  .word 3699726556
  .word 2059195029
  .word 418663502
  .word 3073099271
  .word 1432567744
  .word 4087003513
  .word 2446471986
  .word 805940459
  .word 3460376228
  .word 1819844701
  .word 179313174
  .word 2833748943
  .word 1193217416
  .word 3847653185
  .word 2207121658
  .word 566590131
  .word 3221025900
  .word 1580494373
  .word 4234930142
.section .bss
.balign 4
snapshot: .space 32
