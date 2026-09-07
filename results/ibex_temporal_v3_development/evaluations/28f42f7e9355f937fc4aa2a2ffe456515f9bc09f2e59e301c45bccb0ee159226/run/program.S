.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 465150302
  li a1, 31
  li a2, 1
  li a3, 4294967295
  li a4, 4294967295
  li a5, 4194767623
  li a6, 4294967295
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10687
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 33
.Lloop0:
  divu a4, a7, a1
  add a4, a0, a1
  and a6, a5, a0
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  mul a2, a1, a0
  and a5, a1, a0
  divu a7, a6, a0
  and a7, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40707
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 83
.Lloop1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 81267
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 584
.Lloop2:
  mul a5, a6, a0
  mul a3, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 97317
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 1
.Lloop3:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 118451
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 592
.Lloop4:
  sll a4, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 147140
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 300
.Lloop5:
  divu a3, a0, a1
  or a4, a2, a5
  and a4, a2, a7
  and a3, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 172450
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 50
.Lloop6:
  sll a1, a6, a6
  add a4, a4, a4
  sll a0, a0, a1
  and a6, a7, a3
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
  .word 1753712168
  .word 113180641
  .word 2767616410
  .word 1127084883
  .word 3781520652
  .word 2140989125
  .word 500457598
  .word 3154893367
  .word 1514361840
  .word 4168797609
  .word 2528266082
  .word 887734555
  .word 3542170324
  .word 1901638797
  .word 261107270
  .word 2915543039
  .word 1275011512
  .word 3929447281
  .word 2288915754
  .word 648384227
  .word 3302819996
  .word 1662288469
  .word 21756942
  .word 2676192711
  .word 1035661184
  .word 3690096953
  .word 2049565426
  .word 409033899
  .word 3063469668
  .word 1422938141
  .word 4077373910
  .word 2436842383
  .word 796310856
  .word 3450746625
  .word 1810215098
  .word 169683571
  .word 2824119340
  .word 1183587813
  .word 3838023582
  .word 2197492055
  .word 556960528
  .word 3211396297
  .word 1570864770
  .word 4225300539
  .word 2584769012
  .word 944237485
  .word 3598673254
  .word 1958141727
  .word 317610200
  .word 2972045969
  .word 1331514442
  .word 3985950211
  .word 2345418684
  .word 704887157
  .word 3359322926
  .word 1718791399
  .word 78259872
  .word 2732695641
  .word 1092164114
  .word 3746599883
  .word 2106068356
  .word 465536829
  .word 3119972598
  .word 1479441071
.section .bss
.balign 4
snapshot: .space 32
