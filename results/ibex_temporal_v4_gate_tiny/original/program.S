.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 17
  li a2, 4294967295
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
  li t6, 511
.Lloop0:
  add a2, a0, a1
  xor a3, a1, a2
  and a4, a2, a3
  or a5, a3, a4
  sll a6, a4, a5
  srl a7, a5, a6
  mul a2, a6, a7
  divu a3, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  xor a3, a1, a2
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  and a4, a2, a3
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  or a5, a3, a4
  li s9, 0
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  sll a6, a4, a5
  li s9, 0
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  srl a7, a5, a6
  li s9, 0
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  mul a2, a6, a7
  li s9, 0
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  divu a3, a7, a0
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
  .word 123
  .word 2654435892
  .word 1013904365
  .word 3668340134
  .word 2027808607
  .word 387277080
  .word 3041712849
  .word 1401181322
  .word 4055617091
  .word 2415085564
  .word 774554037
  .word 3428989806
  .word 1788458279
  .word 147926752
  .word 2802362521
  .word 1161830994
  .word 3816266763
  .word 2175735236
  .word 535203709
  .word 3189639478
  .word 1549107951
  .word 4203543720
  .word 2563012193
  .word 922480666
  .word 3576916435
  .word 1936384908
  .word 295853381
  .word 2950289150
  .word 1309757623
  .word 3964193392
  .word 2323661865
  .word 683130338
  .word 3337566107
  .word 1697034580
  .word 56503053
  .word 2710938822
  .word 1070407295
  .word 3724843064
  .word 2084311537
  .word 443780010
  .word 3098215779
  .word 1457684252
  .word 4112120021
  .word 2471588494
  .word 831056967
  .word 3485492736
  .word 1844961209
  .word 204429682
  .word 2858865451
  .word 1218333924
  .word 3872769693
  .word 2232238166
  .word 591706639
  .word 3246142408
  .word 1605610881
  .word 4260046650
  .word 2619515123
  .word 978983596
  .word 3633419365
  .word 1992887838
  .word 352356311
  .word 3006792080
  .word 1366260553
  .word 4020696322
.section .bss
.balign 4
snapshot: .space 32
