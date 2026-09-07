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
  li t6, 128
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
  divu a4, a4, a1
  divu a5, a5, a1
  divu a6, a6, a1
  divu a7, a7, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 0
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 128
.Lloop4:
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 0
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 128
.Lloop5:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 3341289844
  .word 1700758317
  .word 60226790
  .word 2714662559
  .word 1074131032
  .word 3728566801
  .word 2088035274
  .word 447503747
  .word 3101939516
  .word 1461407989
  .word 4115843758
  .word 2475312231
  .word 834780704
  .word 3489216473
  .word 1848684946
  .word 208153419
  .word 2862589188
  .word 1222057661
  .word 3876493430
  .word 2235961903
  .word 595430376
  .word 3249866145
  .word 1609334618
  .word 4263770387
  .word 2623238860
  .word 982707333
  .word 3637143102
  .word 1996611575
  .word 356080048
  .word 3010515817
  .word 1369984290
  .word 4024420059
  .word 2383888532
  .word 743357005
  .word 3397792774
  .word 1757261247
  .word 116729720
  .word 2771165489
  .word 1130633962
  .word 3785069731
  .word 2144538204
  .word 504006677
  .word 3158442446
  .word 1517910919
  .word 4172346688
  .word 2531815161
  .word 891283634
  .word 3545719403
  .word 1905187876
  .word 264656349
  .word 2919092118
  .word 1278560591
  .word 3932996360
  .word 2292464833
  .word 651933306
  .word 3306369075
  .word 1665837548
  .word 25306021
  .word 2679741790
  .word 1039210263
  .word 3693646032
  .word 2053114505
  .word 412582978
  .word 3067018747
.section .bss
.balign 4
snapshot: .space 32
