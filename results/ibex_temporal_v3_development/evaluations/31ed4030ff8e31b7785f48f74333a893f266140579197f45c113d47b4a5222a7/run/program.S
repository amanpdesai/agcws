.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 341
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  sll a2, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 341
.Lloop1:
  mul a3, a3, a4
  or a4, a4, a5
  srl a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  mul a3, a3, a4
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 341
.Lloop2:
  divu a6, a6, a7
  bnez a0, .Lskip2_1
  mv a7, a1
.Lskip2_1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a6, a6, a7
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 341
.Lloop3:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  add a4, a4, a5
  mul a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
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
  .word 1003
  .word 2654436772
  .word 1013905245
  .word 3668341014
  .word 2027809487
  .word 387277960
  .word 3041713729
  .word 1401182202
  .word 4055617971
  .word 2415086444
  .word 774554917
  .word 3428990686
  .word 1788459159
  .word 147927632
  .word 2802363401
  .word 1161831874
  .word 3816267643
  .word 2175736116
  .word 535204589
  .word 3189640358
  .word 1549108831
  .word 4203544600
  .word 2563013073
  .word 922481546
  .word 3576917315
  .word 1936385788
  .word 295854261
  .word 2950290030
  .word 1309758503
  .word 3964194272
  .word 2323662745
  .word 683131218
  .word 3337566987
  .word 1697035460
  .word 56503933
  .word 2710939702
  .word 1070408175
  .word 3724843944
  .word 2084312417
  .word 443780890
  .word 3098216659
  .word 1457685132
  .word 4112120901
  .word 2471589374
  .word 831057847
  .word 3485493616
  .word 1844962089
  .word 204430562
  .word 2858866331
  .word 1218334804
  .word 3872770573
  .word 2232239046
  .word 591707519
  .word 3246143288
  .word 1605611761
  .word 4260047530
  .word 2619516003
  .word 978984476
  .word 3633420245
  .word 1992888718
  .word 352357191
  .word 3006792960
  .word 1366261433
  .word 4020697202
.section .bss
.balign 4
snapshot: .space 32
