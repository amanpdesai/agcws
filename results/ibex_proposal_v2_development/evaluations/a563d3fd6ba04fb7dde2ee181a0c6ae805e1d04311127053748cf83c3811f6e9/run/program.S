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
  li t6, 204
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  mul a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  xor a4, a2, a3
  sll a6, a4, a5
  srl a0, a6, a7
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 204
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  add a5, a3, a4
  xor a7, a5, a6
  sll a1, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  add a5, a3, a4
  xor a7, a5, a6
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  mul a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 204
.Lloop3:
  bnez a0, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  add a4, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  mul a1, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  bnez a0, .Ltail_skip3_0
  mv a2, a1
.Ltail_skip3_0:
  add a4, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
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
  .word 20002
  .word 2654455771
  .word 1013924244
  .word 3668360013
  .word 2027828486
  .word 387296959
  .word 3041732728
  .word 1401201201
  .word 4055636970
  .word 2415105443
  .word 774573916
  .word 3429009685
  .word 1788478158
  .word 147946631
  .word 2802382400
  .word 1161850873
  .word 3816286642
  .word 2175755115
  .word 535223588
  .word 3189659357
  .word 1549127830
  .word 4203563599
  .word 2563032072
  .word 922500545
  .word 3576936314
  .word 1936404787
  .word 295873260
  .word 2950309029
  .word 1309777502
  .word 3964213271
  .word 2323681744
  .word 683150217
  .word 3337585986
  .word 1697054459
  .word 56522932
  .word 2710958701
  .word 1070427174
  .word 3724862943
  .word 2084331416
  .word 443799889
  .word 3098235658
  .word 1457704131
  .word 4112139900
  .word 2471608373
  .word 831076846
  .word 3485512615
  .word 1844981088
  .word 204449561
  .word 2858885330
  .word 1218353803
  .word 3872789572
  .word 2232258045
  .word 591726518
  .word 3246162287
  .word 1605630760
  .word 4260066529
  .word 2619535002
  .word 979003475
  .word 3633439244
  .word 1992907717
  .word 352376190
  .word 3006811959
  .word 1366280432
  .word 4020716201
.section .bss
.balign 4
snapshot: .space 32
