.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1108300482
  li a1, 978658013
  li a2, 31
  li a3, 1
  li a4, 0
  li a5, 17
  li a6, 17
  li a7, 1765682813
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 20000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 166
.Lloop0:
  add a7, a0, a3
  xor a1, a5, a2
  and a1, a3, a5
  sll a3, a7, a6
  add a0, a1, a2
  srl a5, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a7, a0, a3
  xor a1, a5, a2
  and a1, a3, a5
  sll a3, a7, a6
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 60000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 166
.Lloop1:
  bnez a4, .Lskip1_0
  mv a3, a0
.Lskip1_0:
  or a6, a1, a2
  sll a4, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a4, .Ltail_skip1_0
  mv a3, a0
.Ltail_skip1_0:
  or a6, a1, a2
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 120000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 500
.Lloop2:
  sll a5, a6, a1
  add a4, a6, a4
  mul a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 160000
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
  srl a4, a4, a3
  or a2, a4, a0
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
  .word 2886339993
  .word 1245808466
  .word 3900244235
  .word 2259712708
  .word 619181181
  .word 3273616950
  .word 1633085423
  .word 4287521192
  .word 2646989665
  .word 1006458138
  .word 3660893907
  .word 2020362380
  .word 379830853
  .word 3034266622
  .word 1393735095
  .word 4048170864
  .word 2407639337
  .word 767107810
  .word 3421543579
  .word 1781012052
  .word 140480525
  .word 2794916294
  .word 1154384767
  .word 3808820536
  .word 2168289009
  .word 527757482
  .word 3182193251
  .word 1541661724
  .word 4196097493
  .word 2555565966
  .word 915034439
  .word 3569470208
  .word 1928938681
  .word 288407154
  .word 2942842923
  .word 1302311396
  .word 3956747165
  .word 2316215638
  .word 675684111
  .word 3330119880
  .word 1689588353
  .word 49056826
  .word 2703492595
  .word 1062961068
  .word 3717396837
  .word 2076865310
  .word 436333783
  .word 3090769552
  .word 1450238025
  .word 4104673794
  .word 2464142267
  .word 823610740
  .word 3478046509
  .word 1837514982
  .word 196983455
  .word 2851419224
  .word 1210887697
  .word 3865323466
  .word 2224791939
  .word 584260412
  .word 3238696181
  .word 1598164654
  .word 4252600423
  .word 2612068896
.section .bss
.balign 4
snapshot: .space 32
