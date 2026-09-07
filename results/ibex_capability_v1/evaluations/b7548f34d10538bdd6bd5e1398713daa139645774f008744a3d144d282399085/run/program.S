.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1511584066
  li a2, 0
  li a3, 1
  li a4, 4294967295
  li a5, 17
  li a6, 1287493331
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 46135
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 22
.Lloop0:
  mul a7, a6, a0
  mul a0, a0, a2
  mul a7, a0, a6
  mul a4, a0, a6
  mul a4, a2, a4
  mul a5, a7, a1
  mul a2, a6, a7
  mul a7, a2, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 59527
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 356
.Lloop1:
  mul a5, a3, a0
  mul a2, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 68220
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 3
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 134291
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 80
.Lloop3:
  mul a5, a6, a1
  mul a4, a5, a0
  mul a5, a0, a1
  mul a5, a0, a0
  mul a3, a3, a0
  mul a4, a5, a0
  mul a7, a4, a0
  mul a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 134534
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 318
.Lloop4:
  and a3, a5, a0
  and a5, a7, a0
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  bnez a6, .Lskip4_3
  mv a7, a1
.Lskip4_3:
  sll a2, a3, a0
  xor a2, a7, a0
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  divu a7, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 1792866724
  .word 152335197
  .word 2806770966
  .word 1166239439
  .word 3820675208
  .word 2180143681
  .word 539612154
  .word 3194047923
  .word 1553516396
  .word 4207952165
  .word 2567420638
  .word 926889111
  .word 3581324880
  .word 1940793353
  .word 300261826
  .word 2954697595
  .word 1314166068
  .word 3968601837
  .word 2328070310
  .word 687538783
  .word 3341974552
  .word 1701443025
  .word 60911498
  .word 2715347267
  .word 1074815740
  .word 3729251509
  .word 2088719982
  .word 448188455
  .word 3102624224
  .word 1462092697
  .word 4116528466
  .word 2475996939
  .word 835465412
  .word 3489901181
  .word 1849369654
  .word 208838127
  .word 2863273896
  .word 1222742369
  .word 3877178138
  .word 2236646611
  .word 596115084
  .word 3250550853
  .word 1610019326
  .word 4264455095
  .word 2623923568
  .word 983392041
  .word 3637827810
  .word 1997296283
  .word 356764756
  .word 3011200525
  .word 1370668998
  .word 4025104767
  .word 2384573240
  .word 744041713
  .word 3398477482
  .word 1757945955
  .word 117414428
  .word 2771850197
  .word 1131318670
  .word 3785754439
  .word 2145222912
  .word 504691385
  .word 3159127154
  .word 1518595627
.section .bss
.balign 4
snapshot: .space 32
