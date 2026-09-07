.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 0
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 300
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  sll a4, a4, a5
  add a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 50000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 200
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  divu a2, a0, a3
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  divu a6, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 100000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 200
.Lloop2:
  divu a1, a1, a2
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  divu a5, a3, a4
  divu a7, a7, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 150000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 324
.Lloop3:
  or a0, a1, a2
  add a3, a4, a5
  xor a6, a7, a0
  srl a1, a2, a3
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
  .word 1234
  .word 2654437003
  .word 1013905476
  .word 3668341245
  .word 2027809718
  .word 387278191
  .word 3041713960
  .word 1401182433
  .word 4055618202
  .word 2415086675
  .word 774555148
  .word 3428990917
  .word 1788459390
  .word 147927863
  .word 2802363632
  .word 1161832105
  .word 3816267874
  .word 2175736347
  .word 535204820
  .word 3189640589
  .word 1549109062
  .word 4203544831
  .word 2563013304
  .word 922481777
  .word 3576917546
  .word 1936386019
  .word 295854492
  .word 2950290261
  .word 1309758734
  .word 3964194503
  .word 2323662976
  .word 683131449
  .word 3337567218
  .word 1697035691
  .word 56504164
  .word 2710939933
  .word 1070408406
  .word 3724844175
  .word 2084312648
  .word 443781121
  .word 3098216890
  .word 1457685363
  .word 4112121132
  .word 2471589605
  .word 831058078
  .word 3485493847
  .word 1844962320
  .word 204430793
  .word 2858866562
  .word 1218335035
  .word 3872770804
  .word 2232239277
  .word 591707750
  .word 3246143519
  .word 1605611992
  .word 4260047761
  .word 2619516234
  .word 978984707
  .word 3633420476
  .word 1992888949
  .word 352357422
  .word 3006793191
  .word 1366261664
  .word 4020697433
.section .bss
.balign 4
snapshot: .space 32
