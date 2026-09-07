.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1129164839
  li a1, 17
  li a2, 17
  li a3, 4294967295
  li a4, 0
  li a5, 1
  li a6, 1730245853
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 27616
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 248
.Lloop0:
  divu a5, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 67077
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 393
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 134064
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 704
.Lloop2:
  mul a6, a6, a0
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
  .word 822665469
  .word 3477101238
  .word 1836569711
  .word 196038184
  .word 2850473953
  .word 1209942426
  .word 3864378195
  .word 2223846668
  .word 583315141
  .word 3237750910
  .word 1597219383
  .word 4251655152
  .word 2611123625
  .word 970592098
  .word 3625027867
  .word 1984496340
  .word 343964813
  .word 2998400582
  .word 1357869055
  .word 4012304824
  .word 2371773297
  .word 731241770
  .word 3385677539
  .word 1745146012
  .word 104614485
  .word 2759050254
  .word 1118518727
  .word 3772954496
  .word 2132422969
  .word 491891442
  .word 3146327211
  .word 1505795684
  .word 4160231453
  .word 2519699926
  .word 879168399
  .word 3533604168
  .word 1893072641
  .word 252541114
  .word 2906976883
  .word 1266445356
  .word 3920881125
  .word 2280349598
  .word 639818071
  .word 3294253840
  .word 1653722313
  .word 13190786
  .word 2667626555
  .word 1027095028
  .word 3681530797
  .word 2040999270
  .word 400467743
  .word 3054903512
  .word 1414371985
  .word 4068807754
  .word 2428276227
  .word 787744700
  .word 3442180469
  .word 1801648942
  .word 161117415
  .word 2815553184
  .word 1175021657
  .word 3829457426
  .word 2188925899
  .word 548394372
.section .bss
.balign 4
snapshot: .space 32
