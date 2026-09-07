.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 17
  li a3, 31
  li a4, 0
  li a5, 1
  li a6, 1
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 28346
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 209
.Lloop0:
  divu a6, a4, a7
  divu a3, a0, a5
  divu a5, a4, a5
  divu a0, a7, a0
  divu a4, a3, a0
  divu a0, a6, a3
  divu a1, a6, a3
  divu a5, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 57230
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 402
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 148039
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 408
.Lloop2:
  xor a4, a1, a0
  or a4, a1, a0
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
  .word 1063110037
  .word 3717545806
  .word 2077014279
  .word 436482752
  .word 3090918521
  .word 1450386994
  .word 4104822763
  .word 2464291236
  .word 823759709
  .word 3478195478
  .word 1837663951
  .word 197132424
  .word 2851568193
  .word 1211036666
  .word 3865472435
  .word 2224940908
  .word 584409381
  .word 3238845150
  .word 1598313623
  .word 4252749392
  .word 2612217865
  .word 971686338
  .word 3626122107
  .word 1985590580
  .word 345059053
  .word 2999494822
  .word 1358963295
  .word 4013399064
  .word 2372867537
  .word 732336010
  .word 3386771779
  .word 1746240252
  .word 105708725
  .word 2760144494
  .word 1119612967
  .word 3774048736
  .word 2133517209
  .word 492985682
  .word 3147421451
  .word 1506889924
  .word 4161325693
  .word 2520794166
  .word 880262639
  .word 3534698408
  .word 1894166881
  .word 253635354
  .word 2908071123
  .word 1267539596
  .word 3921975365
  .word 2281443838
  .word 640912311
  .word 3295348080
  .word 1654816553
  .word 14285026
  .word 2668720795
  .word 1028189268
  .word 3682625037
  .word 2042093510
  .word 401561983
  .word 3055997752
  .word 1415466225
  .word 4069901994
  .word 2429370467
  .word 788838940
.section .bss
.balign 4
snapshot: .space 32
