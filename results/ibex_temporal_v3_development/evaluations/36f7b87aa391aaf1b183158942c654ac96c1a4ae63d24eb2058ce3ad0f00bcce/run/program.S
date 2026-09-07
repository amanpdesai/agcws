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
  li t6, 125
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 131
.Lloop1:
  xor a0, a0, a1
  sll a1, a1, a2
  mul a2, a2, a3
  and a3, a3, a4
  or a4, a4, a5
  srl a5, a5, a6
  add a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  xor a0, a0, a1
  sll a1, a1, a2
  li s9, 45000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
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
  li s9, 70000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 127
.Lloop3:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  mul a3, a3, a4
  and a4, a4, a5
  or a5, a5, a6
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
  .word 1122334466
  .word 3776770235
  .word 2136238708
  .word 495707181
  .word 3150142950
  .word 1509611423
  .word 4164047192
  .word 2523515665
  .word 882984138
  .word 3537419907
  .word 1896888380
  .word 256356853
  .word 2910792622
  .word 1270261095
  .word 3924696864
  .word 2284165337
  .word 643633810
  .word 3298069579
  .word 1657538052
  .word 17006525
  .word 2671442294
  .word 1030910767
  .word 3685346536
  .word 2044815009
  .word 404283482
  .word 3058719251
  .word 1418187724
  .word 4072623493
  .word 2432091966
  .word 791560439
  .word 3445996208
  .word 1805464681
  .word 164933154
  .word 2819368923
  .word 1178837396
  .word 3833273165
  .word 2192741638
  .word 552210111
  .word 3206645880
  .word 1566114353
  .word 4220550122
  .word 2580018595
  .word 939487068
  .word 3593922837
  .word 1953391310
  .word 312859783
  .word 2967295552
  .word 1326764025
  .word 3981199794
  .word 2340668267
  .word 700136740
  .word 3354572509
  .word 1714040982
  .word 73509455
  .word 2727945224
  .word 1087413697
  .word 3741849466
  .word 2101317939
  .word 460786412
  .word 3115222181
  .word 1474690654
  .word 4129126423
  .word 2488594896
  .word 848063369
.section .bss
.balign 4
snapshot: .space 32
