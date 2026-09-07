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
  li s9, 29922
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 2048
.Lloop0:
  or a6, a5, a6
  divu a6, a4, a3
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
  .word 4043725751
  .word 2403194224
  .word 762662697
  .word 3417098466
  .word 1776566939
  .word 136035412
  .word 2790471181
  .word 1149939654
  .word 3804375423
  .word 2163843896
  .word 523312369
  .word 3177748138
  .word 1537216611
  .word 4191652380
  .word 2551120853
  .word 910589326
  .word 3565025095
  .word 1924493568
  .word 283962041
  .word 2938397810
  .word 1297866283
  .word 3952302052
  .word 2311770525
  .word 671238998
  .word 3325674767
  .word 1685143240
  .word 44611713
  .word 2699047482
  .word 1058515955
  .word 3712951724
  .word 2072420197
  .word 431888670
  .word 3086324439
  .word 1445792912
  .word 4100228681
  .word 2459697154
  .word 819165627
  .word 3473601396
  .word 1833069869
  .word 192538342
  .word 2846974111
  .word 1206442584
  .word 3860878353
  .word 2220346826
  .word 579815299
  .word 3234251068
  .word 1593719541
  .word 4248155310
  .word 2607623783
  .word 967092256
  .word 3621528025
  .word 1980996498
  .word 340464971
  .word 2994900740
  .word 1354369213
  .word 4008804982
  .word 2368273455
  .word 727741928
  .word 3382177697
  .word 1741646170
  .word 101114643
  .word 2755550412
  .word 1115018885
  .word 3769454654
.section .bss
.balign 4
snapshot: .space 32
