.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 17
  li a2, 17
  li a3, 4294967295
  li a4, 0
  li a5, 31
  li a6, 31
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 4299
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 400
.Lloop0:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 35017
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 92
.Lloop1:
  bnez a3, .Lskip1_0
  mv a3, a1
.Lskip1_0:
  bnez a0, .Lskip1_1
  mv a3, a1
.Lskip1_1:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 41067
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 22
.Lloop2:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 69217
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 100
.Lloop3:
  bnez a7, .Lskip3_0
  mv a2, a1
.Lskip3_0:
  bnez a4, .Lskip3_1
  mv a5, a0
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 85248
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 1896
.Lloop4:
  add a5, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 90192
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 408
.Lloop5:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 107800
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 344
.Lloop6:
  bnez a5, .Lskip6_0
  mv a4, a0
.Lskip6_0:
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 154582
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 11
.Lloop7:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
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
  .word 3906442532
  .word 2265911005
  .word 625379478
  .word 3279815247
  .word 1639283720
  .word 4293719489
  .word 2653187962
  .word 1012656435
  .word 3667092204
  .word 2026560677
  .word 386029150
  .word 3040464919
  .word 1399933392
  .word 4054369161
  .word 2413837634
  .word 773306107
  .word 3427741876
  .word 1787210349
  .word 146678822
  .word 2801114591
  .word 1160583064
  .word 3815018833
  .word 2174487306
  .word 533955779
  .word 3188391548
  .word 1547860021
  .word 4202295790
  .word 2561764263
  .word 921232736
  .word 3575668505
  .word 1935136978
  .word 294605451
  .word 2949041220
  .word 1308509693
  .word 3962945462
  .word 2322413935
  .word 681882408
  .word 3336318177
  .word 1695786650
  .word 55255123
  .word 2709690892
  .word 1069159365
  .word 3723595134
  .word 2083063607
  .word 442532080
  .word 3096967849
  .word 1456436322
  .word 4110872091
  .word 2470340564
  .word 829809037
  .word 3484244806
  .word 1843713279
  .word 203181752
  .word 2857617521
  .word 1217085994
  .word 3871521763
  .word 2230990236
  .word 590458709
  .word 3244894478
  .word 1604362951
  .word 4258798720
  .word 2618267193
  .word 977735666
  .word 3632171435
.section .bss
.balign 4
snapshot: .space 32
