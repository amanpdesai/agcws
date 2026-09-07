.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 4294967295
  li a2, 31
  li a3, 17
  li a4, 31
  li a5, 0
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 61392
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 158
.Lloop0:
  bnez a4, .Lskip0_0
  mv a2, a1
.Lskip0_0:
  bnez a7, .Lskip0_1
  mv a5, a0
.Lskip0_1:
  bnez a3, .Lskip0_2
  mv a3, a1
.Lskip0_2:
  bnez a4, .Lskip0_3
  mv a5, a1
.Lskip0_3:
  bnez a4, .Lskip0_4
  mv a5, a1
.Lskip0_4:
  bnez a6, .Lskip0_5
  mv a4, a1
.Lskip0_5:
  bnez a7, .Lskip0_6
  mv a5, a0
.Lskip0_6:
  bnez a0, .Lskip0_7
  mv a3, a1
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 71889
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 676
.Lloop1:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 92177
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 276
.Lloop2:
  bnez a7, .Lskip2_0
  mv a6, a0
.Lskip2_0:
  xor a6, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 116050
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 880
.Lloop3:
  mul a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 175700
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 12
.Lloop4:
  bnez a5, .Lskip4_0
  mv a4, a1
.Lskip4_0:
  bnez a4, .Lskip4_1
  mv a5, a1
.Lskip4_1:
  bnez a2, .Lskip4_2
  mv a7, a0
.Lskip4_2:
  bnez a3, .Lskip4_3
  mv a7, a1
.Lskip4_3:
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 4190998609
  .word 2550467082
  .word 909935555
  .word 3564371324
  .word 1923839797
  .word 283308270
  .word 2937744039
  .word 1297212512
  .word 3951648281
  .word 2311116754
  .word 670585227
  .word 3325020996
  .word 1684489469
  .word 43957942
  .word 2698393711
  .word 1057862184
  .word 3712297953
  .word 2071766426
  .word 431234899
  .word 3085670668
  .word 1445139141
  .word 4099574910
  .word 2459043383
  .word 818511856
  .word 3472947625
  .word 1832416098
  .word 191884571
  .word 2846320340
  .word 1205788813
  .word 3860224582
  .word 2219693055
  .word 579161528
  .word 3233597297
  .word 1593065770
  .word 4247501539
  .word 2606970012
  .word 966438485
  .word 3620874254
  .word 1980342727
  .word 339811200
  .word 2994246969
  .word 1353715442
  .word 4008151211
  .word 2367619684
  .word 727088157
  .word 3381523926
  .word 1740992399
  .word 100460872
  .word 2754896641
  .word 1114365114
  .word 3768800883
  .word 2128269356
  .word 487737829
  .word 3142173598
  .word 1501642071
  .word 4156077840
  .word 2515546313
  .word 875014786
  .word 3529450555
  .word 1888919028
  .word 248387501
  .word 2902823270
  .word 1262291743
  .word 3916727512
.section .bss
.balign 4
snapshot: .space 32
