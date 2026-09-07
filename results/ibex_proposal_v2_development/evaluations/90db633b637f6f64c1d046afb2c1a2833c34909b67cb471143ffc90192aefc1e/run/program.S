.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 4032293290
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 3024829961
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 175
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  mul a1, a0, a2
  or a2, a1, a5
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  bnez a6, .Lskip0_4
  mv a3, a1
.Lskip0_4:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 237
.Lloop1:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  mul a5, a6, a4
  and a6, a2, a5
  xor a7, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  mul a5, a6, a4
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 230
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  bnez a7, .Lskip2_2
  mv a0, a0
.Lskip2_2:
  add a2, a5, a0
  sll a3, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 236
.Lloop3:
  or a1, a0, a2
  mul a3, a4, a1
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  srl a7, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop3
  or a1, a0, a2
  mul a3, a4, a1
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
  .word 3341289843
  .word 1700758316
  .word 60226789
  .word 2714662558
  .word 1074131031
  .word 3728566800
  .word 2088035273
  .word 447503746
  .word 3101939515
  .word 1461407988
  .word 4115843757
  .word 2475312230
  .word 834780703
  .word 3489216472
  .word 1848684945
  .word 208153418
  .word 2862589187
  .word 1222057660
  .word 3876493429
  .word 2235961902
  .word 595430375
  .word 3249866144
  .word 1609334617
  .word 4263770386
  .word 2623238859
  .word 982707332
  .word 3637143101
  .word 1996611574
  .word 356080047
  .word 3010515816
  .word 1369984289
  .word 4024420058
  .word 2383888531
  .word 743357004
  .word 3397792773
  .word 1757261246
  .word 116729719
  .word 2771165488
  .word 1130633961
  .word 3785069730
  .word 2144538203
  .word 504006676
  .word 3158442445
  .word 1517910918
  .word 4172346687
  .word 2531815160
  .word 891283633
  .word 3545719402
  .word 1905187875
  .word 264656348
  .word 2919092117
  .word 1278560590
  .word 3932996359
  .word 2292464832
  .word 651933305
  .word 3306369074
  .word 1665837547
  .word 25306020
  .word 2679741789
  .word 1039210262
  .word 3693646031
  .word 2053114504
  .word 412582977
  .word 3067018746
.section .bss
.balign 4
snapshot: .space 32
