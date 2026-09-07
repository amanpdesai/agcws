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
  li s9, 5000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 166
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  bnez a5, .Lskip0_5
  mv a5, a6
.Lskip0_5:
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  li s9, 25000
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
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 55000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 200
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
  li s9, 90000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 219
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
  .word 1000000005
  .word 3654435774
  .word 2013904247
  .word 373372720
  .word 3027808489
  .word 1387276962
  .word 4041712731
  .word 2401181204
  .word 760649677
  .word 3415085446
  .word 1774553919
  .word 134022392
  .word 2788458161
  .word 1147926634
  .word 3802362403
  .word 2161830876
  .word 521299349
  .word 3175735118
  .word 1535203591
  .word 4189639360
  .word 2549107833
  .word 908576306
  .word 3563012075
  .word 1922480548
  .word 281949021
  .word 2936384790
  .word 1295853263
  .word 3950289032
  .word 2309757505
  .word 669225978
  .word 3323661747
  .word 1683130220
  .word 42598693
  .word 2697034462
  .word 1056502935
  .word 3710938704
  .word 2070407177
  .word 429875650
  .word 3084311419
  .word 1443779892
  .word 4098215661
  .word 2457684134
  .word 817152607
  .word 3471588376
  .word 1831056849
  .word 190525322
  .word 2844961091
  .word 1204429564
  .word 3858865333
  .word 2218333806
  .word 577802279
  .word 3232238048
  .word 1591706521
  .word 4246142290
  .word 2605610763
  .word 965079236
  .word 3619515005
  .word 1978983478
  .word 338451951
  .word 2992887720
  .word 1352356193
  .word 4006791962
  .word 2366260435
  .word 725728908
.section .bss
.balign 4
snapshot: .space 32
