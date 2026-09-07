.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
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
  divu a0, a0, a1
  divu a1, a1, a2
  divu a2, a2, a3
  divu a3, a3, a4
  divu a4, a4, a5
  divu a5, a5, a6
  divu a6, a6, a7
  divu a7, a7, a0
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
  .word 2468013579
  .word 827482052
  .word 3481917821
  .word 1841386294
  .word 200854767
  .word 2855290536
  .word 1214759009
  .word 3869194778
  .word 2228663251
  .word 588131724
  .word 3242567493
  .word 1602035966
  .word 4256471735
  .word 2615940208
  .word 975408681
  .word 3629844450
  .word 1989312923
  .word 348781396
  .word 3003217165
  .word 1362685638
  .word 4017121407
  .word 2376589880
  .word 736058353
  .word 3390494122
  .word 1749962595
  .word 109431068
  .word 2763866837
  .word 1123335310
  .word 3777771079
  .word 2137239552
  .word 496708025
  .word 3151143794
  .word 1510612267
  .word 4165048036
  .word 2524516509
  .word 883984982
  .word 3538420751
  .word 1897889224
  .word 257357697
  .word 2911793466
  .word 1271261939
  .word 3925697708
  .word 2285166181
  .word 644634654
  .word 3299070423
  .word 1658538896
  .word 18007369
  .word 2672443138
  .word 1031911611
  .word 3686347380
  .word 2045815853
  .word 405284326
  .word 3059720095
  .word 1419188568
  .word 4073624337
  .word 2433092810
  .word 792561283
  .word 3446997052
  .word 1806465525
  .word 165933998
  .word 2820369767
  .word 1179838240
  .word 3834274009
  .word 2193742482
.section .bss
.balign 4
snapshot: .space 32
