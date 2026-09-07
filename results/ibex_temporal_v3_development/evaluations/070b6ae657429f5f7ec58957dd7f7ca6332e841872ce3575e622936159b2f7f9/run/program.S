.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 8
  li a1, 7
  li a2, 6
  li a3, 5
  li a4, 4
  li a5, 3
  li a6, 2
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
  li t6, 256
.Lloop0:
  mul a5, a5, a5
  add a0, a1, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a5, a5, a0
  xor a1, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  mul a5, a5, a5
  sll a2, a0, a1
  add a7, a6, a5
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  bnez a5, .Lskip3_0
  mv a5, a4
.Lskip3_0:
  srl a3, a2, a1
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
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
  .word 1000000002
  .word 3654435771
  .word 2013904244
  .word 373372717
  .word 3027808486
  .word 1387276959
  .word 4041712728
  .word 2401181201
  .word 760649674
  .word 3415085443
  .word 1774553916
  .word 134022389
  .word 2788458158
  .word 1147926631
  .word 3802362400
  .word 2161830873
  .word 521299346
  .word 3175735115
  .word 1535203588
  .word 4189639357
  .word 2549107830
  .word 908576303
  .word 3563012072
  .word 1922480545
  .word 281949018
  .word 2936384787
  .word 1295853260
  .word 3950289029
  .word 2309757502
  .word 669225975
  .word 3323661744
  .word 1683130217
  .word 42598690
  .word 2697034459
  .word 1056502932
  .word 3710938701
  .word 2070407174
  .word 429875647
  .word 3084311416
  .word 1443779889
  .word 4098215658
  .word 2457684131
  .word 817152604
  .word 3471588373
  .word 1831056846
  .word 190525319
  .word 2844961088
  .word 1204429561
  .word 3858865330
  .word 2218333803
  .word 577802276
  .word 3232238045
  .word 1591706518
  .word 4246142287
  .word 2605610760
  .word 965079233
  .word 3619515002
  .word 1978983475
  .word 338451948
  .word 2992887717
  .word 1352356190
  .word 4006791959
  .word 2366260432
  .word 725728905
.section .bss
.balign 4
snapshot: .space 32
