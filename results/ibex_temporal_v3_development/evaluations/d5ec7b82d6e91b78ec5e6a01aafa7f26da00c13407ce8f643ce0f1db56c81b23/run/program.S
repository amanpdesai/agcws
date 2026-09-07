.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 543449912
  li a1, 17
  li a2, 0
  li a3, 1918431710
  li a4, 4294967295
  li a5, 17
  li a6, 487449572
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 27039
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 182
.Lloop0:
  srl a0, a5, a7
  xor a4, a6, a3
  srl a4, a3, a7
  srl a0, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 29625
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 16
.Lloop1:
  add a2, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 53833
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 33
.Lloop2:
  bnez a2, .Lskip2_0
  mv a5, a6
.Lskip2_0:
  bnez a6, .Lskip2_1
  mv a0, a5
.Lskip2_1:
  bnez a4, .Lskip2_2
  mv a1, a2
.Lskip2_2:
  bnez a0, .Lskip2_3
  mv a0, a6
.Lskip2_3:
  bnez a4, .Lskip2_4
  mv a7, a6
.Lskip2_4:
  bnez a6, .Lskip2_5
  mv a2, a6
.Lskip2_5:
  bnez a6, .Lskip2_6
  mv a4, a4
.Lskip2_6:
  bnez a6, .Lskip2_7
  mv a0, a5
.Lskip2_7:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 87555
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 468
.Lloop3:
  bnez a3, .Lskip3_0
  mv a0, a0
.Lskip3_0:
  bnez a2, .Lskip3_1
  mv a5, a1
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 135496
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 92
.Lloop4:
  xor a6, a1, a1
  xor a7, a2, a0
  and a6, a2, a0
  and a6, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 160184
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 223
.Lloop5:
  bnez a6, .Lskip5_0
  mv a4, a3
.Lskip5_0:
  bnez a0, .Lskip5_1
  mv a3, a7
.Lskip5_1:
  bnez a0, .Lskip5_2
  mv a4, a7
.Lskip5_2:
  bnez a6, .Lskip5_3
  mv a0, a7
.Lskip5_3:
  bnez a7, .Lskip5_4
  mv a7, a0
.Lskip5_4:
  bnez a1, .Lskip5_5
  mv a7, a3
.Lskip5_5:
  bnez a4, .Lskip5_6
  mv a1, a6
.Lskip5_6:
  bnez a0, .Lskip5_7
  mv a0, a0
.Lskip5_7:
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 3417102572
  .word 1776571045
  .word 136039518
  .word 2790475287
  .word 1149943760
  .word 3804379529
  .word 2163848002
  .word 523316475
  .word 3177752244
  .word 1537220717
  .word 4191656486
  .word 2551124959
  .word 910593432
  .word 3565029201
  .word 1924497674
  .word 283966147
  .word 2938401916
  .word 1297870389
  .word 3952306158
  .word 2311774631
  .word 671243104
  .word 3325678873
  .word 1685147346
  .word 44615819
  .word 2699051588
  .word 1058520061
  .word 3712955830
  .word 2072424303
  .word 431892776
  .word 3086328545
  .word 1445797018
  .word 4100232787
  .word 2459701260
  .word 819169733
  .word 3473605502
  .word 1833073975
  .word 192542448
  .word 2846978217
  .word 1206446690
  .word 3860882459
  .word 2220350932
  .word 579819405
  .word 3234255174
  .word 1593723647
  .word 4248159416
  .word 2607627889
  .word 967096362
  .word 3621532131
  .word 1981000604
  .word 340469077
  .word 2994904846
  .word 1354373319
  .word 4008809088
  .word 2368277561
  .word 727746034
  .word 3382181803
  .word 1741650276
  .word 101118749
  .word 2755554518
  .word 1115022991
  .word 3769458760
  .word 2128927233
  .word 488395706
  .word 3142831475
.section .bss
.balign 4
snapshot: .space 32
