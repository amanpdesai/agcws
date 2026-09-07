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
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 256
.Lloop0:
  divu a0, a0, a1
  divu a1, a1, a1
  divu a2, a2, a1
  divu a3, a3, a1
  divu a4, a4, a1
  divu a5, a5, a1
  divu a6, a6, a1
  divu a7, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  add a0, a0, a1
  add a1, a1, a1
  add a2, a2, a1
  add a3, a3, a1
  add a4, a4, a1
  add a5, a5, a1
  add a6, a6, a1
  add a7, a7, a1
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
  .word 1689309069
  .word 48777542
  .word 2703213311
  .word 1062681784
  .word 3717117553
  .word 2076586026
  .word 436054499
  .word 3090490268
  .word 1449958741
  .word 4104394510
  .word 2463862983
  .word 823331456
  .word 3477767225
  .word 1837235698
  .word 196704171
  .word 2851139940
  .word 1210608413
  .word 3865044182
  .word 2224512655
  .word 583981128
  .word 3238416897
  .word 1597885370
  .word 4252321139
  .word 2611789612
  .word 971258085
  .word 3625693854
  .word 1985162327
  .word 344630800
  .word 2999066569
  .word 1358535042
  .word 4012970811
  .word 2372439284
  .word 731907757
  .word 3386343526
  .word 1745811999
  .word 105280472
  .word 2759716241
  .word 1119184714
  .word 3773620483
  .word 2133088956
  .word 492557429
  .word 3146993198
  .word 1506461671
  .word 4160897440
  .word 2520365913
  .word 879834386
  .word 3534270155
  .word 1893738628
  .word 253207101
  .word 2907642870
  .word 1267111343
  .word 3921547112
  .word 2281015585
  .word 640484058
  .word 3294919827
  .word 1654388300
  .word 13856773
  .word 2668292542
  .word 1027761015
  .word 3682196784
  .word 2041665257
  .word 401133730
  .word 3055569499
  .word 1415037972
.section .bss
.balign 4
snapshot: .space 32
