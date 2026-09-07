.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 668217370
  li a6, 17
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 44941
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 376
.Lloop0:
  or a6, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 51446
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 156
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  bnez a0, .Lskip1_1
  mv a2, a3
.Lskip1_1:
  divu a4, a0, a2
  add a3, a7, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 88845
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 428
.Lloop2:
  mul a2, a0, a5
  mul a7, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 109950
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 120
.Lloop3:
  bnez a2, .Lskip3_0
  mv a4, a1
.Lskip3_0:
  bnez a6, .Lskip3_1
  mv a6, a0
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 127409
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 504
.Lloop4:
  or a4, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 139915
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 130
.Lloop5:
  mul a6, a6, a1
  mul a7, a1, a1
  mul a2, a4, a0
  mul a2, a7, a0
  mul a6, a1, a1
  mul a5, a5, a0
  mul a3, a0, a0
  mul a6, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 147393
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 80
.Lloop6:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 148387
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 94
.Lloop7:
  mul a6, a2, a0
  xor a5, a4, a0
  divu a6, a5, a0
  or a4, a0, a1
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
  .word 3790665855
  .word 2150134328
  .word 509602801
  .word 3164038570
  .word 1523507043
  .word 4177942812
  .word 2537411285
  .word 896879758
  .word 3551315527
  .word 1910784000
  .word 270252473
  .word 2924688242
  .word 1284156715
  .word 3938592484
  .word 2298060957
  .word 657529430
  .word 3311965199
  .word 1671433672
  .word 30902145
  .word 2685337914
  .word 1044806387
  .word 3699242156
  .word 2058710629
  .word 418179102
  .word 3072614871
  .word 1432083344
  .word 4086519113
  .word 2445987586
  .word 805456059
  .word 3459891828
  .word 1819360301
  .word 178828774
  .word 2833264543
  .word 1192733016
  .word 3847168785
  .word 2206637258
  .word 566105731
  .word 3220541500
  .word 1580009973
  .word 4234445742
  .word 2593914215
  .word 953382688
  .word 3607818457
  .word 1967286930
  .word 326755403
  .word 2981191172
  .word 1340659645
  .word 3995095414
  .word 2354563887
  .word 714032360
  .word 3368468129
  .word 1727936602
  .word 87405075
  .word 2741840844
  .word 1101309317
  .word 3755745086
  .word 2115213559
  .word 474682032
  .word 3129117801
  .word 1488586274
  .word 4143022043
  .word 2502490516
  .word 861958989
  .word 3516394758
.section .bss
.balign 4
snapshot: .space 32
