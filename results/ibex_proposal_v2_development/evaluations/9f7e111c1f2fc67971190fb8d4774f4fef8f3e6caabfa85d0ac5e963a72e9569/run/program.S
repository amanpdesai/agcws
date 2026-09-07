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
  divu a2, a0, a1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  add a5, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a0, a5, a1
  mul a6, a0, a2
  xor a7, a3, a4
  sll a1, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a2, a1, a0
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  srl a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a5, a3, a1
  add a7, a5, a0
  mul a0, a7, a2
  bnez a0, .Lskip3_3
  mv a1, a4
.Lskip3_3:
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
  .word 99887766
  .word 2754323535
  .word 1113792008
  .word 3768227777
  .word 2127696250
  .word 487164723
  .word 3141600492
  .word 1501068965
  .word 4155504734
  .word 2514973207
  .word 874441680
  .word 3528877449
  .word 1888345922
  .word 247814395
  .word 2902250164
  .word 1261718637
  .word 3916154406
  .word 2275622879
  .word 635091352
  .word 3289527121
  .word 1648995594
  .word 8464067
  .word 2662899836
  .word 1022368309
  .word 3676804078
  .word 2036272551
  .word 395741024
  .word 3050176793
  .word 1409645266
  .word 4064081035
  .word 2423549508
  .word 783017981
  .word 3437453750
  .word 1796922223
  .word 156390696
  .word 2810826465
  .word 1170294938
  .word 3824730707
  .word 2184199180
  .word 543667653
  .word 3198103422
  .word 1557571895
  .word 4212007664
  .word 2571476137
  .word 930944610
  .word 3585380379
  .word 1944848852
  .word 304317325
  .word 2958753094
  .word 1318221567
  .word 3972657336
  .word 2332125809
  .word 691594282
  .word 3346030051
  .word 1705498524
  .word 64966997
  .word 2719402766
  .word 1078871239
  .word 3733307008
  .word 2092775481
  .word 452243954
  .word 3106679723
  .word 1466148196
  .word 4120583965
.section .bss
.balign 4
snapshot: .space 32
