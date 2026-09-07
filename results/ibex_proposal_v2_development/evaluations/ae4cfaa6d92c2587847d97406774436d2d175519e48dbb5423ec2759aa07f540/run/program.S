.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1
  li a2, 4294967295
  li a3, 0
  li a4, 31
  li a5, 3150259334
  li a6, 4294967295
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 74137
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 224
.Lloop0:
  divu a5, a5, a0
  divu a2, a4, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 86682
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 218
.Lloop1:
  and a5, a5, a4
  and a2, a2, a0
  add a3, a2, a1
  and a0, a4, a6
  srl a3, a7, a2
  and a6, a6, a2
  and a7, a5, a2
  sll a3, a7, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 131018
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 476
.Lloop2:
  divu a7, a7, a0
  divu a4, a1, a1
  divu a4, a7, a0
  divu a2, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 1390220120
  .word 4044655889
  .word 2404124362
  .word 763592835
  .word 3418028604
  .word 1777497077
  .word 136965550
  .word 2791401319
  .word 1150869792
  .word 3805305561
  .word 2164774034
  .word 524242507
  .word 3178678276
  .word 1538146749
  .word 4192582518
  .word 2552050991
  .word 911519464
  .word 3565955233
  .word 1925423706
  .word 284892179
  .word 2939327948
  .word 1298796421
  .word 3953232190
  .word 2312700663
  .word 672169136
  .word 3326604905
  .word 1686073378
  .word 45541851
  .word 2699977620
  .word 1059446093
  .word 3713881862
  .word 2073350335
  .word 432818808
  .word 3087254577
  .word 1446723050
  .word 4101158819
  .word 2460627292
  .word 820095765
  .word 3474531534
  .word 1834000007
  .word 193468480
  .word 2847904249
  .word 1207372722
  .word 3861808491
  .word 2221276964
  .word 580745437
  .word 3235181206
  .word 1594649679
  .word 4249085448
  .word 2608553921
  .word 968022394
  .word 3622458163
  .word 1981926636
  .word 341395109
  .word 2995830878
  .word 1355299351
  .word 4009735120
  .word 2369203593
  .word 728672066
  .word 3383107835
  .word 1742576308
  .word 102044781
  .word 2756480550
  .word 1115949023
.section .bss
.balign 4
snapshot: .space 32
