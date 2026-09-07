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
  li t6, 1024
.Lloop0:
  add a2, a0, a1
  xor a4, a2, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 1024
.Lloop1:
  or a6, a4, a5
  sll a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 1234567894
  .word 3889003663
  .word 2248472136
  .word 607940609
  .word 3262376378
  .word 1621844851
  .word 4276280620
  .word 2635749093
  .word 995217566
  .word 3649653335
  .word 2009121808
  .word 368590281
  .word 3023026050
  .word 1382494523
  .word 4036930292
  .word 2396398765
  .word 755867238
  .word 3410303007
  .word 1769771480
  .word 129239953
  .word 2783675722
  .word 1143144195
  .word 3797579964
  .word 2157048437
  .word 516516910
  .word 3170952679
  .word 1530421152
  .word 4184856921
  .word 2544325394
  .word 903793867
  .word 3558229636
  .word 1917698109
  .word 277166582
  .word 2931602351
  .word 1291070824
  .word 3945506593
  .word 2304975066
  .word 664443539
  .word 3318879308
  .word 1678347781
  .word 37816254
  .word 2692252023
  .word 1051720496
  .word 3706156265
  .word 2065624738
  .word 425093211
  .word 3079528980
  .word 1438997453
  .word 4093433222
  .word 2452901695
  .word 812370168
  .word 3466805937
  .word 1826274410
  .word 185742883
  .word 2840178652
  .word 1199647125
  .word 3854082894
  .word 2213551367
  .word 573019840
  .word 3227455609
  .word 1586924082
  .word 4241359851
  .word 2600828324
  .word 960296797
.section .bss
.balign 4
snapshot: .space 32
