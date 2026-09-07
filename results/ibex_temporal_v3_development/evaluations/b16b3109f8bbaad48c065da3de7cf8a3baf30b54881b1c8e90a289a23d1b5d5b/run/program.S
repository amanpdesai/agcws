.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4294967295
  li a2, 0
  li a3, 17
  li a4, 0
  li a5, 0
  li a6, 17
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 1706
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 86
.Lloop0:
  mul a6, a0, a1
  mul a2, a7, a1
  mul a7, a5, a0
  mul a7, a0, a0
  mul a4, a1, a1
  mul a3, a6, a0
  mul a4, a3, a1
  mul a5, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 19841
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 182
.Lloop1:
  mul a4, a3, a1
  mul a2, a6, a4
  mul a0, a0, a2
  mul a7, a1, a6
  mul a4, a1, a7
  mul a4, a0, a4
  mul a0, a2, a2
  mul a4, a6, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 64697
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 732
.Lloop2:
  and a0, a2, a7
  sll a3, a2, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 167238
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 28
.Lloop3:
  divu a4, a1, a0
  divu a5, a0, a0
  divu a7, a0, a1
  divu a2, a2, a0
  divu a7, a5, a1
  divu a7, a4, a0
  divu a4, a4, a1
  divu a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 169196
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 66
.Lloop4:
  bnez a1, .Lskip4_0
  mv a6, a1
.Lskip4_0:
  bnez a2, .Lskip4_1
  mv a7, a1
.Lskip4_1:
  bnez a3, .Lskip4_2
  mv a5, a1
.Lskip4_2:
  bnez a4, .Lskip4_3
  mv a4, a0
.Lskip4_3:
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
  .word 182803298
  .word 2837239067
  .word 1196707540
  .word 3851143309
  .word 2210611782
  .word 570080255
  .word 3224516024
  .word 1583984497
  .word 4238420266
  .word 2597888739
  .word 957357212
  .word 3611792981
  .word 1971261454
  .word 330729927
  .word 2985165696
  .word 1344634169
  .word 3999069938
  .word 2358538411
  .word 718006884
  .word 3372442653
  .word 1731911126
  .word 91379599
  .word 2745815368
  .word 1105283841
  .word 3759719610
  .word 2119188083
  .word 478656556
  .word 3133092325
  .word 1492560798
  .word 4146996567
  .word 2506465040
  .word 865933513
  .word 3520369282
  .word 1879837755
  .word 239306228
  .word 2893741997
  .word 1253210470
  .word 3907646239
  .word 2267114712
  .word 626583185
  .word 3281018954
  .word 1640487427
  .word 4294923196
  .word 2654391669
  .word 1013860142
  .word 3668295911
  .word 2027764384
  .word 387232857
  .word 3041668626
  .word 1401137099
  .word 4055572868
  .word 2415041341
  .word 774509814
  .word 3428945583
  .word 1788414056
  .word 147882529
  .word 2802318298
  .word 1161786771
  .word 3816222540
  .word 2175691013
  .word 535159486
  .word 3189595255
  .word 1549063728
  .word 4203499497
.section .bss
.balign 4
snapshot: .space 32
