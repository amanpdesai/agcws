.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
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
  add a0, a0, a1
  xor a2, a2, a3
  sll a4, a4, a5
  divu a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  divu a1, a1, a2
  mul a3, a3, a4
  srl a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 60000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  bnez a0, .Lskip2_1
  mv a0, a1
.Lskip2_1:
  add a2, a2, a3
  xor a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a6, a6, a7
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  divu a0, a0, a1
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
  .word 100000002
  .word 2754435771
  .word 1113904244
  .word 3768340013
  .word 2127808486
  .word 487276959
  .word 3141712728
  .word 1501181201
  .word 4155616970
  .word 2515085443
  .word 874553916
  .word 3528989685
  .word 1888458158
  .word 247926631
  .word 2902362400
  .word 1261830873
  .word 3916266642
  .word 2275735115
  .word 635203588
  .word 3289639357
  .word 1649107830
  .word 8576303
  .word 2663012072
  .word 1022480545
  .word 3676916314
  .word 2036384787
  .word 395853260
  .word 3050289029
  .word 1409757502
  .word 4064193271
  .word 2423661744
  .word 783130217
  .word 3437565986
  .word 1797034459
  .word 156502932
  .word 2810938701
  .word 1170407174
  .word 3824842943
  .word 2184311416
  .word 543779889
  .word 3198215658
  .word 1557684131
  .word 4212119900
  .word 2571588373
  .word 931056846
  .word 3585492615
  .word 1944961088
  .word 304429561
  .word 2958865330
  .word 1318333803
  .word 3972769572
  .word 2332238045
  .word 691706518
  .word 3346142287
  .word 1705610760
  .word 65079233
  .word 2719515002
  .word 1078983475
  .word 3733419244
  .word 2092887717
  .word 452356190
  .word 3106791959
  .word 1466260432
  .word 4120696201
.section .bss
.balign 4
snapshot: .space 32
