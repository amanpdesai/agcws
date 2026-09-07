.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 31
  li a3, 31
  li a4, 1
  li a5, 1
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 29237
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 172
.Lloop0:
  bnez a3, .Lskip0_0
  mv a0, a0
.Lskip0_0:
  bnez a2, .Lskip0_1
  mv a6, a5
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 85905
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 184
.Lloop1:
  divu a6, a1, a6
  divu a2, a7, a0
  divu a0, a2, a5
  divu a6, a5, a4
  divu a0, a2, a4
  divu a2, a1, a7
  divu a0, a4, a6
  divu a0, a7, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 93601
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 688
.Lloop2:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 145728
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 608
.Lloop3:
  add a7, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 147573
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 240
.Lloop4:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 159467
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 24
.Lloop5:
  divu a5, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 4260381960
  .word 2619850433
  .word 979318906
  .word 3633754675
  .word 1993223148
  .word 352691621
  .word 3007127390
  .word 1366595863
  .word 4021031632
  .word 2380500105
  .word 739968578
  .word 3394404347
  .word 1753872820
  .word 113341293
  .word 2767777062
  .word 1127245535
  .word 3781681304
  .word 2141149777
  .word 500618250
  .word 3155054019
  .word 1514522492
  .word 4168958261
  .word 2528426734
  .word 887895207
  .word 3542330976
  .word 1901799449
  .word 261267922
  .word 2915703691
  .word 1275172164
  .word 3929607933
  .word 2289076406
  .word 648544879
  .word 3302980648
  .word 1662449121
  .word 21917594
  .word 2676353363
  .word 1035821836
  .word 3690257605
  .word 2049726078
  .word 409194551
  .word 3063630320
  .word 1423098793
  .word 4077534562
  .word 2437003035
  .word 796471508
  .word 3450907277
  .word 1810375750
  .word 169844223
  .word 2824279992
  .word 1183748465
  .word 3838184234
  .word 2197652707
  .word 557121180
  .word 3211556949
  .word 1571025422
  .word 4225461191
  .word 2584929664
  .word 944398137
  .word 3598833906
  .word 1958302379
  .word 317770852
  .word 2972206621
  .word 1331675094
  .word 3986110863
.section .bss
.balign 4
snapshot: .space 32
