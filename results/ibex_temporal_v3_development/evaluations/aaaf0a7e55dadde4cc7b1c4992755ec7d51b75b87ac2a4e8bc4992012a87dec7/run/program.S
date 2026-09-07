.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 0
  li a3, 1
  li a4, 0
  li a5, 1
  li a6, 0
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
  li t6, 128
.Lloop0:
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  divu a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  divu a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
  divu a6, a6, a7
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
  .word 10000
  .word 2654445769
  .word 1013914242
  .word 3668350011
  .word 2027818484
  .word 387286957
  .word 3041722726
  .word 1401191199
  .word 4055626968
  .word 2415095441
  .word 774563914
  .word 3428999683
  .word 1788468156
  .word 147936629
  .word 2802372398
  .word 1161840871
  .word 3816276640
  .word 2175745113
  .word 535213586
  .word 3189649355
  .word 1549117828
  .word 4203553597
  .word 2563022070
  .word 922490543
  .word 3576926312
  .word 1936394785
  .word 295863258
  .word 2950299027
  .word 1309767500
  .word 3964203269
  .word 2323671742
  .word 683140215
  .word 3337575984
  .word 1697044457
  .word 56512930
  .word 2710948699
  .word 1070417172
  .word 3724852941
  .word 2084321414
  .word 443789887
  .word 3098225656
  .word 1457694129
  .word 4112129898
  .word 2471598371
  .word 831066844
  .word 3485502613
  .word 1844971086
  .word 204439559
  .word 2858875328
  .word 1218343801
  .word 3872779570
  .word 2232248043
  .word 591716516
  .word 3246152285
  .word 1605620758
  .word 4260056527
  .word 2619525000
  .word 978993473
  .word 3633429242
  .word 1992897715
  .word 352366188
  .word 3006801957
  .word 1366270430
  .word 4020706199
.section .bss
.balign 4
snapshot: .space 32
