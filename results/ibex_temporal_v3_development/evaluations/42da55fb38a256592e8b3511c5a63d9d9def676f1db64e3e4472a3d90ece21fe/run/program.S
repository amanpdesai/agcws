.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
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
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
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
  .word 1357924680
  .word 4012360449
  .word 2371828922
  .word 731297395
  .word 3385733164
  .word 1745201637
  .word 104670110
  .word 2759105879
  .word 1118574352
  .word 3773010121
  .word 2132478594
  .word 491947067
  .word 3146382836
  .word 1505851309
  .word 4160287078
  .word 2519755551
  .word 879224024
  .word 3533659793
  .word 1893128266
  .word 252596739
  .word 2907032508
  .word 1266500981
  .word 3920936750
  .word 2280405223
  .word 639873696
  .word 3294309465
  .word 1653777938
  .word 13246411
  .word 2667682180
  .word 1027150653
  .word 3681586422
  .word 2041054895
  .word 400523368
  .word 3054959137
  .word 1414427610
  .word 4068863379
  .word 2428331852
  .word 787800325
  .word 3442236094
  .word 1801704567
  .word 161173040
  .word 2815608809
  .word 1175077282
  .word 3829513051
  .word 2188981524
  .word 548449997
  .word 3202885766
  .word 1562354239
  .word 4216790008
  .word 2576258481
  .word 935726954
  .word 3590162723
  .word 1949631196
  .word 309099669
  .word 2963535438
  .word 1323003911
  .word 3977439680
  .word 2336908153
  .word 696376626
  .word 3350812395
  .word 1710280868
  .word 69749341
  .word 2724185110
  .word 1083653583
.section .bss
.balign 4
snapshot: .space 32
