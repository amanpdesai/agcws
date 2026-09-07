.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  add a0, a0, a1
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 75000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a2, a2, a0
  divu a4, a4, a0
  divu a6, a6, a0
  divu a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a0, a0, a1
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
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
  .word 22222
  .word 2654457991
  .word 1013926464
  .word 3668362233
  .word 2027830706
  .word 387299179
  .word 3041734948
  .word 1401203421
  .word 4055639190
  .word 2415107663
  .word 774576136
  .word 3429011905
  .word 1788480378
  .word 147948851
  .word 2802384620
  .word 1161853093
  .word 3816288862
  .word 2175757335
  .word 535225808
  .word 3189661577
  .word 1549130050
  .word 4203565819
  .word 2563034292
  .word 922502765
  .word 3576938534
  .word 1936407007
  .word 295875480
  .word 2950311249
  .word 1309779722
  .word 3964215491
  .word 2323683964
  .word 683152437
  .word 3337588206
  .word 1697056679
  .word 56525152
  .word 2710960921
  .word 1070429394
  .word 3724865163
  .word 2084333636
  .word 443802109
  .word 3098237878
  .word 1457706351
  .word 4112142120
  .word 2471610593
  .word 831079066
  .word 3485514835
  .word 1844983308
  .word 204451781
  .word 2858887550
  .word 1218356023
  .word 3872791792
  .word 2232260265
  .word 591728738
  .word 3246164507
  .word 1605632980
  .word 4260068749
  .word 2619537222
  .word 979005695
  .word 3633441464
  .word 1992909937
  .word 352378410
  .word 3006814179
  .word 1366282652
  .word 4020718421
.section .bss
.balign 4
snapshot: .space 32
