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
  add a7, a0, a1
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
  .word 1002
  .word 2654436771
  .word 1013905244
  .word 3668341013
  .word 2027809486
  .word 387277959
  .word 3041713728
  .word 1401182201
  .word 4055617970
  .word 2415086443
  .word 774554916
  .word 3428990685
  .word 1788459158
  .word 147927631
  .word 2802363400
  .word 1161831873
  .word 3816267642
  .word 2175736115
  .word 535204588
  .word 3189640357
  .word 1549108830
  .word 4203544599
  .word 2563013072
  .word 922481545
  .word 3576917314
  .word 1936385787
  .word 295854260
  .word 2950290029
  .word 1309758502
  .word 3964194271
  .word 2323662744
  .word 683131217
  .word 3337566986
  .word 1697035459
  .word 56503932
  .word 2710939701
  .word 1070408174
  .word 3724843943
  .word 2084312416
  .word 443780889
  .word 3098216658
  .word 1457685131
  .word 4112120900
  .word 2471589373
  .word 831057846
  .word 3485493615
  .word 1844962088
  .word 204430561
  .word 2858866330
  .word 1218334803
  .word 3872770572
  .word 2232239045
  .word 591707518
  .word 3246143287
  .word 1605611760
  .word 4260047529
  .word 2619516002
  .word 978984475
  .word 3633420244
  .word 1992888717
  .word 352357190
  .word 3006792959
  .word 1366261432
  .word 4020697201
.section .bss
.balign 4
snapshot: .space 32
