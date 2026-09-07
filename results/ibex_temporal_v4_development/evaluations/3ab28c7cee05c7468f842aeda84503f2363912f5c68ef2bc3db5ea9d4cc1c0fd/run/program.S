.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 0
  li a3, 17
  li a4, 4294967295
  li a5, 31
  li a6, 17
  li a7, 31
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
  li t6, 256
.Lloop0:
  srl a2, a1, a0
  mul a4, a2, a3
  xor a6, a4, a5
  bnez a7, .Lskip0_3
  mv a4, a2
.Lskip0_3:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 40000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 256
.Lloop1:
  sll a7, a6, a1
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  srl a3, a1, a2
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
  li t6, 256
.Lloop2:
  add a1, a6, a7
  and a5, a3, a0
  or a7, a5, a1
  mul a2, a3, a4
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
  li t6, 256
.Lloop3:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  xor a0, a0, a1
  add a4, a2, a3
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
  .word 4043725752
  .word 2403194225
  .word 762662698
  .word 3417098467
  .word 1776566940
  .word 136035413
  .word 2790471182
  .word 1149939655
  .word 3804375424
  .word 2163843897
  .word 523312370
  .word 3177748139
  .word 1537216612
  .word 4191652381
  .word 2551120854
  .word 910589327
  .word 3565025096
  .word 1924493569
  .word 283962042
  .word 2938397811
  .word 1297866284
  .word 3952302053
  .word 2311770526
  .word 671238999
  .word 3325674768
  .word 1685143241
  .word 44611714
  .word 2699047483
  .word 1058515956
  .word 3712951725
  .word 2072420198
  .word 431888671
  .word 3086324440
  .word 1445792913
  .word 4100228682
  .word 2459697155
  .word 819165628
  .word 3473601397
  .word 1833069870
  .word 192538343
  .word 2846974112
  .word 1206442585
  .word 3860878354
  .word 2220346827
  .word 579815300
  .word 3234251069
  .word 1593719542
  .word 4248155311
  .word 2607623784
  .word 967092257
  .word 3621528026
  .word 1980996499
  .word 340464972
  .word 2994900741
  .word 1354369214
  .word 4008804983
  .word 2368273456
  .word 727741929
  .word 3382177698
  .word 1741646171
  .word 101114644
  .word 2755550413
  .word 1115018886
  .word 3769454655
.section .bss
.balign 4
snapshot: .space 32
