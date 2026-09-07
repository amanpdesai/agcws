.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 123456789
  li a1, 987654321
  li a2, 25
  li a3, 2
  li a4, 1
  li a5, 13
  li a6, 13
  li a7, 135792468
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
  li t6, 116
.Lloop0:
  sll a7, a0, a3
  mul a1, a5, a2
  xor a1, a3, a5
  bnez a7, .Lskip0_3
  mv a3, a6
.Lskip0_3:
  add a1, a1, a2
  and a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  sll a7, a0, a3
  mul a1, a5, a2
  xor a1, a3, a5
  bnez a7, .Ltail_skip0_3
  mv a3, a6
.Ltail_skip0_3:
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
  li t6, 350
.Lloop1:
  mul a3, a4, a0
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  srl a4, a6, a4
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 80000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 225
.Lloop2:
  divu a0, a0, a1
  bnez a4, .Lskip2_1
  mv a4, a3
.Lskip2_1:
  and a2, a4, a0
  or a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 120000
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
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  sll a2, a2, a1
  xor a5, a5, a6
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
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
  .word 112233445
  .word 2766669214
  .word 1126137687
  .word 3780573456
  .word 2140041929
  .word 499510402
  .word 3153946171
  .word 1513414644
  .word 4167850413
  .word 2527318886
  .word 886787359
  .word 3541223128
  .word 1900691601
  .word 260160074
  .word 2914595843
  .word 1274064316
  .word 3928500085
  .word 2287968558
  .word 647437031
  .word 3301872800
  .word 1661341273
  .word 20809746
  .word 2675245515
  .word 1034713988
  .word 3689149757
  .word 2048618230
  .word 408086703
  .word 3062522472
  .word 1421990945
  .word 4076426714
  .word 2435895187
  .word 795363660
  .word 3449799429
  .word 1809267902
  .word 168736375
  .word 2823172144
  .word 1182640617
  .word 3837076386
  .word 2196544859
  .word 556013332
  .word 3210449101
  .word 1569917574
  .word 4224353343
  .word 2583821816
  .word 943290289
  .word 3597726058
  .word 1957194531
  .word 316663004
  .word 2971098773
  .word 1330567246
  .word 3985003015
  .word 2344471488
  .word 703939961
  .word 3358375730
  .word 1717844203
  .word 77312676
  .word 2731748445
  .word 1091216918
  .word 3745652687
  .word 2105121160
  .word 464589633
  .word 3119025402
  .word 1478493875
  .word 4132929644
.section .bss
.balign 4
snapshot: .space 32
