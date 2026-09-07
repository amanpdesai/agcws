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
  li t6, 150
.Lloop0:
  mul a0, a0, a1
  sll a1, a1, a2
  add a2, a2, a3
  xor a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 125
.Lloop1:
  xor a0, a0, a1
  add a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 112
.Lloop2:
  sll a0, a0, a1
  mul a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  srl a4, a4, a5
  add a5, a5, a6
  xor a6, a6, a7
  sll a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a0, a0, a1
  mul a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 124
.Lloop3:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
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
  .word 1122334467
  .word 3776770236
  .word 2136238709
  .word 495707182
  .word 3150142951
  .word 1509611424
  .word 4164047193
  .word 2523515666
  .word 882984139
  .word 3537419908
  .word 1896888381
  .word 256356854
  .word 2910792623
  .word 1270261096
  .word 3924696865
  .word 2284165338
  .word 643633811
  .word 3298069580
  .word 1657538053
  .word 17006526
  .word 2671442295
  .word 1030910768
  .word 3685346537
  .word 2044815010
  .word 404283483
  .word 3058719252
  .word 1418187725
  .word 4072623494
  .word 2432091967
  .word 791560440
  .word 3445996209
  .word 1805464682
  .word 164933155
  .word 2819368924
  .word 1178837397
  .word 3833273166
  .word 2192741639
  .word 552210112
  .word 3206645881
  .word 1566114354
  .word 4220550123
  .word 2580018596
  .word 939487069
  .word 3593922838
  .word 1953391311
  .word 312859784
  .word 2967295553
  .word 1326764026
  .word 3981199795
  .word 2340668268
  .word 700136741
  .word 3354572510
  .word 1714040983
  .word 73509456
  .word 2727945225
  .word 1087413698
  .word 3741849467
  .word 2101317940
  .word 460786413
  .word 3115222182
  .word 1474690655
  .word 4129126424
  .word 2488594897
  .word 848063370
.section .bss
.balign 4
snapshot: .space 32
