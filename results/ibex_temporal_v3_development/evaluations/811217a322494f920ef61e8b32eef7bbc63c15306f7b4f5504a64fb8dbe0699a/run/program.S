.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
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
  li t6, 128
.Lloop0:
  add a0, a0, a0
  add a1, a1, a1
  add a2, a2, a2
  add a3, a3, a3
  add a4, a4, a4
  add a5, a5, a5
  add a6, a6, a6
  add a7, a7, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 5000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  xor a0, a0, a1
  xor a1, a1, a2
  xor a2, a2, a3
  xor a3, a3, a4
  xor a4, a4, a5
  xor a5, a5, a6
  xor a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 10000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  srl a0, a0, a1
  srl a1, a1, a2
  srl a2, a2, a3
  srl a3, a3, a4
  srl a4, a4, a5
  srl a5, a5, a6
  srl a6, a6, a7
  srl a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 15000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a0, a0, a1
  divu a1, a1, a1
  divu a2, a2, a1
  divu a3, a3, a1
  divu a4, a4, a1
  divu a5, a5, a1
  divu a6, a6, a1
  divu a7, a7, a1
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
  .word 2000000001
  .word 359468474
  .word 3013904243
  .word 1373372716
  .word 4027808485
  .word 2387276958
  .word 746745431
  .word 3401181200
  .word 1760649673
  .word 120118146
  .word 2774553915
  .word 1134022388
  .word 3788458157
  .word 2147926630
  .word 507395103
  .word 3161830872
  .word 1521299345
  .word 4175735114
  .word 2535203587
  .word 894672060
  .word 3549107829
  .word 1908576302
  .word 268044775
  .word 2922480544
  .word 1281949017
  .word 3936384786
  .word 2295853259
  .word 655321732
  .word 3309757501
  .word 1669225974
  .word 28694447
  .word 2683130216
  .word 1042598689
  .word 3697034458
  .word 2056502931
  .word 415971404
  .word 3070407173
  .word 1429875646
  .word 4084311415
  .word 2443779888
  .word 803248361
  .word 3457684130
  .word 1817152603
  .word 176621076
  .word 2831056845
  .word 1190525318
  .word 3844961087
  .word 2204429560
  .word 563898033
  .word 3218333802
  .word 1577802275
  .word 4232238044
  .word 2591706517
  .word 951174990
  .word 3605610759
  .word 1965079232
  .word 324547705
  .word 2978983474
  .word 1338451947
  .word 3992887716
  .word 2352356189
  .word 711824662
  .word 3366260431
  .word 1725728904
.section .bss
.balign 4
snapshot: .space 32
