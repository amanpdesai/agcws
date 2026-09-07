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
  li t6, 129
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 129
.Lloop1:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 126
.Lloop2:
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a1
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 126
.Lloop3:
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop3
  divu a0, a0, a1
  li s9, 100000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 126
.Lloop4:
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop4
  divu a0, a0, a1
  li s9, 125000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 126
.Lloop5:
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop5
  divu a0, a0, a1
  li s9, 150000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 129
.Lloop6:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 175000
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 129
.Lloop7:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 1000000007
  .word 3654435776
  .word 2013904249
  .word 373372722
  .word 3027808491
  .word 1387276964
  .word 4041712733
  .word 2401181206
  .word 760649679
  .word 3415085448
  .word 1774553921
  .word 134022394
  .word 2788458163
  .word 1147926636
  .word 3802362405
  .word 2161830878
  .word 521299351
  .word 3175735120
  .word 1535203593
  .word 4189639362
  .word 2549107835
  .word 908576308
  .word 3563012077
  .word 1922480550
  .word 281949023
  .word 2936384792
  .word 1295853265
  .word 3950289034
  .word 2309757507
  .word 669225980
  .word 3323661749
  .word 1683130222
  .word 42598695
  .word 2697034464
  .word 1056502937
  .word 3710938706
  .word 2070407179
  .word 429875652
  .word 3084311421
  .word 1443779894
  .word 4098215663
  .word 2457684136
  .word 817152609
  .word 3471588378
  .word 1831056851
  .word 190525324
  .word 2844961093
  .word 1204429566
  .word 3858865335
  .word 2218333808
  .word 577802281
  .word 3232238050
  .word 1591706523
  .word 4246142292
  .word 2605610765
  .word 965079238
  .word 3619515007
  .word 1978983480
  .word 338451953
  .word 2992887722
  .word 1352356195
  .word 4006791964
  .word 2366260437
  .word 725728910
.section .bss
.balign 4
snapshot: .space 32
