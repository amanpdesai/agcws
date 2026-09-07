.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4294967295
  li a2, 17
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 31
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 28390
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 207
.Lloop0:
  bnez a4, .Lskip0_0
  mv a2, a6
.Lskip0_0:
  bnez a2, .Lskip0_1
  mv a1, a3
.Lskip0_1:
  bnez a3, .Lskip0_2
  mv a6, a0
.Lskip0_2:
  bnez a5, .Lskip0_3
  mv a2, a2
.Lskip0_3:
  bnez a0, .Lskip0_4
  mv a3, a5
.Lskip0_4:
  bnez a5, .Lskip0_5
  mv a3, a6
.Lskip0_5:
  bnez a7, .Lskip0_6
  mv a3, a0
.Lskip0_6:
  bnez a0, .Lskip0_7
  mv a7, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 50211
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1344
.Lloop1:
  divu a0, a2, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 126554
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 274
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 3591300883
  .word 1950769356
  .word 310237829
  .word 2964673598
  .word 1324142071
  .word 3978577840
  .word 2338046313
  .word 697514786
  .word 3351950555
  .word 1711419028
  .word 70887501
  .word 2725323270
  .word 1084791743
  .word 3739227512
  .word 2098695985
  .word 458164458
  .word 3112600227
  .word 1472068700
  .word 4126504469
  .word 2485972942
  .word 845441415
  .word 3499877184
  .word 1859345657
  .word 218814130
  .word 2873249899
  .word 1232718372
  .word 3887154141
  .word 2246622614
  .word 606091087
  .word 3260526856
  .word 1619995329
  .word 4274431098
  .word 2633899571
  .word 993368044
  .word 3647803813
  .word 2007272286
  .word 366740759
  .word 3021176528
  .word 1380645001
  .word 4035080770
  .word 2394549243
  .word 754017716
  .word 3408453485
  .word 1767921958
  .word 127390431
  .word 2781826200
  .word 1141294673
  .word 3795730442
  .word 2155198915
  .word 514667388
  .word 3169103157
  .word 1528571630
  .word 4183007399
  .word 2542475872
  .word 901944345
  .word 3556380114
  .word 1915848587
  .word 275317060
  .word 2929752829
  .word 1289221302
  .word 3943657071
  .word 2303125544
  .word 662594017
  .word 3317029786
.section .bss
.balign 4
snapshot: .space 32
