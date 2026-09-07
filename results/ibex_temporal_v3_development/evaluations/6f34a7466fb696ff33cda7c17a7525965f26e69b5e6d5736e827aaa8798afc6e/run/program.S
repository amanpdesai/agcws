.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 17
  li a2, 0
  li a3, 1
  li a4, 1
  li a5, 17
  li a6, 1
  li a7, 84173419
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 14610
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 20
.Lloop0:
  bnez a0, .Lskip0_0
  mv a3, a1
.Lskip0_0:
  bnez a5, .Lskip0_1
  mv a6, a1
.Lskip0_1:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 43137
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 1712
.Lloop1:
  mul a4, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 59308
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 57
.Lloop2:
  bnez a1, .Lskip2_0
  mv a7, a2
.Lskip2_0:
  bnez a0, .Lskip2_1
  mv a5, a0
.Lskip2_1:
  bnez a7, .Lskip2_2
  mv a0, a5
.Lskip2_2:
  bnez a2, .Lskip2_3
  mv a5, a3
.Lskip2_3:
  bnez a3, .Lskip2_4
  mv a5, a7
.Lskip2_4:
  bnez a0, .Lskip2_5
  mv a3, a1
.Lskip2_5:
  bnez a5, .Lskip2_6
  mv a2, a0
.Lskip2_6:
  bnez a1, .Lskip2_7
  mv a3, a1
.Lskip2_7:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 100238
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 176
.Lloop3:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 110702
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 1696
.Lloop4:
  divu a3, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 164913
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 8
.Lloop5:
  mul a2, a5, a1
  mul a5, a3, a0
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
  .word 4160007669
  .word 2519476142
  .word 878944615
  .word 3533380384
  .word 1892848857
  .word 252317330
  .word 2906753099
  .word 1266221572
  .word 3920657341
  .word 2280125814
  .word 639594287
  .word 3294030056
  .word 1653498529
  .word 12967002
  .word 2667402771
  .word 1026871244
  .word 3681307013
  .word 2040775486
  .word 400243959
  .word 3054679728
  .word 1414148201
  .word 4068583970
  .word 2428052443
  .word 787520916
  .word 3441956685
  .word 1801425158
  .word 160893631
  .word 2815329400
  .word 1174797873
  .word 3829233642
  .word 2188702115
  .word 548170588
  .word 3202606357
  .word 1562074830
  .word 4216510599
  .word 2575979072
  .word 935447545
  .word 3589883314
  .word 1949351787
  .word 308820260
  .word 2963256029
  .word 1322724502
  .word 3977160271
  .word 2336628744
  .word 696097217
  .word 3350532986
  .word 1710001459
  .word 69469932
  .word 2723905701
  .word 1083374174
  .word 3737809943
  .word 2097278416
  .word 456746889
  .word 3111182658
  .word 1470651131
  .word 4125086900
  .word 2484555373
  .word 844023846
  .word 3498459615
  .word 1857928088
  .word 217396561
  .word 2871832330
  .word 1231300803
  .word 3885736572
.section .bss
.balign 4
snapshot: .space 32
