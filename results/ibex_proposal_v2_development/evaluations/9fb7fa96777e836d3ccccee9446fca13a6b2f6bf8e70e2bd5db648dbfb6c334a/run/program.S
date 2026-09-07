.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 4294967295
  li a4, 3712213172
  li a5, 17
  li a6, 2265335430
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 5529
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 117
.Lloop0:
  mul a5, a2, a0
  mul a4, a3, a0
  mul a3, a1, a1
  mul a5, a2, a0
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  mul a7, a4, a0
  mul a7, a2, a1
  mul a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 44990
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 768
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 111706
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 179
.Lloop2:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 135784
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 480
.Lloop3:
  mul a3, a3, a0
  mul a4, a2, a0
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
  .word 3463607953
  .word 1823076426
  .word 182544899
  .word 2836980668
  .word 1196449141
  .word 3850884910
  .word 2210353383
  .word 569821856
  .word 3224257625
  .word 1583726098
  .word 4238161867
  .word 2597630340
  .word 957098813
  .word 3611534582
  .word 1971003055
  .word 330471528
  .word 2984907297
  .word 1344375770
  .word 3998811539
  .word 2358280012
  .word 717748485
  .word 3372184254
  .word 1731652727
  .word 91121200
  .word 2745556969
  .word 1105025442
  .word 3759461211
  .word 2118929684
  .word 478398157
  .word 3132833926
  .word 1492302399
  .word 4146738168
  .word 2506206641
  .word 865675114
  .word 3520110883
  .word 1879579356
  .word 239047829
  .word 2893483598
  .word 1252952071
  .word 3907387840
  .word 2266856313
  .word 626324786
  .word 3280760555
  .word 1640229028
  .word 4294664797
  .word 2654133270
  .word 1013601743
  .word 3668037512
  .word 2027505985
  .word 386974458
  .word 3041410227
  .word 1400878700
  .word 4055314469
  .word 2414782942
  .word 774251415
  .word 3428687184
  .word 1788155657
  .word 147624130
  .word 2802059899
  .word 1161528372
  .word 3815964141
  .word 2175432614
  .word 534901087
  .word 3189336856
.section .bss
.balign 4
snapshot: .space 32
