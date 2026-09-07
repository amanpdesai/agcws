.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4294967295
  li a2, 4294967295
  li a3, 17
  li a4, 4294967295
  li a5, 0
  li a6, 2308648542
  li a7, 239383268
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 64539
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 39
.Lloop0:
  divu a2, a2, a0
  divu a3, a3, a1
  divu a2, a3, a0
  divu a3, a3, a0
  divu a3, a7, a1
  divu a2, a0, a1
  divu a6, a2, a1
  divu a4, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 85875
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 224
.Lloop1:
  srl a4, a0, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 154150
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 940
.Lloop2:
  divu a7, a1, a0
  divu a4, a5, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 179540
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 420
.Lloop3:
  divu a5, a3, a1
  divu a3, a6, a1
  divu a4, a5, a0
  divu a7, a4, a0
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
  .word 1642314628
  .word 1783101
  .word 2656218870
  .word 1015687343
  .word 3670123112
  .word 2029591585
  .word 389060058
  .word 3043495827
  .word 1402964300
  .word 4057400069
  .word 2416868542
  .word 776337015
  .word 3430772784
  .word 1790241257
  .word 149709730
  .word 2804145499
  .word 1163613972
  .word 3818049741
  .word 2177518214
  .word 536986687
  .word 3191422456
  .word 1550890929
  .word 4205326698
  .word 2564795171
  .word 924263644
  .word 3578699413
  .word 1938167886
  .word 297636359
  .word 2952072128
  .word 1311540601
  .word 3965976370
  .word 2325444843
  .word 684913316
  .word 3339349085
  .word 1698817558
  .word 58286031
  .word 2712721800
  .word 1072190273
  .word 3726626042
  .word 2086094515
  .word 445562988
  .word 3099998757
  .word 1459467230
  .word 4113902999
  .word 2473371472
  .word 832839945
  .word 3487275714
  .word 1846744187
  .word 206212660
  .word 2860648429
  .word 1220116902
  .word 3874552671
  .word 2234021144
  .word 593489617
  .word 3247925386
  .word 1607393859
  .word 4261829628
  .word 2621298101
  .word 980766574
  .word 3635202343
  .word 1994670816
  .word 354139289
  .word 3008575058
  .word 1368043531
.section .bss
.balign 4
snapshot: .space 32
