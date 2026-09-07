.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 0
  li a2, 31
  li a3, 0
  li a4, 2477256246
  li a5, 4294967295
  li a6, 17
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 10480
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 81
.Lloop0:
  mul a7, a2, a3
  mul a4, a0, a4
  mul a6, a7, a7
  mul a1, a4, a4
  mul a1, a7, a1
  mul a2, a5, a0
  mul a2, a0, a7
  mul a1, a5, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 13092
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 8
.Lloop1:
  bnez a7, .Lskip1_0
  mv a3, a5
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a0, a6
.Lskip1_1:
  bnez a0, .Lskip1_2
  mv a5, a2
.Lskip1_2:
  bnez a1, .Lskip1_3
  mv a1, a2
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 61347
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 31
.Lloop2:
  and a2, a6, a1
  sll a2, a0, a0
  add a4, a0, a0
  or a6, a2, a0
  and a4, a0, a0
  srl a2, a2, a1
  sll a6, a5, a1
  or a6, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 86865
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 430
.Lloop3:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 120968
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 552
.Lloop4:
  divu a5, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 156390
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 248
.Lloop5:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 158366
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 100
.Lloop6:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
  .word 929524398
  .word 3583960167
  .word 1943428640
  .word 302897113
  .word 2957332882
  .word 1316801355
  .word 3971237124
  .word 2330705597
  .word 690174070
  .word 3344609839
  .word 1704078312
  .word 63546785
  .word 2717982554
  .word 1077451027
  .word 3731886796
  .word 2091355269
  .word 450823742
  .word 3105259511
  .word 1464727984
  .word 4119163753
  .word 2478632226
  .word 838100699
  .word 3492536468
  .word 1852004941
  .word 211473414
  .word 2865909183
  .word 1225377656
  .word 3879813425
  .word 2239281898
  .word 598750371
  .word 3253186140
  .word 1612654613
  .word 4267090382
  .word 2626558855
  .word 986027328
  .word 3640463097
  .word 1999931570
  .word 359400043
  .word 3013835812
  .word 1373304285
  .word 4027740054
  .word 2387208527
  .word 746677000
  .word 3401112769
  .word 1760581242
  .word 120049715
  .word 2774485484
  .word 1133953957
  .word 3788389726
  .word 2147858199
  .word 507326672
  .word 3161762441
  .word 1521230914
  .word 4175666683
  .word 2535135156
  .word 894603629
  .word 3549039398
  .word 1908507871
  .word 267976344
  .word 2922412113
  .word 1281880586
  .word 3936316355
  .word 2295784828
  .word 655253301
.section .bss
.balign 4
snapshot: .space 32
