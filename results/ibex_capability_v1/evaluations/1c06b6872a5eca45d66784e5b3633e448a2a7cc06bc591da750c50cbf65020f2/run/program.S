.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 3541254524
  li a2, 4294967295
  li a3, 3953422350
  li a4, 1
  li a5, 4294967295
  li a6, 17
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 116843
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 302
.Lloop0:
  mul a3, a0, a0
  mul a7, a0, a0
  mul a5, a3, a0
  mul a4, a1, a1
  mul a2, a1, a1
  mul a2, a5, a0
  mul a5, a5, a0
  mul a2, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 178031
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 840
.Lloop1:
  divu a2, a0, a1
  srl a3, a4, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 2958880549
  .word 1318349022
  .word 3972784791
  .word 2332253264
  .word 691721737
  .word 3346157506
  .word 1705625979
  .word 65094452
  .word 2719530221
  .word 1078998694
  .word 3733434463
  .word 2092902936
  .word 452371409
  .word 3106807178
  .word 1466275651
  .word 4120711420
  .word 2480179893
  .word 839648366
  .word 3494084135
  .word 1853552608
  .word 213021081
  .word 2867456850
  .word 1226925323
  .word 3881361092
  .word 2240829565
  .word 600298038
  .word 3254733807
  .word 1614202280
  .word 4268638049
  .word 2628106522
  .word 987574995
  .word 3642010764
  .word 2001479237
  .word 360947710
  .word 3015383479
  .word 1374851952
  .word 4029287721
  .word 2388756194
  .word 748224667
  .word 3402660436
  .word 1762128909
  .word 121597382
  .word 2776033151
  .word 1135501624
  .word 3789937393
  .word 2149405866
  .word 508874339
  .word 3163310108
  .word 1522778581
  .word 4177214350
  .word 2536682823
  .word 896151296
  .word 3550587065
  .word 1910055538
  .word 269524011
  .word 2923959780
  .word 1283428253
  .word 3937864022
  .word 2297332495
  .word 656800968
  .word 3311236737
  .word 1670705210
  .word 30173683
  .word 2684609452
.section .bss
.balign 4
snapshot: .space 32
