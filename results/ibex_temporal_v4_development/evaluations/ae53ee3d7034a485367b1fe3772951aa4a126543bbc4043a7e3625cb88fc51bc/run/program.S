.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 2495285818
  li a1, 2791579571
  li a2, 0
  li a3, 17
  li a4, 4294967295
  li a5, 1
  li a6, 4294967295
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 134469
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1024
.Lloop0:
  bnez a1, .Lskip0_0
  mv a4, a3
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a1, a5
.Lskip0_1:
  bnez a7, .Lskip0_2
  mv a1, a5
.Lskip0_2:
  bnez a6, .Lskip0_3
  mv a2, a4
.Lskip0_3:
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 2096112259
  .word 455580732
  .word 3110016501
  .word 1469484974
  .word 4123920743
  .word 2483389216
  .word 842857689
  .word 3497293458
  .word 1856761931
  .word 216230404
  .word 2870666173
  .word 1230134646
  .word 3884570415
  .word 2244038888
  .word 603507361
  .word 3257943130
  .word 1617411603
  .word 4271847372
  .word 2631315845
  .word 990784318
  .word 3645220087
  .word 2004688560
  .word 364157033
  .word 3018592802
  .word 1378061275
  .word 4032497044
  .word 2391965517
  .word 751433990
  .word 3405869759
  .word 1765338232
  .word 124806705
  .word 2779242474
  .word 1138710947
  .word 3793146716
  .word 2152615189
  .word 512083662
  .word 3166519431
  .word 1525987904
  .word 4180423673
  .word 2539892146
  .word 899360619
  .word 3553796388
  .word 1913264861
  .word 272733334
  .word 2927169103
  .word 1286637576
  .word 3941073345
  .word 2300541818
  .word 660010291
  .word 3314446060
  .word 1673914533
  .word 33383006
  .word 2687818775
  .word 1047287248
  .word 3701723017
  .word 2061191490
  .word 420659963
  .word 3075095732
  .word 1434564205
  .word 4088999974
  .word 2448468447
  .word 807936920
  .word 3462372689
  .word 1821841162
.section .bss
.balign 4
snapshot: .space 32
