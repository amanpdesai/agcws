.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 0
  li a3, 17
  li a4, 0
  li a5, 17
  li a6, 31
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 98799
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 358
.Lloop0:
  mul a2, a2, a3
  mul a2, a3, a2
  mul a7, a5, a2
  mul a6, a6, a7
  mul a6, a5, a6
  mul a6, a6, a6
  mul a5, a5, a6
  mul a4, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 130100
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 70
.Lloop1:
  mul a1, a3, a0
  mul a7, a7, a3
  mul a2, a2, a0
  mul a4, a0, a2
  mul a5, a2, a0
  mul a7, a7, a3
  mul a3, a1, a7
  mul a1, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 161564
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 168
.Lloop2:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  add a6, a4, a1
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
  .word 134772680
  .word 2789208449
  .word 1148676922
  .word 3803112691
  .word 2162581164
  .word 522049637
  .word 3176485406
  .word 1535953879
  .word 4190389648
  .word 2549858121
  .word 909326594
  .word 3563762363
  .word 1923230836
  .word 282699309
  .word 2937135078
  .word 1296603551
  .word 3951039320
  .word 2310507793
  .word 669976266
  .word 3324412035
  .word 1683880508
  .word 43348981
  .word 2697784750
  .word 1057253223
  .word 3711688992
  .word 2071157465
  .word 430625938
  .word 3085061707
  .word 1444530180
  .word 4098965949
  .word 2458434422
  .word 817902895
  .word 3472338664
  .word 1831807137
  .word 191275610
  .word 2845711379
  .word 1205179852
  .word 3859615621
  .word 2219084094
  .word 578552567
  .word 3232988336
  .word 1592456809
  .word 4246892578
  .word 2606361051
  .word 965829524
  .word 3620265293
  .word 1979733766
  .word 339202239
  .word 2993638008
  .word 1353106481
  .word 4007542250
  .word 2367010723
  .word 726479196
  .word 3380914965
  .word 1740383438
  .word 99851911
  .word 2754287680
  .word 1113756153
  .word 3768191922
  .word 2127660395
  .word 487128868
  .word 3141564637
  .word 1501033110
  .word 4155468879
.section .bss
.balign 4
snapshot: .space 32
