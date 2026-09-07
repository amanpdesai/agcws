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
  li t6, 256
.Lloop0:
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a7, a0, a1
  add a5, a2, a3
  add a3, a4, a5
  add a1, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
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
  .word 3341289846
  .word 1700758319
  .word 60226792
  .word 2714662561
  .word 1074131034
  .word 3728566803
  .word 2088035276
  .word 447503749
  .word 3101939518
  .word 1461407991
  .word 4115843760
  .word 2475312233
  .word 834780706
  .word 3489216475
  .word 1848684948
  .word 208153421
  .word 2862589190
  .word 1222057663
  .word 3876493432
  .word 2235961905
  .word 595430378
  .word 3249866147
  .word 1609334620
  .word 4263770389
  .word 2623238862
  .word 982707335
  .word 3637143104
  .word 1996611577
  .word 356080050
  .word 3010515819
  .word 1369984292
  .word 4024420061
  .word 2383888534
  .word 743357007
  .word 3397792776
  .word 1757261249
  .word 116729722
  .word 2771165491
  .word 1130633964
  .word 3785069733
  .word 2144538206
  .word 504006679
  .word 3158442448
  .word 1517910921
  .word 4172346690
  .word 2531815163
  .word 891283636
  .word 3545719405
  .word 1905187878
  .word 264656351
  .word 2919092120
  .word 1278560593
  .word 3932996362
  .word 2292464835
  .word 651933308
  .word 3306369077
  .word 1665837550
  .word 25306023
  .word 2679741792
  .word 1039210265
  .word 3693646034
  .word 2053114507
  .word 412582980
  .word 3067018749
.section .bss
.balign 4
snapshot: .space 32
