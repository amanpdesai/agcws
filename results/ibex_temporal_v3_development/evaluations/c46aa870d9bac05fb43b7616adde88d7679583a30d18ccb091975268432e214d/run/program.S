.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
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
  divu a0, a0, a1
  divu a1, a1, a1
  divu a2, a2, a1
  divu a3, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 512
.Lloop1:
  divu a4, a4, a1
  divu a5, a5, a1
  divu a6, a6, a1
  divu a7, a7, a1
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
  .word 67890
  .word 2654503659
  .word 1013972132
  .word 3668407901
  .word 2027876374
  .word 387344847
  .word 3041780616
  .word 1401249089
  .word 4055684858
  .word 2415153331
  .word 774621804
  .word 3429057573
  .word 1788526046
  .word 147994519
  .word 2802430288
  .word 1161898761
  .word 3816334530
  .word 2175803003
  .word 535271476
  .word 3189707245
  .word 1549175718
  .word 4203611487
  .word 2563079960
  .word 922548433
  .word 3576984202
  .word 1936452675
  .word 295921148
  .word 2950356917
  .word 1309825390
  .word 3964261159
  .word 2323729632
  .word 683198105
  .word 3337633874
  .word 1697102347
  .word 56570820
  .word 2711006589
  .word 1070475062
  .word 3724910831
  .word 2084379304
  .word 443847777
  .word 3098283546
  .word 1457752019
  .word 4112187788
  .word 2471656261
  .word 831124734
  .word 3485560503
  .word 1845028976
  .word 204497449
  .word 2858933218
  .word 1218401691
  .word 3872837460
  .word 2232305933
  .word 591774406
  .word 3246210175
  .word 1605678648
  .word 4260114417
  .word 2619582890
  .word 979051363
  .word 3633487132
  .word 1992955605
  .word 352424078
  .word 3006859847
  .word 1366328320
  .word 4020764089
.section .bss
.balign 4
snapshot: .space 32
