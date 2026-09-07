.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 3463037595
  li a4, 0
  li a5, 3691360859
  li a6, 0
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 40834
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 4
.Lloop0:
  srl a2, a6, a1
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  srl a4, a5, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  or a6, a6, a1
  add a3, a0, a0
  xor a2, a7, a0
  and a6, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 43546
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 210
.Lloop1:
  divu a0, a3, a4
  divu a7, a4, a3
  divu a2, a2, a7
  divu a6, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 57547
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 50
.Lloop2:
  xor a5, a4, a2
  xor a6, a5, a2
  xor a4, a6, a6
  xor a1, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 85296
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 144
.Lloop3:
  mul a2, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 107440
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 760
.Lloop4:
  bnez a2, .Lskip4_0
  mv a5, a1
.Lskip4_0:
  bnez a1, .Lskip4_1
  mv a5, a1
.Lskip4_1:
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 160826
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 256
.Lloop5:
  bnez a2, .Lskip5_0
  mv a0, a2
.Lskip5_0:
  bnez a5, .Lskip5_1
  mv a1, a5
.Lskip5_1:
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 167629
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 848
.Lloop6:
  mul a6, a0, a0
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
  .word 3687895727
  .word 2047364200
  .word 406832673
  .word 3061268442
  .word 1420736915
  .word 4075172684
  .word 2434641157
  .word 794109630
  .word 3448545399
  .word 1808013872
  .word 167482345
  .word 2821918114
  .word 1181386587
  .word 3835822356
  .word 2195290829
  .word 554759302
  .word 3209195071
  .word 1568663544
  .word 4223099313
  .word 2582567786
  .word 942036259
  .word 3596472028
  .word 1955940501
  .word 315408974
  .word 2969844743
  .word 1329313216
  .word 3983748985
  .word 2343217458
  .word 702685931
  .word 3357121700
  .word 1716590173
  .word 76058646
  .word 2730494415
  .word 1089962888
  .word 3744398657
  .word 2103867130
  .word 463335603
  .word 3117771372
  .word 1477239845
  .word 4131675614
  .word 2491144087
  .word 850612560
  .word 3505048329
  .word 1864516802
  .word 223985275
  .word 2878421044
  .word 1237889517
  .word 3892325286
  .word 2251793759
  .word 611262232
  .word 3265698001
  .word 1625166474
  .word 4279602243
  .word 2639070716
  .word 998539189
  .word 3652974958
  .word 2012443431
  .word 371911904
  .word 3026347673
  .word 1385816146
  .word 4040251915
  .word 2399720388
  .word 759188861
  .word 3413624630
.section .bss
.balign 4
snapshot: .space 32
