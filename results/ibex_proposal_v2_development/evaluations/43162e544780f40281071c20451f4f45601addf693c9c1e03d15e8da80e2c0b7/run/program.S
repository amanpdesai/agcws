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
  li t6, 171
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  bnez a5, .Lskip0_5
  mv a5, a6
.Lskip0_5:
  bnez a6, .Lskip0_6
  mv a6, a7
.Lskip0_6:
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 200
.Lloop1:
  xor a5, a5, a6
  sll a6, a6, a7
  srl a7, a7, a0
  add a0, a0, a1
  bnez a1, .Lskip1_4
  mv a1, a2
.Lskip1_4:
  bnez a2, .Lskip1_5
  mv a2, a3
.Lskip1_5:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 160
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  mul a5, a5, a6
  mul a6, a6, a7
  srl a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 179
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
  bnez a0, .Ltail_skip3_0
  mv a0, a1
.Ltail_skip3_0:
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
  .word 1000000006
  .word 3654435775
  .word 2013904248
  .word 373372721
  .word 3027808490
  .word 1387276963
  .word 4041712732
  .word 2401181205
  .word 760649678
  .word 3415085447
  .word 1774553920
  .word 134022393
  .word 2788458162
  .word 1147926635
  .word 3802362404
  .word 2161830877
  .word 521299350
  .word 3175735119
  .word 1535203592
  .word 4189639361
  .word 2549107834
  .word 908576307
  .word 3563012076
  .word 1922480549
  .word 281949022
  .word 2936384791
  .word 1295853264
  .word 3950289033
  .word 2309757506
  .word 669225979
  .word 3323661748
  .word 1683130221
  .word 42598694
  .word 2697034463
  .word 1056502936
  .word 3710938705
  .word 2070407178
  .word 429875651
  .word 3084311420
  .word 1443779893
  .word 4098215662
  .word 2457684135
  .word 817152608
  .word 3471588377
  .word 1831056850
  .word 190525323
  .word 2844961092
  .word 1204429565
  .word 3858865334
  .word 2218333807
  .word 577802280
  .word 3232238049
  .word 1591706522
  .word 4246142291
  .word 2605610764
  .word 965079237
  .word 3619515006
  .word 1978983479
  .word 338451952
  .word 2992887721
  .word 1352356194
  .word 4006791963
  .word 2366260436
  .word 725728909
.section .bss
.balign 4
snapshot: .space 32
