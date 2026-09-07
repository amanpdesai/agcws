.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 250
.Lloop0:
  add a2, a0, a1
  mul a4, a2, a3
  xor a6, a4, a5
  sll a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 20000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 500
.Lloop1:
  divu a2, a0, a1
  divu a4, a2, a3
  divu a6, a4, a5
  divu a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 40000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 274
.Lloop2:
  add a2, a0, a1
  mul a4, a2, a3
  xor a6, a4, a5
  sll a0, a6, a7
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
  .word 1001
  .word 2654436770
  .word 1013905243
  .word 3668341012
  .word 2027809485
  .word 387277958
  .word 3041713727
  .word 1401182200
  .word 4055617969
  .word 2415086442
  .word 774554915
  .word 3428990684
  .word 1788459157
  .word 147927630
  .word 2802363399
  .word 1161831872
  .word 3816267641
  .word 2175736114
  .word 535204587
  .word 3189640356
  .word 1549108829
  .word 4203544598
  .word 2563013071
  .word 922481544
  .word 3576917313
  .word 1936385786
  .word 295854259
  .word 2950290028
  .word 1309758501
  .word 3964194270
  .word 2323662743
  .word 683131216
  .word 3337566985
  .word 1697035458
  .word 56503931
  .word 2710939700
  .word 1070408173
  .word 3724843942
  .word 2084312415
  .word 443780888
  .word 3098216657
  .word 1457685130
  .word 4112120899
  .word 2471589372
  .word 831057845
  .word 3485493614
  .word 1844962087
  .word 204430560
  .word 2858866329
  .word 1218334802
  .word 3872770571
  .word 2232239044
  .word 591707517
  .word 3246143286
  .word 1605611759
  .word 4260047528
  .word 2619516001
  .word 978984474
  .word 3633420243
  .word 1992888716
  .word 352357189
  .word 3006792958
  .word 1366261431
  .word 4020697200
.section .bss
.balign 4
snapshot: .space 32
