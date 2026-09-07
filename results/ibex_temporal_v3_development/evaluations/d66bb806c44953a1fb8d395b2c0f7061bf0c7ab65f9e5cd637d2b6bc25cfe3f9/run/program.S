.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 0
  li a3, 1
  li a4, 0
  li a5, 0
  li a6, 4294967295
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 21357
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 76
.Lloop0:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25826
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 156
.Lloop1:
  divu a0, a1, a4
  divu a3, a6, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 103375
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 11
.Lloop2:
  srl a6, a3, a1
  and a7, a6, a0
  sll a3, a2, a1
  or a2, a6, a1
  xor a6, a3, a0
  srl a7, a6, a0
  sll a6, a7, a0
  and a2, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 132686
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 36
.Lloop3:
  mul a0, a4, a7
  mul a7, a5, a2
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 136024
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 1616
.Lloop4:
  bnez a2, .Lskip4_0
  mv a0, a1
.Lskip4_0:
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 150276
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 124
.Lloop5:
  add a2, a6, a1
  sll a7, a2, a1
  sll a4, a2, a0
  add a6, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 162324
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 77
.Lloop6:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  or a2, a0, a6
  add a0, a1, a2
  bnez a1, .Lskip6_3
  mv a5, a6
.Lskip6_3:
  bnez a5, .Lskip6_4
  mv a0, a3
.Lskip6_4:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  srl a3, a2, a4
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 174026
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 144
.Lloop7:
  divu a4, a7, a0
  divu a2, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 3663387947
  .word 2022856420
  .word 382324893
  .word 3036760662
  .word 1396229135
  .word 4050664904
  .word 2410133377
  .word 769601850
  .word 3424037619
  .word 1783506092
  .word 142974565
  .word 2797410334
  .word 1156878807
  .word 3811314576
  .word 2170783049
  .word 530251522
  .word 3184687291
  .word 1544155764
  .word 4198591533
  .word 2558060006
  .word 917528479
  .word 3571964248
  .word 1931432721
  .word 290901194
  .word 2945336963
  .word 1304805436
  .word 3959241205
  .word 2318709678
  .word 678178151
  .word 3332613920
  .word 1692082393
  .word 51550866
  .word 2705986635
  .word 1065455108
  .word 3719890877
  .word 2079359350
  .word 438827823
  .word 3093263592
  .word 1452732065
  .word 4107167834
  .word 2466636307
  .word 826104780
  .word 3480540549
  .word 1840009022
  .word 199477495
  .word 2853913264
  .word 1213381737
  .word 3867817506
  .word 2227285979
  .word 586754452
  .word 3241190221
  .word 1600658694
  .word 4255094463
  .word 2614562936
  .word 974031409
  .word 3628467178
  .word 1987935651
  .word 347404124
  .word 3001839893
  .word 1361308366
  .word 4015744135
  .word 2375212608
  .word 734681081
  .word 3389116850
.section .bss
.balign 4
snapshot: .space 32
