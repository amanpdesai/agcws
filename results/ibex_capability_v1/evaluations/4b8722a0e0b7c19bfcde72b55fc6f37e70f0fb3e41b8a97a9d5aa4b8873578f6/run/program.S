.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 10
  li a1, 20
  li a2, 30
  li a3, 40
  li a4, 50
  li a5, 60
  li a6, 70
  li a7, 80
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
  li t6, 341
.Lloop0:
  add a2, a0, a1
  sll a4, a2, a3
  add a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 45000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 341
.Lloop1:
  mul a0, a0, a1
  mul a2, a2, a3
  mul a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
  mul a0, a0, a1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 95000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 256
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 145000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 256
.Lloop3:
  bnez a0, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  and a5, a3, a4
  or a7, a5, a6
  xor a1, a7, a0
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
  .word 20240521
  .word 2674676290
  .word 1034144763
  .word 3688580532
  .word 2048049005
  .word 407517478
  .word 3061953247
  .word 1421421720
  .word 4075857489
  .word 2435325962
  .word 794794435
  .word 3449230204
  .word 1808698677
  .word 168167150
  .word 2822602919
  .word 1182071392
  .word 3836507161
  .word 2195975634
  .word 555444107
  .word 3209879876
  .word 1569348349
  .word 4223784118
  .word 2583252591
  .word 942721064
  .word 3597156833
  .word 1956625306
  .word 316093779
  .word 2970529548
  .word 1329998021
  .word 3984433790
  .word 2343902263
  .word 703370736
  .word 3357806505
  .word 1717274978
  .word 76743451
  .word 2731179220
  .word 1090647693
  .word 3745083462
  .word 2104551935
  .word 464020408
  .word 3118456177
  .word 1477924650
  .word 4132360419
  .word 2491828892
  .word 851297365
  .word 3505733134
  .word 1865201607
  .word 224670080
  .word 2879105849
  .word 1238574322
  .word 3893010091
  .word 2252478564
  .word 611947037
  .word 3266382806
  .word 1625851279
  .word 4280287048
  .word 2639755521
  .word 999223994
  .word 3653659763
  .word 2013128236
  .word 372596709
  .word 3027032478
  .word 1386500951
  .word 4040936720
.section .bss
.balign 4
snapshot: .space 32
