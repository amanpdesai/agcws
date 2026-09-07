.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 4294967295
  li a2, 1
  li a3, 17
  li a4, 0
  li a5, 2985570848
  li a6, 31
  li a7, 3009348924
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 24304
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1448
.Lloop0:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 91436
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 35
.Lloop1:
  mul a6, a3, a0
  mul a4, a6, a0
  mul a4, a6, a1
  mul a6, a0, a1
  mul a3, a3, a0
  mul a2, a0, a0
  mul a5, a1, a1
  mul a5, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 95630
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 92
.Lloop2:
  divu a0, a5, a6
  divu a6, a1, a7
  divu a2, a2, a0
  divu a5, a3, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 134073
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 120
.Lloop3:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 150030
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 168
.Lloop4:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 163162
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 33
.Lloop5:
  bnez a5, .Lskip5_0
  mv a6, a5
.Lskip5_0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  and a0, a1, a5
  and a5, a1, a5
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 163993
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 76
.Lloop6:
  add a2, a1, a1
  and a2, a5, a0
  or a2, a4, a0
  xor a2, a3, a0
  or a4, a3, a0
  and a7, a7, a1
  or a6, a2, a0
  xor a2, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 1785860748
  .word 145329221
  .word 2799764990
  .word 1159233463
  .word 3813669232
  .word 2173137705
  .word 532606178
  .word 3187041947
  .word 1546510420
  .word 4200946189
  .word 2560414662
  .word 919883135
  .word 3574318904
  .word 1933787377
  .word 293255850
  .word 2947691619
  .word 1307160092
  .word 3961595861
  .word 2321064334
  .word 680532807
  .word 3334968576
  .word 1694437049
  .word 53905522
  .word 2708341291
  .word 1067809764
  .word 3722245533
  .word 2081714006
  .word 441182479
  .word 3095618248
  .word 1455086721
  .word 4109522490
  .word 2468990963
  .word 828459436
  .word 3482895205
  .word 1842363678
  .word 201832151
  .word 2856267920
  .word 1215736393
  .word 3870172162
  .word 2229640635
  .word 589109108
  .word 3243544877
  .word 1603013350
  .word 4257449119
  .word 2616917592
  .word 976386065
  .word 3630821834
  .word 1990290307
  .word 349758780
  .word 3004194549
  .word 1363663022
  .word 4018098791
  .word 2377567264
  .word 737035737
  .word 3391471506
  .word 1750939979
  .word 110408452
  .word 2764844221
  .word 1124312694
  .word 3778748463
  .word 2138216936
  .word 497685409
  .word 3152121178
  .word 1511589651
.section .bss
.balign 4
snapshot: .space 32
