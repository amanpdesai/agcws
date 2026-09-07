.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 42
  li a1, 42
  li a2, 42
  li a3, 42
  li a4, 42
  li a5, 42
  li a6, 42
  li a7, 42
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 5000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 266
.Lloop0:
  mul a2, a0, a1
  xor a4, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  mul a2, a0, a1
  xor a4, a2, a3
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
  li t6, 266
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a3, a1, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a3, a1, a2
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 85000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 266
.Lloop2:
  sll a2, a0, a1
  srl a4, a2, a3
  and a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a2, a0, a1
  srl a4, a2, a3
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 110000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 266
.Lloop3:
  bnez a7, .Lskip3_0
  mv a5, a6
.Lskip3_0:
  or a3, a5, a4
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  bnez a7, .Ltail_skip3_0
  mv a5, a6
.Ltail_skip3_0:
  or a3, a5, a4
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 160000
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 298
.Lloop4:
  mul a2, a0, a1
  add a4, a2, a3
  xor a6, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop4
  mul a2, a0, a1
  add a4, a2, a3
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
  .word 12345678
  .word 2666781447
  .word 1026249920
  .word 3680685689
  .word 2040154162
  .word 399622635
  .word 3054058404
  .word 1413526877
  .word 4067962646
  .word 2427431119
  .word 786899592
  .word 3441335361
  .word 1800803834
  .word 160272307
  .word 2814708076
  .word 1174176549
  .word 3828612318
  .word 2188080791
  .word 547549264
  .word 3201985033
  .word 1561453506
  .word 4215889275
  .word 2575357748
  .word 934826221
  .word 3589261990
  .word 1948730463
  .word 308198936
  .word 2962634705
  .word 1322103178
  .word 3976538947
  .word 2336007420
  .word 695475893
  .word 3349911662
  .word 1709380135
  .word 68848608
  .word 2723284377
  .word 1082752850
  .word 3737188619
  .word 2096657092
  .word 456125565
  .word 3110561334
  .word 1470029807
  .word 4124465576
  .word 2483934049
  .word 843402522
  .word 3497838291
  .word 1857306764
  .word 216775237
  .word 2871211006
  .word 1230679479
  .word 3885115248
  .word 2244583721
  .word 604052194
  .word 3258487963
  .word 1617956436
  .word 4272392205
  .word 2631860678
  .word 991329151
  .word 3645764920
  .word 2005233393
  .word 364701866
  .word 3019137635
  .word 1378606108
  .word 4033041877
.section .bss
.balign 4
snapshot: .space 32
