.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 31
  li a2, 1
  li a3, 2068541046
  li a4, 31
  li a5, 4294967295
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 25700
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 236
.Lloop0:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 34403
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 244
.Lloop1:
  mul a4, a7, a3
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  sll a3, a1, a4
  add a7, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 118141
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  add a4, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 140781
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 1376
.Lloop3:
  mul a5, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 142106
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 11
.Lloop4:
  and a2, a1, a0
  or a6, a6, a0
  xor a6, a1, a1
  xor a2, a5, a0
  srl a5, a6, a0
  sll a2, a5, a1
  or a5, a1, a1
  srl a5, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 161329
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 352
.Lloop5:
  divu a7, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 172365
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 704
.Lloop6:
  xor a2, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 1992997464
  .word 352465937
  .word 3006901706
  .word 1366370179
  .word 4020805948
  .word 2380274421
  .word 739742894
  .word 3394178663
  .word 1753647136
  .word 113115609
  .word 2767551378
  .word 1127019851
  .word 3781455620
  .word 2140924093
  .word 500392566
  .word 3154828335
  .word 1514296808
  .word 4168732577
  .word 2528201050
  .word 887669523
  .word 3542105292
  .word 1901573765
  .word 261042238
  .word 2915478007
  .word 1274946480
  .word 3929382249
  .word 2288850722
  .word 648319195
  .word 3302754964
  .word 1662223437
  .word 21691910
  .word 2676127679
  .word 1035596152
  .word 3690031921
  .word 2049500394
  .word 408968867
  .word 3063404636
  .word 1422873109
  .word 4077308878
  .word 2436777351
  .word 796245824
  .word 3450681593
  .word 1810150066
  .word 169618539
  .word 2824054308
  .word 1183522781
  .word 3837958550
  .word 2197427023
  .word 556895496
  .word 3211331265
  .word 1570799738
  .word 4225235507
  .word 2584703980
  .word 944172453
  .word 3598608222
  .word 1958076695
  .word 317545168
  .word 2971980937
  .word 1331449410
  .word 3985885179
  .word 2345353652
  .word 704822125
  .word 3359257894
  .word 1718726367
.section .bss
.balign 4
snapshot: .space 32
