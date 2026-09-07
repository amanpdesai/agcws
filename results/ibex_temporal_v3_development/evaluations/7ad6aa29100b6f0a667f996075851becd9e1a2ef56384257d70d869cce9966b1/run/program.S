.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
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
  add a0, a0, a1
  xor a1, a1, a2
  add a2, a2, a3
  xor a3, a3, a0
  add a4, a4, a5
  xor a5, a5, a6
  add a6, a6, a7
  xor a7, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 150000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  add a0, a0, a1
  xor a1, a1, a2
  add a2, a2, a3
  xor a3, a3, a0
  add a4, a4, a5
  xor a5, a5, a6
  add a6, a6, a7
  xor a7, a7, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
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
  .word 123456789
  .word 2777892558
  .word 1137361031
  .word 3791796800
  .word 2151265273
  .word 510733746
  .word 3165169515
  .word 1524637988
  .word 4179073757
  .word 2538542230
  .word 898010703
  .word 3552446472
  .word 1911914945
  .word 271383418
  .word 2925819187
  .word 1285287660
  .word 3939723429
  .word 2299191902
  .word 658660375
  .word 3313096144
  .word 1672564617
  .word 32033090
  .word 2686468859
  .word 1045937332
  .word 3700373101
  .word 2059841574
  .word 419310047
  .word 3073745816
  .word 1433214289
  .word 4087650058
  .word 2447118531
  .word 806587004
  .word 3461022773
  .word 1820491246
  .word 179959719
  .word 2834395488
  .word 1193863961
  .word 3848299730
  .word 2207768203
  .word 567236676
  .word 3221672445
  .word 1581140918
  .word 4235576687
  .word 2595045160
  .word 954513633
  .word 3608949402
  .word 1968417875
  .word 327886348
  .word 2982322117
  .word 1341790590
  .word 3996226359
  .word 2355694832
  .word 715163305
  .word 3369599074
  .word 1729067547
  .word 88536020
  .word 2742971789
  .word 1102440262
  .word 3756876031
  .word 2116344504
  .word 475812977
  .word 3130248746
  .word 1489717219
  .word 4144152988
.section .bss
.balign 4
snapshot: .space 32
