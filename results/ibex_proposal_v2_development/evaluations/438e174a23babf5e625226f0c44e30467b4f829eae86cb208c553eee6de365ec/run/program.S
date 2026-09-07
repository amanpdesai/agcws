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
  li t6, 256
.Lloop0:
  mul a2, a0, a1
  divu a4, a2, a3
  add a6, a4, a5
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
  li t6, 256
.Lloop1:
  xor a2, a0, a1
  sll a4, a2, a3
  srl a6, a4, a5
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
  li t6, 256
.Lloop2:
  and a5, a7, a6
  or a3, a5, a4
  bnez a3, .Lskip2_2
  mv a1, a2
.Lskip2_2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  mul a2, a0, a1
  divu a4, a2, a3
  add a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
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
  .word 3141592653
  .word 1501061126
  .word 4155496895
  .word 2514965368
  .word 874433841
  .word 3528869610
  .word 1888338083
  .word 247806556
  .word 2902242325
  .word 1261710798
  .word 3916146567
  .word 2275615040
  .word 635083513
  .word 3289519282
  .word 1648987755
  .word 8456228
  .word 2662891997
  .word 1022360470
  .word 3676796239
  .word 2036264712
  .word 395733185
  .word 3050168954
  .word 1409637427
  .word 4064073196
  .word 2423541669
  .word 783010142
  .word 3437445911
  .word 1796914384
  .word 156382857
  .word 2810818626
  .word 1170287099
  .word 3824722868
  .word 2184191341
  .word 543659814
  .word 3198095583
  .word 1557564056
  .word 4211999825
  .word 2571468298
  .word 930936771
  .word 3585372540
  .word 1944841013
  .word 304309486
  .word 2958745255
  .word 1318213728
  .word 3972649497
  .word 2332117970
  .word 691586443
  .word 3346022212
  .word 1705490685
  .word 64959158
  .word 2719394927
  .word 1078863400
  .word 3733299169
  .word 2092767642
  .word 452236115
  .word 3106671884
  .word 1466140357
  .word 4120576126
  .word 2480044599
  .word 839513072
  .word 3493948841
  .word 1853417314
  .word 212885787
  .word 2867321556
.section .bss
.balign 4
snapshot: .space 32
