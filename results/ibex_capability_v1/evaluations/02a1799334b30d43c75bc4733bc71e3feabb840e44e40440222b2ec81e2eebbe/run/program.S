.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 210710821
  li a2, 1
  li a3, 1
  li a4, 4294967295
  li a5, 4294967295
  li a6, 17
  li a7, 4265691339
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 19253
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 346
.Lloop0:
  mul a7, a7, a1
  mul a5, a5, a0
  mul a6, a2, a0
  mul a7, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 22381
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 78
.Lloop1:
  bnez a2, .Lskip1_0
  mv a3, a0
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a6, a0
.Lskip1_1:
  bnez a7, .Lskip1_2
  mv a7, a0
.Lskip1_2:
  bnez a5, .Lskip1_3
  mv a5, a0
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 37087
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 163
.Lloop2:
  divu a5, a3, a6
  divu a2, a4, a0
  divu a0, a3, a3
  divu a0, a6, a5
  divu a6, a3, a1
  divu a6, a2, a2
  divu a1, a5, a1
  divu a1, a3, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 168127
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 864
.Lloop3:
  divu a2, a0, a3
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 177807
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 58
.Lloop4:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
  .word 4111553103
  .word 2471021576
  .word 830490049
  .word 3484925818
  .word 1844394291
  .word 203862764
  .word 2858298533
  .word 1217767006
  .word 3872202775
  .word 2231671248
  .word 591139721
  .word 3245575490
  .word 1605043963
  .word 4259479732
  .word 2618948205
  .word 978416678
  .word 3632852447
  .word 1992320920
  .word 351789393
  .word 3006225162
  .word 1365693635
  .word 4020129404
  .word 2379597877
  .word 739066350
  .word 3393502119
  .word 1752970592
  .word 112439065
  .word 2766874834
  .word 1126343307
  .word 3780779076
  .word 2140247549
  .word 499716022
  .word 3154151791
  .word 1513620264
  .word 4168056033
  .word 2527524506
  .word 886992979
  .word 3541428748
  .word 1900897221
  .word 260365694
  .word 2914801463
  .word 1274269936
  .word 3928705705
  .word 2288174178
  .word 647642651
  .word 3302078420
  .word 1661546893
  .word 21015366
  .word 2675451135
  .word 1034919608
  .word 3689355377
  .word 2048823850
  .word 408292323
  .word 3062728092
  .word 1422196565
  .word 4076632334
  .word 2436100807
  .word 795569280
  .word 3450005049
  .word 1809473522
  .word 168941995
  .word 2823377764
  .word 1182846237
  .word 3837282006
.section .bss
.balign 4
snapshot: .space 32
