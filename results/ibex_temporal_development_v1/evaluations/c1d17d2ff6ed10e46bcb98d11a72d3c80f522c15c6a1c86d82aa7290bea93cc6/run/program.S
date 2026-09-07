.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 17
  li a3, 4294967295
  li a4, 1076035761
  li a5, 4294967295
  li a6, 1
  li a7, 4294967295
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
  add a5, a7, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a5, a4, a6
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a0, a6, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  srl a3, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  bnez a5, .Lskip2_0
  mv a3, a0
.Lskip2_0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  xor a4, a0, a3
  srl a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  bnez a4, .Lskip3_0
  mv a2, a5
.Lskip3_0:
  divu a7, a7, a7
  add a2, a3, a3
  xor a0, a3, a4
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
  .word 100000001
  .word 2754435770
  .word 1113904243
  .word 3768340012
  .word 2127808485
  .word 487276958
  .word 3141712727
  .word 1501181200
  .word 4155616969
  .word 2515085442
  .word 874553915
  .word 3528989684
  .word 1888458157
  .word 247926630
  .word 2902362399
  .word 1261830872
  .word 3916266641
  .word 2275735114
  .word 635203587
  .word 3289639356
  .word 1649107829
  .word 8576302
  .word 2663012071
  .word 1022480544
  .word 3676916313
  .word 2036384786
  .word 395853259
  .word 3050289028
  .word 1409757501
  .word 4064193270
  .word 2423661743
  .word 783130216
  .word 3437565985
  .word 1797034458
  .word 156502931
  .word 2810938700
  .word 1170407173
  .word 3824842942
  .word 2184311415
  .word 543779888
  .word 3198215657
  .word 1557684130
  .word 4212119899
  .word 2571588372
  .word 931056845
  .word 3585492614
  .word 1944961087
  .word 304429560
  .word 2958865329
  .word 1318333802
  .word 3972769571
  .word 2332238044
  .word 691706517
  .word 3346142286
  .word 1705610759
  .word 65079232
  .word 2719515001
  .word 1078983474
  .word 3733419243
  .word 2092887716
  .word 452356189
  .word 3106791958
  .word 1466260431
  .word 4120696200
.section .bss
.balign 4
snapshot: .space 32
