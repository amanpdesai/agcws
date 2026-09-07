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
  li t6, 256
.Lloop0:
  divu a0, a0, a1
  divu a2, a2, a3
  divu a4, a4, a5
  divu a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 512
.Lloop1:
  divu a0, a0, a0
  divu a0, a0, a0
  divu a0, a0, a0
  divu a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 150000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a0, a0, a1
  divu a2, a2, a3
  divu a4, a4, a5
  divu a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 20000
  .word 2654455769
  .word 1013924242
  .word 3668360011
  .word 2027828484
  .word 387296957
  .word 3041732726
  .word 1401201199
  .word 4055636968
  .word 2415105441
  .word 774573914
  .word 3429009683
  .word 1788478156
  .word 147946629
  .word 2802382398
  .word 1161850871
  .word 3816286640
  .word 2175755113
  .word 535223586
  .word 3189659355
  .word 1549127828
  .word 4203563597
  .word 2563032070
  .word 922500543
  .word 3576936312
  .word 1936404785
  .word 295873258
  .word 2950309027
  .word 1309777500
  .word 3964213269
  .word 2323681742
  .word 683150215
  .word 3337585984
  .word 1697054457
  .word 56522930
  .word 2710958699
  .word 1070427172
  .word 3724862941
  .word 2084331414
  .word 443799887
  .word 3098235656
  .word 1457704129
  .word 4112139898
  .word 2471608371
  .word 831076844
  .word 3485512613
  .word 1844981086
  .word 204449559
  .word 2858885328
  .word 1218353801
  .word 3872789570
  .word 2232258043
  .word 591726516
  .word 3246162285
  .word 1605630758
  .word 4260066527
  .word 2619535000
  .word 979003473
  .word 3633439242
  .word 1992907715
  .word 352376188
  .word 3006811957
  .word 1366280430
  .word 4020716199
.section .bss
.balign 4
snapshot: .space 32
