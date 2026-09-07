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
  li t6, 256
.Lloop0:
  divu a0, a0, a1
  divu a1, a0, a1
  divu a2, a0, a1
  divu a3, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a4, a0, a1
  divu a5, a0, a1
  divu a6, a0, a1
  divu a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a0, a0, a1
  divu a1, a0, a1
  divu a2, a0, a1
  divu a3, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a4, a0, a1
  divu a5, a0, a1
  divu a6, a0, a1
  divu a7, a0, a1
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
  .word 1000
  .word 2654436769
  .word 1013905242
  .word 3668341011
  .word 2027809484
  .word 387277957
  .word 3041713726
  .word 1401182199
  .word 4055617968
  .word 2415086441
  .word 774554914
  .word 3428990683
  .word 1788459156
  .word 147927629
  .word 2802363398
  .word 1161831871
  .word 3816267640
  .word 2175736113
  .word 535204586
  .word 3189640355
  .word 1549108828
  .word 4203544597
  .word 2563013070
  .word 922481543
  .word 3576917312
  .word 1936385785
  .word 295854258
  .word 2950290027
  .word 1309758500
  .word 3964194269
  .word 2323662742
  .word 683131215
  .word 3337566984
  .word 1697035457
  .word 56503930
  .word 2710939699
  .word 1070408172
  .word 3724843941
  .word 2084312414
  .word 443780887
  .word 3098216656
  .word 1457685129
  .word 4112120898
  .word 2471589371
  .word 831057844
  .word 3485493613
  .word 1844962086
  .word 204430559
  .word 2858866328
  .word 1218334801
  .word 3872770570
  .word 2232239043
  .word 591707516
  .word 3246143285
  .word 1605611758
  .word 4260047527
  .word 2619516000
  .word 978984473
  .word 3633420242
  .word 1992888715
  .word 352357188
  .word 3006792957
  .word 1366261430
  .word 4020697199
.section .bss
.balign 4
snapshot: .space 32
