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
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 170
.Lloop0:
  divu a0, a1, a0
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a3, a4, a0
  bnez a5, .Lskip0_3
  mv a4, a0
.Lskip0_3:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  mul a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a0, a1, a0
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  add a3, a4, a0
  bnez a5, .Ltail_skip0_3
  mv a4, a0
.Ltail_skip0_3:
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 204
.Lloop1:
  xor a0, a0, a1
  divu a1, a1, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  sll a4, a4, a5
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  xor a0, a0, a1
  divu a1, a1, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  sll a4, a4, a5
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 170
.Lloop2:
  bnez a0, .Lskip2_0
  mv a0, a1
.Lskip2_0:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  divu a3, a3, a4
  or a4, a4, a5
  and a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  bnez a0, .Ltail_skip2_0
  mv a0, a1
.Ltail_skip2_0:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  divu a3, a3, a4
  or a4, a4, a5
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 204
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  srl a1, a1, a2
  divu a3, a4, a0
  bnez a5, .Lskip3_3
  mv a4, a0
.Lskip3_3:
  add a5, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  srl a1, a1, a2
  divu a3, a4, a0
  bnez a5, .Ltail_skip3_3
  mv a4, a0
.Ltail_skip3_3:
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
  .word 3341289841
  .word 1700758314
  .word 60226787
  .word 2714662556
  .word 1074131029
  .word 3728566798
  .word 2088035271
  .word 447503744
  .word 3101939513
  .word 1461407986
  .word 4115843755
  .word 2475312228
  .word 834780701
  .word 3489216470
  .word 1848684943
  .word 208153416
  .word 2862589185
  .word 1222057658
  .word 3876493427
  .word 2235961900
  .word 595430373
  .word 3249866142
  .word 1609334615
  .word 4263770384
  .word 2623238857
  .word 982707330
  .word 3637143099
  .word 1996611572
  .word 356080045
  .word 3010515814
  .word 1369984287
  .word 4024420056
  .word 2383888529
  .word 743357002
  .word 3397792771
  .word 1757261244
  .word 116729717
  .word 2771165486
  .word 1130633959
  .word 3785069728
  .word 2144538201
  .word 504006674
  .word 3158442443
  .word 1517910916
  .word 4172346685
  .word 2531815158
  .word 891283631
  .word 3545719400
  .word 1905187873
  .word 264656346
  .word 2919092115
  .word 1278560588
  .word 3932996357
  .word 2292464830
  .word 651933303
  .word 3306369072
  .word 1665837545
  .word 25306018
  .word 2679741787
  .word 1039210260
  .word 3693646029
  .word 2053114502
  .word 412582975
  .word 3067018744
.section .bss
.balign 4
snapshot: .space 32
