.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 602019163
  li a1, 4185563966
  li a2, 1
  li a3, 1
  li a4, 4294967295
  li a5, 4294967295
  li a6, 134217745
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 9295
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 728
.Lloop0:
  bnez a5, .Lskip0_0
  mv a6, a1
.Lskip0_0:
  bnez a7, .Lskip0_1
  mv a6, a1
.Lskip0_1:
  bnez a0, .Lskip0_2
  mv a5, a1
.Lskip0_2:
  bnez a2, .Lskip0_3
  mv a3, a1
.Lskip0_3:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 51042
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 752
.Lloop1:
  bnez a5, .Lskip1_0
  mv a3, a0
.Lskip1_0:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80120
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 54
.Lloop2:
  srl a3, a4, a1
  add a2, a0, a0
  or a6, a2, a1
  divu a4, a0, a1
  sll a4, a5, a1
  and a6, a6, a1
  bnez a3, .Lskip2_6
  mv a3, a1
.Lskip2_6:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
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
  .word 4273087611
  .word 2632556084
  .word 992024557
  .word 3646460326
  .word 2005928799
  .word 365397272
  .word 3019833041
  .word 1379301514
  .word 4033737283
  .word 2393205756
  .word 752674229
  .word 3407109998
  .word 1766578471
  .word 126046944
  .word 2780482713
  .word 1139951186
  .word 3794386955
  .word 2153855428
  .word 513323901
  .word 3167759670
  .word 1527228143
  .word 4181663912
  .word 2541132385
  .word 900600858
  .word 3555036627
  .word 1914505100
  .word 273973573
  .word 2928409342
  .word 1287877815
  .word 3942313584
  .word 2301782057
  .word 661250530
  .word 3315686299
  .word 1675154772
  .word 34623245
  .word 2689059014
  .word 1048527487
  .word 3702963256
  .word 2062431729
  .word 421900202
  .word 3076335971
  .word 1435804444
  .word 4090240213
  .word 2449708686
  .word 809177159
  .word 3463612928
  .word 1823081401
  .word 182549874
  .word 2836985643
  .word 1196454116
  .word 3850889885
  .word 2210358358
  .word 569826831
  .word 3224262600
  .word 1583731073
  .word 4238166842
  .word 2597635315
  .word 957103788
  .word 3611539557
  .word 1971008030
  .word 330476503
  .word 2984912272
  .word 1344380745
  .word 3998816514
.section .bss
.balign 4
snapshot: .space 32
