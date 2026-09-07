.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 4032293290
  li a3, 0
  li a4, 0
  li a5, 1
  li a6, 3024829961
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 90063
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 299
.Lloop0:
  bnez a5, .Lskip0_0
  mv a3, a1
.Lskip0_0:
  bnez a6, .Lskip0_1
  mv a3, a1
.Lskip0_1:
  bnez a5, .Lskip0_2
  mv a6, a0
.Lskip0_2:
  bnez a4, .Lskip0_3
  mv a7, a1
.Lskip0_3:
  bnez a3, .Lskip0_4
  mv a6, a1
.Lskip0_4:
  bnez a1, .Lskip0_5
  mv a7, a0
.Lskip0_5:
  bnez a0, .Lskip0_6
  mv a5, a1
.Lskip0_6:
  bnez a1, .Lskip0_7
  mv a2, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 155362
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 340
.Lloop1:
  bnez a3, .Lskip1_0
  mv a4, a0
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a6, a2
.Lskip1_1:
  bnez a7, .Lskip1_2
  mv a3, a2
.Lskip1_2:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  bnez a3, .Lskip1_4
  mv a7, a1
.Lskip1_4:
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a3, .Ltail_skip1_0
  mv a4, a0
.Ltail_skip1_0:
  bnez a7, .Ltail_skip1_1
  mv a6, a2
.Ltail_skip1_1:
  bnez a7, .Ltail_skip1_2
  mv a3, a2
.Ltail_skip1_2:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
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
  .word 2496061276
  .word 855529749
  .word 3509965518
  .word 1869433991
  .word 228902464
  .word 2883338233
  .word 1242806706
  .word 3897242475
  .word 2256710948
  .word 616179421
  .word 3270615190
  .word 1630083663
  .word 4284519432
  .word 2643987905
  .word 1003456378
  .word 3657892147
  .word 2017360620
  .word 376829093
  .word 3031264862
  .word 1390733335
  .word 4045169104
  .word 2404637577
  .word 764106050
  .word 3418541819
  .word 1778010292
  .word 137478765
  .word 2791914534
  .word 1151383007
  .word 3805818776
  .word 2165287249
  .word 524755722
  .word 3179191491
  .word 1538659964
  .word 4193095733
  .word 2552564206
  .word 912032679
  .word 3566468448
  .word 1925936921
  .word 285405394
  .word 2939841163
  .word 1299309636
  .word 3953745405
  .word 2313213878
  .word 672682351
  .word 3327118120
  .word 1686586593
  .word 46055066
  .word 2700490835
  .word 1059959308
  .word 3714395077
  .word 2073863550
  .word 433332023
  .word 3087767792
  .word 1447236265
  .word 4101672034
  .word 2461140507
  .word 820608980
  .word 3475044749
  .word 1834513222
  .word 193981695
  .word 2848417464
  .word 1207885937
  .word 3862321706
  .word 2221790179
.section .bss
.balign 4
snapshot: .space 32
