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
  li t6, 512
.Lloop0:
  add a1, a0, a1
  xor a2, a1, a2
  mul a3, a2, a3
  sll a4, a3, a4
  srl a5, a4, a5
  and a6, a5, a6
  or a7, a6, a7
  add a0, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 1234567893
  .word 3889003662
  .word 2248472135
  .word 607940608
  .word 3262376377
  .word 1621844850
  .word 4276280619
  .word 2635749092
  .word 995217565
  .word 3649653334
  .word 2009121807
  .word 368590280
  .word 3023026049
  .word 1382494522
  .word 4036930291
  .word 2396398764
  .word 755867237
  .word 3410303006
  .word 1769771479
  .word 129239952
  .word 2783675721
  .word 1143144194
  .word 3797579963
  .word 2157048436
  .word 516516909
  .word 3170952678
  .word 1530421151
  .word 4184856920
  .word 2544325393
  .word 903793866
  .word 3558229635
  .word 1917698108
  .word 277166581
  .word 2931602350
  .word 1291070823
  .word 3945506592
  .word 2304975065
  .word 664443538
  .word 3318879307
  .word 1678347780
  .word 37816253
  .word 2692252022
  .word 1051720495
  .word 3706156264
  .word 2065624737
  .word 425093210
  .word 3079528979
  .word 1438997452
  .word 4093433221
  .word 2452901694
  .word 812370167
  .word 3466805936
  .word 1826274409
  .word 185742882
  .word 2840178651
  .word 1199647124
  .word 3854082893
  .word 2213551366
  .word 573019839
  .word 3227455608
  .word 1586924081
  .word 4241359850
  .word 2600828323
  .word 960296796
.section .bss
.balign 4
snapshot: .space 32
