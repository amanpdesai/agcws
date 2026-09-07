.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 891737813
  li a3, 4294967295
  li a4, 1
  li a5, 31
  li a6, 1
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 12402
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 436
.Lloop0:
  divu a5, a7, a1
  divu a7, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 13424
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 20
.Lloop1:
  mul a0, a7, a6
  mul a1, a7, a1
  mul a7, a7, a3
  mul a3, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 55344
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 192
.Lloop2:
  and a7, a3, a1
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 88967
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 76
.Lloop3:
  srl a0, a0, a4
  or a1, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 171937
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 169
.Lloop4:
  and a4, a1, a0
  and a6, a5, a0
  or a3, a0, a1
  add a7, a6, a0
  sll a7, a7, a1
  and a4, a6, a1
  and a3, a2, a1
  sll a7, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 176286
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 1256
.Lloop5:
  srl a7, a5, a0
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
  .word 3402213900
  .word 1761682373
  .word 121150846
  .word 2775586615
  .word 1135055088
  .word 3789490857
  .word 2148959330
  .word 508427803
  .word 3162863572
  .word 1522332045
  .word 4176767814
  .word 2536236287
  .word 895704760
  .word 3550140529
  .word 1909609002
  .word 269077475
  .word 2923513244
  .word 1282981717
  .word 3937417486
  .word 2296885959
  .word 656354432
  .word 3310790201
  .word 1670258674
  .word 29727147
  .word 2684162916
  .word 1043631389
  .word 3698067158
  .word 2057535631
  .word 417004104
  .word 3071439873
  .word 1430908346
  .word 4085344115
  .word 2444812588
  .word 804281061
  .word 3458716830
  .word 1818185303
  .word 177653776
  .word 2832089545
  .word 1191558018
  .word 3845993787
  .word 2205462260
  .word 564930733
  .word 3219366502
  .word 1578834975
  .word 4233270744
  .word 2592739217
  .word 952207690
  .word 3606643459
  .word 1966111932
  .word 325580405
  .word 2980016174
  .word 1339484647
  .word 3993920416
  .word 2353388889
  .word 712857362
  .word 3367293131
  .word 1726761604
  .word 86230077
  .word 2740665846
  .word 1100134319
  .word 3754570088
  .word 2114038561
  .word 473507034
  .word 3127942803
.section .bss
.balign 4
snapshot: .space 32
