.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4023010825
  li a2, 31
  li a3, 1277147764
  li a4, 1
  li a5, 1
  li a6, 0
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 57957
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 202
.Lloop0:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 119066
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 296
.Lloop1:
  sll a3, a3, a1
  and a0, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 130442
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 1888
.Lloop2:
  divu a3, a7, a5
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
  .word 1940485465
  .word 299953938
  .word 2954389707
  .word 1313858180
  .word 3968293949
  .word 2327762422
  .word 687230895
  .word 3341666664
  .word 1701135137
  .word 60603610
  .word 2715039379
  .word 1074507852
  .word 3728943621
  .word 2088412094
  .word 447880567
  .word 3102316336
  .word 1461784809
  .word 4116220578
  .word 2475689051
  .word 835157524
  .word 3489593293
  .word 1849061766
  .word 208530239
  .word 2862966008
  .word 1222434481
  .word 3876870250
  .word 2236338723
  .word 595807196
  .word 3250242965
  .word 1609711438
  .word 4264147207
  .word 2623615680
  .word 983084153
  .word 3637519922
  .word 1996988395
  .word 356456868
  .word 3010892637
  .word 1370361110
  .word 4024796879
  .word 2384265352
  .word 743733825
  .word 3398169594
  .word 1757638067
  .word 117106540
  .word 2771542309
  .word 1131010782
  .word 3785446551
  .word 2144915024
  .word 504383497
  .word 3158819266
  .word 1518287739
  .word 4172723508
  .word 2532191981
  .word 891660454
  .word 3546096223
  .word 1905564696
  .word 265033169
  .word 2919468938
  .word 1278937411
  .word 3933373180
  .word 2292841653
  .word 652310126
  .word 3306745895
  .word 1666214368
.section .bss
.balign 4
snapshot: .space 32
