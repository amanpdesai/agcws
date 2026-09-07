.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 15000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 240
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 260
.Lloop1:
  xor a5, a5, a6
  sll a6, a6, a7
  srl a7, a7, a0
  add a0, a0, a1
  xor a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 75000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 200
.Lloop2:
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 95000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 198
.Lloop3:
  mul a0, a0, a1
  mul a1, a2, a3
  mul a2, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop3
  mul a0, a0, a1
  mul a1, a2, a3
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
