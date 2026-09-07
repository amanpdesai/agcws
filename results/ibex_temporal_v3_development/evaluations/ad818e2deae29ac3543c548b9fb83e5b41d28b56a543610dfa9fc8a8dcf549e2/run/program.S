.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 125
.Lloop0:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 125
.Lloop1:
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 125
.Lloop2:
  divu a4, a0, a1
  divu a5, a2, a3
  divu a6, a4, a5
  divu a7, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 100
.Lloop3:
  bnez a0, .Lskip3_0
  mv a0, a1
.Lskip3_0:
  bnez a1, .Lskip3_1
  mv a1, a2
.Lskip3_1:
  bnez a2, .Lskip3_2
  mv a2, a3
.Lskip3_2:
  bnez a3, .Lskip3_3
  mv a3, a4
.Lskip3_3:
  bnez a4, .Lskip3_4
  mv a4, a5
.Lskip3_4:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 140000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 125
.Lloop4:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 180000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 74
.Lloop5:
  bnez a0, .Lskip5_0
  mv a0, a1
.Lskip5_0:
  bnez a1, .Lskip5_1
  mv a1, a2
.Lskip5_1:
  bnez a2, .Lskip5_2
  mv a2, a3
.Lskip5_2:
  bnez a3, .Lskip5_3
  mv a3, a4
.Lskip5_3:
  bnez a4, .Lskip5_4
  mv a4, a5
.Lskip5_4:
  bnez a5, .Lskip5_5
  mv a5, a6
.Lskip5_5:
  bnez a6, .Lskip5_6
  mv a6, a7
.Lskip5_6:
  bnez a7, .Lskip5_7
  mv a7, a0
.Lskip5_7:
  addi t6, t6, -1
  bnez t6, .Lloop5
  bnez a0, .Ltail_skip5_0
  mv a0, a1
.Ltail_skip5_0:
  bnez a1, .Ltail_skip5_1
  mv a1, a2
.Ltail_skip5_1:
  bnez a2, .Ltail_skip5_2
  mv a2, a3
.Ltail_skip5_2:
  bnez a3, .Ltail_skip5_3
  mv a3, a4
.Ltail_skip5_3:
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
  .word 1000000001
  .word 3654435770
  .word 2013904243
  .word 373372716
  .word 3027808485
  .word 1387276958
  .word 4041712727
  .word 2401181200
  .word 760649673
  .word 3415085442
  .word 1774553915
  .word 134022388
  .word 2788458157
  .word 1147926630
  .word 3802362399
  .word 2161830872
  .word 521299345
  .word 3175735114
  .word 1535203587
  .word 4189639356
  .word 2549107829
  .word 908576302
  .word 3563012071
  .word 1922480544
  .word 281949017
  .word 2936384786
  .word 1295853259
  .word 3950289028
  .word 2309757501
  .word 669225974
  .word 3323661743
  .word 1683130216
  .word 42598689
  .word 2697034458
  .word 1056502931
  .word 3710938700
  .word 2070407173
  .word 429875646
  .word 3084311415
  .word 1443779888
  .word 4098215657
  .word 2457684130
  .word 817152603
  .word 3471588372
  .word 1831056845
  .word 190525318
  .word 2844961087
  .word 1204429560
  .word 3858865329
  .word 2218333802
  .word 577802275
  .word 3232238044
  .word 1591706517
  .word 4246142286
  .word 2605610759
  .word 965079232
  .word 3619515001
  .word 1978983474
  .word 338451947
  .word 2992887716
  .word 1352356189
  .word 4006791958
  .word 2366260431
  .word 725728904
.section .bss
.balign 4
snapshot: .space 32
