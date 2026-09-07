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
  li t6, 116
.Lloop0:
  add a2, a0, a1
  add a3, a0, a1
  add a4, a0, a1
  add a5, a0, a1
  add a6, a0, a1
  add a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  add a3, a0, a1
  add a4, a0, a1
  add a5, a0, a1
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 250
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a1, a2
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a2, a3
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a3, a4
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 216
.Lloop2:
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  divu a4, a0, a1
  divu a5, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 150
.Lloop3:
  bnez a0, .Lskip3_0
  mv a0, a1
.Lskip3_0:
  bnez a1, .Lskip3_1
  mv a1, a2
.Lskip3_1:
  bnez a2, .Lskip3_2
  mv a2, a3
.Lskip3_2:
  bnez a3, .Lskip3_3
  mv a3, a4
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 160000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 99
.Lloop4:
  add a0, a0, a1
  add a1, a0, a1
  add a2, a0, a1
  add a3, a0, a1
  add a4, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  add a0, a0, a1
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
  .word 2983740192
  .word 1343208665
  .word 3997644434
  .word 2357112907
  .word 716581380
  .word 3371017149
  .word 1730485622
  .word 89954095
  .word 2744389864
  .word 1103858337
  .word 3758294106
  .word 2117762579
  .word 477231052
  .word 3131666821
  .word 1491135294
  .word 4145571063
  .word 2505039536
  .word 864508009
  .word 3518943778
  .word 1878412251
  .word 237880724
  .word 2892316493
  .word 1251784966
  .word 3906220735
  .word 2265689208
  .word 625157681
  .word 3279593450
  .word 1639061923
  .word 4293497692
  .word 2652966165
  .word 1012434638
  .word 3666870407
  .word 2026338880
  .word 385807353
  .word 3040243122
  .word 1399711595
  .word 4054147364
  .word 2413615837
  .word 773084310
  .word 3427520079
  .word 1786988552
  .word 146457025
  .word 2800892794
  .word 1160361267
  .word 3814797036
  .word 2174265509
  .word 533733982
  .word 3188169751
  .word 1547638224
  .word 4202073993
  .word 2561542466
  .word 921010939
  .word 3575446708
  .word 1934915181
  .word 294383654
  .word 2948819423
  .word 1308287896
  .word 3962723665
  .word 2322192138
  .word 681660611
  .word 3336096380
  .word 1695564853
  .word 55033326
  .word 2709469095
.section .bss
.balign 4
snapshot: .space 32
