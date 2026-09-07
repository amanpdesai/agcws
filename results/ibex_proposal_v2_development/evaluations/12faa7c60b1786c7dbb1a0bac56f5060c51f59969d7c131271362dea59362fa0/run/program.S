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
  li t6, 150
.Lloop0:
  mul a0, a0, a1
  mul a1, a1, a2
  mul a2, a2, a3
  divu a3, a3, a4
  divu a4, a4, a5
  divu a5, a5, a6
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
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 112
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
  bnez a3, .Lskip1_3
  mv a3, a4
.Lskip1_3:
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
  bnez a3, .Ltail_skip1_3
  mv a3, a4
.Ltail_skip1_3:
  li s9, 70000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 125
.Lloop2:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  srl a3, a3, a4
  mul a4, a4, a5
  divu a5, a5, a6
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
  li s9, 130000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 124
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
  sll a2, a2, a3
  srl a3, a3, a4
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
  .word 738905629
  .word 3393341398
  .word 1752809871
  .word 112278344
  .word 2766714113
  .word 1126182586
  .word 3780618355
  .word 2140086828
  .word 499555301
  .word 3153991070
  .word 1513459543
  .word 4167895312
  .word 2527363785
  .word 886832258
  .word 3541268027
  .word 1900736500
  .word 260204973
  .word 2914640742
  .word 1274109215
  .word 3928544984
  .word 2288013457
  .word 647481930
  .word 3301917699
  .word 1661386172
  .word 20854645
  .word 2675290414
  .word 1034758887
  .word 3689194656
  .word 2048663129
  .word 408131602
  .word 3062567371
  .word 1422035844
  .word 4076471613
  .word 2435940086
  .word 795408559
  .word 3449844328
  .word 1809312801
  .word 168781274
  .word 2823217043
  .word 1182685516
  .word 3837121285
  .word 2196589758
  .word 556058231
  .word 3210494000
  .word 1569962473
  .word 4224398242
  .word 2583866715
  .word 943335188
  .word 3597770957
  .word 1957239430
  .word 316707903
  .word 2971143672
  .word 1330612145
  .word 3985047914
  .word 2344516387
  .word 703984860
  .word 3358420629
  .word 1717889102
  .word 77357575
  .word 2731793344
  .word 1091261817
  .word 3745697586
  .word 2105166059
  .word 464634532
.section .bss
.balign 4
snapshot: .space 32
