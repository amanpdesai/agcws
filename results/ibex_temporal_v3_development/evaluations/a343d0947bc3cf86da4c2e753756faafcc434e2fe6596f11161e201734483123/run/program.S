.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 187
.Lloop0:
  mul a0, a0, a1
  sll a1, a1, a2
  add a2, a2, a3
  xor a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  mul a0, a0, a1
  sll a1, a1, a2
  add a2, a2, a3
  xor a3, a3, a4
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 162
.Lloop1:
  xor a0, a0, a1
  add a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  xor a0, a0, a1
  add a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 162
.Lloop2:
  sll a0, a0, a1
  mul a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  srl a4, a4, a5
  add a5, a5, a6
  xor a6, a6, a7
  sll a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 1122334468
  .word 3776770237
  .word 2136238710
  .word 495707183
  .word 3150142952
  .word 1509611425
  .word 4164047194
  .word 2523515667
  .word 882984140
  .word 3537419909
  .word 1896888382
  .word 256356855
  .word 2910792624
  .word 1270261097
  .word 3924696866
  .word 2284165339
  .word 643633812
  .word 3298069581
  .word 1657538054
  .word 17006527
  .word 2671442296
  .word 1030910769
  .word 3685346538
  .word 2044815011
  .word 404283484
  .word 3058719253
  .word 1418187726
  .word 4072623495
  .word 2432091968
  .word 791560441
  .word 3445996210
  .word 1805464683
  .word 164933156
  .word 2819368925
  .word 1178837398
  .word 3833273167
  .word 2192741640
  .word 552210113
  .word 3206645882
  .word 1566114355
  .word 4220550124
  .word 2580018597
  .word 939487070
  .word 3593922839
  .word 1953391312
  .word 312859785
  .word 2967295554
  .word 1326764027
  .word 3981199796
  .word 2340668269
  .word 700136742
  .word 3354572511
  .word 1714040984
  .word 73509457
  .word 2727945226
  .word 1087413699
  .word 3741849468
  .word 2101317941
  .word 460786414
  .word 3115222183
  .word 1474690656
  .word 4129126425
  .word 2488594898
  .word 848063371
.section .bss
.balign 4
snapshot: .space 32
