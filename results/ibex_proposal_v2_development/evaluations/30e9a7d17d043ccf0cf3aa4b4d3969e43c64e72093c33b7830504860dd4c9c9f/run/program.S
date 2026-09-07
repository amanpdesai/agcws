.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 17
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 543449912
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 48747
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 132
.Lloop0:
  bnez a5, .Lskip0_0
  mv a7, a4
.Lskip0_0:
  or a3, a6, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 52320
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 208
.Lloop1:
  divu a4, a3, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 54141
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 406
.Lloop2:
  and a5, a4, a5
  xor a2, a0, a0
  xor a2, a1, a4
  sll a0, a4, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 80450
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 8
.Lloop3:
  divu a4, a6, a1
  divu a6, a5, a0
  divu a2, a6, a0
  divu a7, a3, a1
  divu a5, a3, a0
  divu a2, a5, a0
  divu a2, a6, a1
  divu a7, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 107590
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 4
.Lloop4:
  divu a3, a0, a1
  divu a5, a1, a1
  divu a7, a0, a1
  divu a5, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 129936
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 162
.Lloop5:
  bnez a5, .Lskip5_0
  mv a6, a1
.Lskip5_0:
  bnez a0, .Lskip5_1
  mv a7, a0
.Lskip5_1:
  bnez a5, .Lskip5_2
  mv a6, a0
.Lskip5_2:
  bnez a5, .Lskip5_3
  mv a6, a1
.Lskip5_3:
  bnez a4, .Lskip5_4
  mv a5, a1
.Lskip5_4:
  bnez a4, .Lskip5_5
  mv a4, a1
.Lskip5_5:
  bnez a1, .Lskip5_6
  mv a3, a1
.Lskip5_6:
  bnez a7, .Lskip5_7
  mv a7, a0
.Lskip5_7:
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 143767
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 608
.Lloop6:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 159195
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 8
.Lloop7:
  add a3, a7, a1
  or a2, a0, a1
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
  .word 880803539
  .word 3535239308
  .word 1894707781
  .word 254176254
  .word 2908612023
  .word 1268080496
  .word 3922516265
  .word 2281984738
  .word 641453211
  .word 3295888980
  .word 1655357453
  .word 14825926
  .word 2669261695
  .word 1028730168
  .word 3683165937
  .word 2042634410
  .word 402102883
  .word 3056538652
  .word 1416007125
  .word 4070442894
  .word 2429911367
  .word 789379840
  .word 3443815609
  .word 1803284082
  .word 162752555
  .word 2817188324
  .word 1176656797
  .word 3831092566
  .word 2190561039
  .word 550029512
  .word 3204465281
  .word 1563933754
  .word 4218369523
  .word 2577837996
  .word 937306469
  .word 3591742238
  .word 1951210711
  .word 310679184
  .word 2965114953
  .word 1324583426
  .word 3979019195
  .word 2338487668
  .word 697956141
  .word 3352391910
  .word 1711860383
  .word 71328856
  .word 2725764625
  .word 1085233098
  .word 3739668867
  .word 2099137340
  .word 458605813
  .word 3113041582
  .word 1472510055
  .word 4126945824
  .word 2486414297
  .word 845882770
  .word 3500318539
  .word 1859787012
  .word 219255485
  .word 2873691254
  .word 1233159727
  .word 3887595496
  .word 2247063969
  .word 606532442
.section .bss
.balign 4
snapshot: .space 32
