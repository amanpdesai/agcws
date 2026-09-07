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
  add a0, a0, a1
  add a2, a2, a3
  add a4, a4, a5
  add a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a7, a7, a6
  add a5, a5, a4
  add a3, a3, a2
  add a1, a1, a0
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
  .word 3341289839
  .word 1700758312
  .word 60226785
  .word 2714662554
  .word 1074131027
  .word 3728566796
  .word 2088035269
  .word 447503742
  .word 3101939511
  .word 1461407984
  .word 4115843753
  .word 2475312226
  .word 834780699
  .word 3489216468
  .word 1848684941
  .word 208153414
  .word 2862589183
  .word 1222057656
  .word 3876493425
  .word 2235961898
  .word 595430371
  .word 3249866140
  .word 1609334613
  .word 4263770382
  .word 2623238855
  .word 982707328
  .word 3637143097
  .word 1996611570
  .word 356080043
  .word 3010515812
  .word 1369984285
  .word 4024420054
  .word 2383888527
  .word 743357000
  .word 3397792769
  .word 1757261242
  .word 116729715
  .word 2771165484
  .word 1130633957
  .word 3785069726
  .word 2144538199
  .word 504006672
  .word 3158442441
  .word 1517910914
  .word 4172346683
  .word 2531815156
  .word 891283629
  .word 3545719398
  .word 1905187871
  .word 264656344
  .word 2919092113
  .word 1278560586
  .word 3932996355
  .word 2292464828
  .word 651933301
  .word 3306369070
  .word 1665837543
  .word 25306016
  .word 2679741785
  .word 1039210258
  .word 3693646027
  .word 2053114500
  .word 412582973
  .word 3067018742
.section .bss
.balign 4
snapshot: .space 32
