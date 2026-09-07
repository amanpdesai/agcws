.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 17
  li a2, 31
  li a3, 4243052073
  li a4, 1
  li a5, 1
  li a6, 31
  li a7, 3461416045
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 99230
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 45
.Lloop0:
  divu a6, a1, a0
  divu a5, a7, a1
  divu a5, a2, a0
  divu a6, a7, a0
  divu a3, a0, a1
  divu a5, a1, a1
  divu a2, a5, a1
  divu a5, a1, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 102394
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 72
.Lloop1:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 118688
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 358
.Lloop2:
  mul a6, a6, a0
  mul a2, a2, a0
  mul a4, a6, a0
  mul a3, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 126277
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 244
.Lloop3:
  bnez a0, .Lskip3_0
  mv a4, a1
.Lskip3_0:
  bnez a3, .Lskip3_1
  mv a5, a1
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 146046
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 278
.Lloop4:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 152721
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 39
.Lloop5:
  bnez a0, .Lskip5_0
  mv a4, a1
.Lskip5_0:
  bnez a3, .Lskip5_1
  mv a4, a1
.Lskip5_1:
  bnez a6, .Lskip5_2
  mv a2, a1
.Lskip5_2:
  bnez a5, .Lskip5_3
  mv a6, a1
.Lskip5_3:
  bnez a6, .Lskip5_4
  mv a2, a1
.Lskip5_4:
  bnez a0, .Lskip5_5
  mv a2, a1
.Lskip5_5:
  bnez a4, .Lskip5_6
  mv a3, a0
.Lskip5_6:
  bnez a5, .Lskip5_7
  mv a6, a1
.Lskip5_7:
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 155247
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 140
.Lloop6:
  bnez a2, .Lskip6_0
  mv a6, a1
.Lskip6_0:
  bnez a6, .Lskip6_1
  mv a6, a3
.Lskip6_1:
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 167151
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 40
.Lloop7:
  bnez a4, .Lskip7_0
  mv a2, a1
.Lskip7_0:
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
  .word 3667647469
  .word 2027115942
  .word 386584415
  .word 3041020184
  .word 1400488657
  .word 4054924426
  .word 2414392899
  .word 773861372
  .word 3428297141
  .word 1787765614
  .word 147234087
  .word 2801669856
  .word 1161138329
  .word 3815574098
  .word 2175042571
  .word 534511044
  .word 3188946813
  .word 1548415286
  .word 4202851055
  .word 2562319528
  .word 921788001
  .word 3576223770
  .word 1935692243
  .word 295160716
  .word 2949596485
  .word 1309064958
  .word 3963500727
  .word 2322969200
  .word 682437673
  .word 3336873442
  .word 1696341915
  .word 55810388
  .word 2710246157
  .word 1069714630
  .word 3724150399
  .word 2083618872
  .word 443087345
  .word 3097523114
  .word 1456991587
  .word 4111427356
  .word 2470895829
  .word 830364302
  .word 3484800071
  .word 1844268544
  .word 203737017
  .word 2858172786
  .word 1217641259
  .word 3872077028
  .word 2231545501
  .word 591013974
  .word 3245449743
  .word 1604918216
  .word 4259353985
  .word 2618822458
  .word 978290931
  .word 3632726700
  .word 1992195173
  .word 351663646
  .word 3006099415
  .word 1365567888
  .word 4020003657
  .word 2379472130
  .word 738940603
  .word 3393376372
.section .bss
.balign 4
snapshot: .space 32
