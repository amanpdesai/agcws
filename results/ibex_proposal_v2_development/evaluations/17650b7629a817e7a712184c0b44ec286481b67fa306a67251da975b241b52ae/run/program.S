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
  li s9, 1000
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 275
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  and a4, a4, a5
  or a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 30000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 250
.Lloop1:
  sll a3, a1, a0
  srl a5, a3, a2
  mul a7, a5, a4
  bnez a7, .Lskip1_3
  mv a1, a6
.Lskip1_3:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 70000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 225
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 182
.Lloop3:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
  divu a3, a5, a1
  divu a7, a5, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  divu a7, a1, a0
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
  .word 1234567892
  .word 3889003661
  .word 2248472134
  .word 607940607
  .word 3262376376
  .word 1621844849
  .word 4276280618
  .word 2635749091
  .word 995217564
  .word 3649653333
  .word 2009121806
  .word 368590279
  .word 3023026048
  .word 1382494521
  .word 4036930290
  .word 2396398763
  .word 755867236
  .word 3410303005
  .word 1769771478
  .word 129239951
  .word 2783675720
  .word 1143144193
  .word 3797579962
  .word 2157048435
  .word 516516908
  .word 3170952677
  .word 1530421150
  .word 4184856919
  .word 2544325392
  .word 903793865
  .word 3558229634
  .word 1917698107
  .word 277166580
  .word 2931602349
  .word 1291070822
  .word 3945506591
  .word 2304975064
  .word 664443537
  .word 3318879306
  .word 1678347779
  .word 37816252
  .word 2692252021
  .word 1051720494
  .word 3706156263
  .word 2065624736
  .word 425093209
  .word 3079528978
  .word 1438997451
  .word 4093433220
  .word 2452901693
  .word 812370166
  .word 3466805935
  .word 1826274408
  .word 185742881
  .word 2840178650
  .word 1199647123
  .word 3854082892
  .word 2213551365
  .word 573019838
  .word 3227455607
  .word 1586924080
  .word 4241359849
  .word 2600828322
  .word 960296795
.section .bss
.balign 4
snapshot: .space 32
