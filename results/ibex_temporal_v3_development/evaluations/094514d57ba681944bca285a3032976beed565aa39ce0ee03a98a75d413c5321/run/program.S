.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 4294967295
  li a3, 3205952778
  li a4, 31
  li a5, 4294967295
  li a6, 4294967295
  li a7, 3680914136
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 1380
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 56
.Lloop0:
  bnez a6, .Lskip0_0
  mv a6, a0
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a7, a1
.Lskip0_1:
  bnez a3, .Lskip0_2
  mv a7, a0
.Lskip0_2:
  bnez a1, .Lskip0_3
  mv a3, a0
.Lskip0_3:
  bnez a3, .Lskip0_4
  mv a5, a1
.Lskip0_4:
  bnez a0, .Lskip0_5
  mv a4, a1
.Lskip0_5:
  bnez a7, .Lskip0_6
  mv a6, a0
.Lskip0_6:
  bnez a4, .Lskip0_7
  mv a5, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 1589
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 24
.Lloop1:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 38033
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 80
.Lloop2:
  divu a4, a5, a1
  divu a1, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 46747
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 207
.Lloop3:
  srl a4, a0, a2
  add a3, a7, a7
  add a2, a4, a3
  srl a2, a0, a5
  srl a1, a7, a5
  add a2, a6, a6
  xor a3, a3, a5
  or a1, a6, a4
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 104000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 16
.Lloop4:
  xor a3, a4, a3
  xor a6, a2, a4
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 131659
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 314
.Lloop5:
  mul a7, a1, a0
  mul a2, a5, a0
  xor a6, a2, a0
  sll a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 133985
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 62
.Lloop6:
  bnez a0, .Lskip6_0
  mv a2, a7
.Lskip6_0:
  bnez a3, .Lskip6_1
  mv a2, a4
.Lskip6_1:
  bnez a3, .Lskip6_2
  mv a1, a6
.Lskip6_2:
  bnez a1, .Lskip6_3
  mv a0, a0
.Lskip6_3:
  bnez a7, .Lskip6_4
  mv a5, a1
.Lskip6_4:
  bnez a2, .Lskip6_5
  mv a2, a0
.Lskip6_5:
  bnez a1, .Lskip6_6
  mv a7, a6
.Lskip6_6:
  bnez a6, .Lskip6_7
  mv a1, a6
.Lskip6_7:
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 1097426329
  .word 3751862098
  .word 2111330571
  .word 470799044
  .word 3125234813
  .word 1484703286
  .word 4139139055
  .word 2498607528
  .word 858076001
  .word 3512511770
  .word 1871980243
  .word 231448716
  .word 2885884485
  .word 1245352958
  .word 3899788727
  .word 2259257200
  .word 618725673
  .word 3273161442
  .word 1632629915
  .word 4287065684
  .word 2646534157
  .word 1006002630
  .word 3660438399
  .word 2019906872
  .word 379375345
  .word 3033811114
  .word 1393279587
  .word 4047715356
  .word 2407183829
  .word 766652302
  .word 3421088071
  .word 1780556544
  .word 140025017
  .word 2794460786
  .word 1153929259
  .word 3808365028
  .word 2167833501
  .word 527301974
  .word 3181737743
  .word 1541206216
  .word 4195641985
  .word 2555110458
  .word 914578931
  .word 3569014700
  .word 1928483173
  .word 287951646
  .word 2942387415
  .word 1301855888
  .word 3956291657
  .word 2315760130
  .word 675228603
  .word 3329664372
  .word 1689132845
  .word 48601318
  .word 2703037087
  .word 1062505560
  .word 3716941329
  .word 2076409802
  .word 435878275
  .word 3090314044
  .word 1449782517
  .word 4104218286
  .word 2463686759
  .word 823155232
.section .bss
.balign 4
snapshot: .space 32
