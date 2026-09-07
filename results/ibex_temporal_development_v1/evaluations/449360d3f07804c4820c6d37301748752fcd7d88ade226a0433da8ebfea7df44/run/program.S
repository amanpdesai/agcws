.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 512
.Lloop0:
  add a1, a0, a1
  xor a2, a1, a2
  mul a3, a2, a3
  add a4, a3, a4
  xor a5, a4, a5
  and a6, a5, a6
  or a7, a6, a7
  sll a0, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 987654322
  .word 3642090091
  .word 2001558564
  .word 361027037
  .word 3015462806
  .word 1374931279
  .word 4029367048
  .word 2388835521
  .word 748303994
  .word 3402739763
  .word 1762208236
  .word 121676709
  .word 2776112478
  .word 1135580951
  .word 3790016720
  .word 2149485193
  .word 508953666
  .word 3163389435
  .word 1522857908
  .word 4177293677
  .word 2536762150
  .word 896230623
  .word 3550666392
  .word 1910134865
  .word 269603338
  .word 2924039107
  .word 1283507580
  .word 3937943349
  .word 2297411822
  .word 656880295
  .word 3311316064
  .word 1670784537
  .word 30253010
  .word 2684688779
  .word 1044157252
  .word 3698593021
  .word 2058061494
  .word 417529967
  .word 3071965736
  .word 1431434209
  .word 4085869978
  .word 2445338451
  .word 804806924
  .word 3459242693
  .word 1818711166
  .word 178179639
  .word 2832615408
  .word 1192083881
  .word 3846519650
  .word 2205988123
  .word 565456596
  .word 3219892365
  .word 1579360838
  .word 4233796607
  .word 2593265080
  .word 952733553
  .word 3607169322
  .word 1966637795
  .word 326106268
  .word 2980542037
  .word 1340010510
  .word 3994446279
  .word 2353914752
  .word 713383225
.section .bss
.balign 4
snapshot: .space 32
