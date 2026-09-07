.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 123
  li a1, 234
  li a2, 345
  li a3, 456
  li a4, 567
  li a5, 678
  li a6, 789
  li a7, 890
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 10000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 256
.Lloop0:
  add a1, a0, a1
  sll a2, a1, a2
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 50000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 256
.Lloop1:
  xor a4, a3, a4
  and a5, a4, a5
  divu a3, a5, a1
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 100000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 256
.Lloop2:
  mul a7, a6, a7
  srl a0, a7, a1
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 150000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 256
.Lloop3:
  add a2, a1, a2
  srl a3, a2, a3
  bnez a3, .Lskip3_2
  mv a1, a1
.Lskip3_2:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
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
