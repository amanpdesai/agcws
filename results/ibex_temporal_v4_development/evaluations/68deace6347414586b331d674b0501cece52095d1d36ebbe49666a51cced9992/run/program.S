.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 8000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 225
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 28000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 275
.Lloop1:
  mul a4, a4, a5
  sll a6, a6, a1
  divu a7, a7, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 58000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 250
.Lloop2:
  and a0, a0, a1
  or a2, a2, a3
  bnez a4, .Lskip2_2
  mv a4, a5
.Lskip2_2:
  divu a5, a5, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 88000
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
  add a6, a6, a7
  srl a0, a0, a1
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  xor a4, a4, a5
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
  .word 20230405
  .word 2674666174
  .word 1034134647
  .word 3688570416
  .word 2048038889
  .word 407507362
  .word 3061943131
  .word 1421411604
  .word 4075847373
  .word 2435315846
  .word 794784319
  .word 3449220088
  .word 1808688561
  .word 168157034
  .word 2822592803
  .word 1182061276
  .word 3836497045
  .word 2195965518
  .word 555433991
  .word 3209869760
  .word 1569338233
  .word 4223774002
  .word 2583242475
  .word 942710948
  .word 3597146717
  .word 1956615190
  .word 316083663
  .word 2970519432
  .word 1329987905
  .word 3984423674
  .word 2343892147
  .word 703360620
  .word 3357796389
  .word 1717264862
  .word 76733335
  .word 2731169104
  .word 1090637577
  .word 3745073346
  .word 2104541819
  .word 464010292
  .word 3118446061
  .word 1477914534
  .word 4132350303
  .word 2491818776
  .word 851287249
  .word 3505723018
  .word 1865191491
  .word 224659964
  .word 2879095733
  .word 1238564206
  .word 3892999975
  .word 2252468448
  .word 611936921
  .word 3266372690
  .word 1625841163
  .word 4280276932
  .word 2639745405
  .word 999213878
  .word 3653649647
  .word 2013118120
  .word 372586593
  .word 3027022362
  .word 1386490835
  .word 4040926604
.section .bss
.balign 4
snapshot: .space 32
