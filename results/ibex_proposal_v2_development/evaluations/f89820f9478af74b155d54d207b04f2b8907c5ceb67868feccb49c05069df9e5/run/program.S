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
  li t6, 250
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  mul a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 249
.Lloop1:
  divu a2, a0, a1
  srl a4, a2, a3
  and a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 262
.Lloop2:
  or a5, a7, a6
  add a3, a5, a4
  mul a1, a3, a2
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  or a5, a7, a6
  add a3, a5, a4
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 262
.Lloop3:
  bnez a0, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  xor a4, a2, a3
  sll a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  bnez a0, .Ltail_skip3_0
  mv a2, a1
.Ltail_skip3_0:
  xor a4, a2, a3
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
  .word 1122334457
  .word 3776770226
  .word 2136238699
  .word 495707172
  .word 3150142941
  .word 1509611414
  .word 4164047183
  .word 2523515656
  .word 882984129
  .word 3537419898
  .word 1896888371
  .word 256356844
  .word 2910792613
  .word 1270261086
  .word 3924696855
  .word 2284165328
  .word 643633801
  .word 3298069570
  .word 1657538043
  .word 17006516
  .word 2671442285
  .word 1030910758
  .word 3685346527
  .word 2044815000
  .word 404283473
  .word 3058719242
  .word 1418187715
  .word 4072623484
  .word 2432091957
  .word 791560430
  .word 3445996199
  .word 1805464672
  .word 164933145
  .word 2819368914
  .word 1178837387
  .word 3833273156
  .word 2192741629
  .word 552210102
  .word 3206645871
  .word 1566114344
  .word 4220550113
  .word 2580018586
  .word 939487059
  .word 3593922828
  .word 1953391301
  .word 312859774
  .word 2967295543
  .word 1326764016
  .word 3981199785
  .word 2340668258
  .word 700136731
  .word 3354572500
  .word 1714040973
  .word 73509446
  .word 2727945215
  .word 1087413688
  .word 3741849457
  .word 2101317930
  .word 460786403
  .word 3115222172
  .word 1474690645
  .word 4129126414
  .word 2488594887
  .word 848063360
.section .bss
.balign 4
snapshot: .space 32
