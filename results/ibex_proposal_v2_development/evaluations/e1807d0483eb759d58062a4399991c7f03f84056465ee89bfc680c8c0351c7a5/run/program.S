.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 0
  li a2, 228389991
  li a3, 0
  li a4, 0
  li a5, 31
  li a6, 4294967295
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 92493
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 465
.Lloop0:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a2, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 132371
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 188
.Lloop1:
  bnez a1, .Lskip1_0
  mv a6, a5
.Lskip1_0:
  bnez a7, .Lskip1_1
  mv a4, a6
.Lskip1_1:
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
  .word 2058412725
  .word 417881198
  .word 3072316967
  .word 1431785440
  .word 4086221209
  .word 2445689682
  .word 805158155
  .word 3459593924
  .word 1819062397
  .word 178530870
  .word 2832966639
  .word 1192435112
  .word 3846870881
  .word 2206339354
  .word 565807827
  .word 3220243596
  .word 1579712069
  .word 4234147838
  .word 2593616311
  .word 953084784
  .word 3607520553
  .word 1966989026
  .word 326457499
  .word 2980893268
  .word 1340361741
  .word 3994797510
  .word 2354265983
  .word 713734456
  .word 3368170225
  .word 1727638698
  .word 87107171
  .word 2741542940
  .word 1101011413
  .word 3755447182
  .word 2114915655
  .word 474384128
  .word 3128819897
  .word 1488288370
  .word 4142724139
  .word 2502192612
  .word 861661085
  .word 3516096854
  .word 1875565327
  .word 235033800
  .word 2889469569
  .word 1248938042
  .word 3903373811
  .word 2262842284
  .word 622310757
  .word 3276746526
  .word 1636214999
  .word 4290650768
  .word 2650119241
  .word 1009587714
  .word 3664023483
  .word 2023491956
  .word 382960429
  .word 3037396198
  .word 1396864671
  .word 4051300440
  .word 2410768913
  .word 770237386
  .word 3424673155
  .word 1784141628
.section .bss
.balign 4
snapshot: .space 32
