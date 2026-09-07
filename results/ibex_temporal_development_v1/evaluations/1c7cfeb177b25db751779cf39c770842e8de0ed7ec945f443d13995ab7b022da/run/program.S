.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 0
  li a3, 2662913795
  li a4, 0
  li a5, 4294967295
  li a6, 0
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 56399
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 77
.Lloop0:
  xor a2, a6, a1
  srl a4, a2, a1
  xor a6, a2, a0
  mul a2, a7, a0
  mul a3, a4, a0
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  bnez a6, .Lskip0_6
  mv a5, a1
.Lskip0_6:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 102374
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 400
.Lloop1:
  sll a7, a2, a0
  srl a1, a1, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 105645
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 196
.Lloop2:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 116314
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 196
.Lloop3:
  bnez a2, .Lskip3_0
  mv a5, a1
.Lskip3_0:
  bnez a0, .Lskip3_1
  mv a6, a0
.Lskip3_1:
  bnez a2, .Lskip3_2
  mv a4, a1
.Lskip3_2:
  bnez a2, .Lskip3_3
  mv a5, a0
.Lskip3_3:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 158118
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 188
.Lloop4:
  divu a1, a3, a3
  divu a1, a2, a1
  divu a5, a4, a0
  divu a6, a6, a6
  divu a6, a7, a7
  divu a6, a4, a2
  divu a4, a2, a5
  divu a5, a5, a2
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
  .word 3062472912
  .word 1421941385
  .word 4076377154
  .word 2435845627
  .word 795314100
  .word 3449749869
  .word 1809218342
  .word 168686815
  .word 2823122584
  .word 1182591057
  .word 3837026826
  .word 2196495299
  .word 555963772
  .word 3210399541
  .word 1569868014
  .word 4224303783
  .word 2583772256
  .word 943240729
  .word 3597676498
  .word 1957144971
  .word 316613444
  .word 2971049213
  .word 1330517686
  .word 3984953455
  .word 2344421928
  .word 703890401
  .word 3358326170
  .word 1717794643
  .word 77263116
  .word 2731698885
  .word 1091167358
  .word 3745603127
  .word 2105071600
  .word 464540073
  .word 3118975842
  .word 1478444315
  .word 4132880084
  .word 2492348557
  .word 851817030
  .word 3506252799
  .word 1865721272
  .word 225189745
  .word 2879625514
  .word 1239093987
  .word 3893529756
  .word 2252998229
  .word 612466702
  .word 3266902471
  .word 1626370944
  .word 4280806713
  .word 2640275186
  .word 999743659
  .word 3654179428
  .word 2013647901
  .word 373116374
  .word 3027552143
  .word 1387020616
  .word 4041456385
  .word 2400924858
  .word 760393331
  .word 3414829100
  .word 1774297573
  .word 133766046
  .word 2788201815
.section .bss
.balign 4
snapshot: .space 32
