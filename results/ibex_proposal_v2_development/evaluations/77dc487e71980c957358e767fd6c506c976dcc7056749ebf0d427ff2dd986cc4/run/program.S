.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 10
  li a1, 20
  li a2, 30
  li a3, 40
  li a4, 50
  li a5, 60
  li a6, 70
  li a7, 80
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 150
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a6
  bnez a0, .Lskip0_5
  mv a7, a1
.Lskip0_5:
  bnez a1, .Lskip0_6
  mv a6, a2
.Lskip0_6:
  bnez a2, .Lskip0_7
  mv a4, a3
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 240
.Lloop1:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 133
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 224
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
  .word 1000000010
  .word 3654435779
  .word 2013904252
  .word 373372725
  .word 3027808494
  .word 1387276967
  .word 4041712736
  .word 2401181209
  .word 760649682
  .word 3415085451
  .word 1774553924
  .word 134022397
  .word 2788458166
  .word 1147926639
  .word 3802362408
  .word 2161830881
  .word 521299354
  .word 3175735123
  .word 1535203596
  .word 4189639365
  .word 2549107838
  .word 908576311
  .word 3563012080
  .word 1922480553
  .word 281949026
  .word 2936384795
  .word 1295853268
  .word 3950289037
  .word 2309757510
  .word 669225983
  .word 3323661752
  .word 1683130225
  .word 42598698
  .word 2697034467
  .word 1056502940
  .word 3710938709
  .word 2070407182
  .word 429875655
  .word 3084311424
  .word 1443779897
  .word 4098215666
  .word 2457684139
  .word 817152612
  .word 3471588381
  .word 1831056854
  .word 190525327
  .word 2844961096
  .word 1204429569
  .word 3858865338
  .word 2218333811
  .word 577802284
  .word 3232238053
  .word 1591706526
  .word 4246142295
  .word 2605610768
  .word 965079241
  .word 3619515010
  .word 1978983483
  .word 338451956
  .word 2992887725
  .word 1352356198
  .word 4006791967
  .word 2366260440
  .word 725728913
.section .bss
.balign 4
snapshot: .space 32
