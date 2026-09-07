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
  li s9, 10000
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
  add a0, a0, a1
  xor a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30000
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
  mul a4, a4, a5
  sll a6, a6, a1
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  mul a4, a4, a5
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 60000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 170
.Lloop2:
  and a0, a0, a1
  or a2, a2, a3
  bnez a4, .Lskip2_2
  mv a4, a5
.Lskip2_2:
  addi t6, t6, -1
  bnez t6, .Lloop2
  and a0, a0, a1
  or a2, a2, a3
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 90000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 384
.Lloop3:
  add a6, a6, a7
  srl a0, a0, a1
  mul a2, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
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
  .word 1122334455
  .word 3776770224
  .word 2136238697
  .word 495707170
  .word 3150142939
  .word 1509611412
  .word 4164047181
  .word 2523515654
  .word 882984127
  .word 3537419896
  .word 1896888369
  .word 256356842
  .word 2910792611
  .word 1270261084
  .word 3924696853
  .word 2284165326
  .word 643633799
  .word 3298069568
  .word 1657538041
  .word 17006514
  .word 2671442283
  .word 1030910756
  .word 3685346525
  .word 2044814998
  .word 404283471
  .word 3058719240
  .word 1418187713
  .word 4072623482
  .word 2432091955
  .word 791560428
  .word 3445996197
  .word 1805464670
  .word 164933143
  .word 2819368912
  .word 1178837385
  .word 3833273154
  .word 2192741627
  .word 552210100
  .word 3206645869
  .word 1566114342
  .word 4220550111
  .word 2580018584
  .word 939487057
  .word 3593922826
  .word 1953391299
  .word 312859772
  .word 2967295541
  .word 1326764014
  .word 3981199783
  .word 2340668256
  .word 700136729
  .word 3354572498
  .word 1714040971
  .word 73509444
  .word 2727945213
  .word 1087413686
  .word 3741849455
  .word 2101317928
  .word 460786401
  .word 3115222170
  .word 1474690643
  .word 4129126412
  .word 2488594885
  .word 848063358
.section .bss
.balign 4
snapshot: .space 32
