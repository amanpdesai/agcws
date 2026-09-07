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
  li t6, 256
.Lloop0:
  bnez a0, .Lskip0_0
  mv a0, a1
.Lskip0_0:
  add a1, a1, a2
  bnez a2, .Lskip0_2
  mv a2, a3
.Lskip0_2:
  add a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a4, a4, a5
  divu a5, a5, a6
  divu a6, a6, a7
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
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
  .word 98765432
  .word 2753201201
  .word 1112669674
  .word 3767105443
  .word 2126573916
  .word 486042389
  .word 3140478158
  .word 1499946631
  .word 4154382400
  .word 2513850873
  .word 873319346
  .word 3527755115
  .word 1887223588
  .word 246692061
  .word 2901127830
  .word 1260596303
  .word 3915032072
  .word 2274500545
  .word 633969018
  .word 3288404787
  .word 1647873260
  .word 7341733
  .word 2661777502
  .word 1021245975
  .word 3675681744
  .word 2035150217
  .word 394618690
  .word 3049054459
  .word 1408522932
  .word 4062958701
  .word 2422427174
  .word 781895647
  .word 3436331416
  .word 1795799889
  .word 155268362
  .word 2809704131
  .word 1169172604
  .word 3823608373
  .word 2183076846
  .word 542545319
  .word 3196981088
  .word 1556449561
  .word 4210885330
  .word 2570353803
  .word 929822276
  .word 3584258045
  .word 1943726518
  .word 303194991
  .word 2957630760
  .word 1317099233
  .word 3971535002
  .word 2331003475
  .word 690471948
  .word 3344907717
  .word 1704376190
  .word 63844663
  .word 2718280432
  .word 1077748905
  .word 3732184674
  .word 2091653147
  .word 451121620
  .word 3105557389
  .word 1465025862
  .word 4119461631
.section .bss
.balign 4
snapshot: .space 32
