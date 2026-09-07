.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 137
.Lloop0:
  mul a0, a0, a1
  mul a1, a1, a2
  divu a2, a2, a3
  divu a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  mul a0, a0, a1
  mul a1, a1, a2
  divu a2, a2, a3
  divu a3, a3, a4
  li s9, 15000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 118
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
  add a3, a3, a4
  xor a4, a4, a5
  sll a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a0, .Ltail_skip1_0
  mv a0, a1
.Ltail_skip1_0:
  bnez a1, .Ltail_skip1_1
  mv a1, a2
.Ltail_skip1_1:
  bnez a2, .Ltail_skip1_2
  mv a2, a3
.Ltail_skip1_2:
  add a3, a3, a4
  xor a4, a4, a5
  sll a5, a5, a6
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 112
.Lloop2:
  mul a0, a0, a1
  mul a1, a1, a2
  mul a2, a2, a3
  add a3, a3, a4
  xor a4, a4, a5
  sll a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  mul a0, a0, a1
  mul a1, a1, a2
  mul a2, a2, a3
  add a3, a3, a4
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 143
.Lloop3:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  xor a1, a1, a2
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
  .word 1011121314
  .word 3665557083
  .word 2025025556
  .word 384494029
  .word 3038929798
  .word 1398398271
  .word 4052834040
  .word 2412302513
  .word 771770986
  .word 3426206755
  .word 1785675228
  .word 145143701
  .word 2799579470
  .word 1159047943
  .word 3813483712
  .word 2172952185
  .word 532420658
  .word 3186856427
  .word 1546324900
  .word 4200760669
  .word 2560229142
  .word 919697615
  .word 3574133384
  .word 1933601857
  .word 293070330
  .word 2947506099
  .word 1306974572
  .word 3961410341
  .word 2320878814
  .word 680347287
  .word 3334783056
  .word 1694251529
  .word 53720002
  .word 2708155771
  .word 1067624244
  .word 3722060013
  .word 2081528486
  .word 440996959
  .word 3095432728
  .word 1454901201
  .word 4109336970
  .word 2468805443
  .word 828273916
  .word 3482709685
  .word 1842178158
  .word 201646631
  .word 2856082400
  .word 1215550873
  .word 3869986642
  .word 2229455115
  .word 588923588
  .word 3243359357
  .word 1602827830
  .word 4257263599
  .word 2616732072
  .word 976200545
  .word 3630636314
  .word 1990104787
  .word 349573260
  .word 3004009029
  .word 1363477502
  .word 4017913271
  .word 2377381744
  .word 736850217
.section .bss
.balign 4
snapshot: .space 32
