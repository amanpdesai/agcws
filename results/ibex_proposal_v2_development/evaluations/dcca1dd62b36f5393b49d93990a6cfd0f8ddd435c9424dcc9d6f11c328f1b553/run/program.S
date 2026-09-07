.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1515208206
  li a2, 1
  li a3, 1
  li a4, 0
  li a5, 1904964410
  li a6, 0
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 30806
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 1392
.Lloop0:
  and a5, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 48537
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 86
.Lloop1:
  mul a5, a4, a1
  mul a5, a7, a0
  mul a3, a3, a0
  mul a5, a1, a1
  mul a7, a3, a0
  mul a6, a3, a1
  mul a2, a1, a0
  mul a6, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 63149
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 27
.Lloop2:
  xor a6, a7, a5
  sll a7, a3, a3
  xor a7, a1, a0
  or a2, a4, a7
  or a1, a0, a3
  and a3, a7, a4
  and a2, a0, a5
  and a5, a3, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 138056
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 134
.Lloop3:
  divu a1, a5, a5
  divu a7, a0, a5
  divu a6, a5, a5
  divu a4, a0, a5
  divu a4, a6, a2
  divu a6, a2, a3
  divu a1, a3, a7
  divu a0, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 176227
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 364
.Lloop4:
  add a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
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
  .word 1834917931
  .word 194386404
  .word 2848822173
  .word 1208290646
  .word 3862726415
  .word 2222194888
  .word 581663361
  .word 3236099130
  .word 1595567603
  .word 4250003372
  .word 2609471845
  .word 968940318
  .word 3623376087
  .word 1982844560
  .word 342313033
  .word 2996748802
  .word 1356217275
  .word 4010653044
  .word 2370121517
  .word 729589990
  .word 3384025759
  .word 1743494232
  .word 102962705
  .word 2757398474
  .word 1116866947
  .word 3771302716
  .word 2130771189
  .word 490239662
  .word 3144675431
  .word 1504143904
  .word 4158579673
  .word 2518048146
  .word 877516619
  .word 3531952388
  .word 1891420861
  .word 250889334
  .word 2905325103
  .word 1264793576
  .word 3919229345
  .word 2278697818
  .word 638166291
  .word 3292602060
  .word 1652070533
  .word 11539006
  .word 2665974775
  .word 1025443248
  .word 3679879017
  .word 2039347490
  .word 398815963
  .word 3053251732
  .word 1412720205
  .word 4067155974
  .word 2426624447
  .word 786092920
  .word 3440528689
  .word 1799997162
  .word 159465635
  .word 2813901404
  .word 1173369877
  .word 3827805646
  .word 2187274119
  .word 546742592
  .word 3201178361
  .word 1560646834
.section .bss
.balign 4
snapshot: .space 32
