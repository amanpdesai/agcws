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
  li a4, 1
  li a5, 0
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 1000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 137
.Lloop0:
  bnez a5, .Lskip0_0
  mv a3, a1
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a3, a1
.Lskip0_1:
  bnez a5, .Lskip0_2
  mv a6, a0
.Lskip0_2:
  bnez a4, .Lskip0_3
  mv a7, a1
.Lskip0_3:
  bnez a3, .Lskip0_4
  mv a6, a1
.Lskip0_4:
  bnez a1, .Lskip0_5
  mv a7, a0
.Lskip0_5:
  bnez a0, .Lskip0_6
  mv a5, a1
.Lskip0_6:
  bnez a1, .Lskip0_7
  mv a2, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  bnez a5, .Ltail_skip0_0
  mv a3, a1
.Ltail_skip0_0:
  bnez a6, .Ltail_skip0_1
  mv a3, a1
.Ltail_skip0_1:
  bnez a5, .Ltail_skip0_2
  mv a6, a0
.Ltail_skip0_2:
  bnez a4, .Ltail_skip0_3
  mv a7, a1
.Ltail_skip0_3:
  li s9, 2000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 250
.Lloop1:
  bnez a3, .Lskip1_0
  mv a4, a0
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a6, a2
.Lskip1_1:
  bnez a7, .Lskip1_2
  mv a3, a2
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a7, a1
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 125
.Lloop2:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  divu a3, a5, a1
  divu a7, a5, a0
  divu a4, a6, a1
  divu a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 124
.Lloop3:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
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
  .word 1698240398
  .word 57708871
  .word 2712144640
  .word 1071613113
  .word 3726048882
  .word 2085517355
  .word 444985828
  .word 3099421597
  .word 1458890070
  .word 4113325839
  .word 2472794312
  .word 832262785
  .word 3486698554
  .word 1846167027
  .word 205635500
  .word 2860071269
  .word 1219539742
  .word 3873975511
  .word 2233443984
  .word 592912457
  .word 3247348226
  .word 1606816699
  .word 4261252468
  .word 2620720941
  .word 980189414
  .word 3634625183
  .word 1994093656
  .word 353562129
  .word 3007997898
  .word 1367466371
  .word 4021902140
  .word 2381370613
  .word 740839086
  .word 3395274855
  .word 1754743328
  .word 114211801
  .word 2768647570
  .word 1128116043
  .word 3782551812
  .word 2142020285
  .word 501488758
  .word 3155924527
  .word 1515393000
  .word 4169828769
  .word 2529297242
  .word 888765715
  .word 3543201484
  .word 1902669957
  .word 262138430
  .word 2916574199
  .word 1276042672
  .word 3930478441
  .word 2289946914
  .word 649415387
  .word 3303851156
  .word 1663319629
  .word 22788102
  .word 2677223871
  .word 1036692344
  .word 3691128113
  .word 2050596586
  .word 410065059
  .word 3064500828
  .word 1423969301
.section .bss
.balign 4
snapshot: .space 32
