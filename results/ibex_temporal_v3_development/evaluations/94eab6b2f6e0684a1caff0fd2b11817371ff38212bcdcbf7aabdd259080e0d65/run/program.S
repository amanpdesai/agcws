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
  divu a2, a0, a0
  divu a4, a0, a0
  divu a6, a0, a0
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
  .word 445566
  .word 2654881335
  .word 1014349808
  .word 3668785577
  .word 2028254050
  .word 387722523
  .word 3042158292
  .word 1401626765
  .word 4056062534
  .word 2415531007
  .word 774999480
  .word 3429435249
  .word 1788903722
  .word 148372195
  .word 2802807964
  .word 1162276437
  .word 3816712206
  .word 2176180679
  .word 535649152
  .word 3190084921
  .word 1549553394
  .word 4203989163
  .word 2563457636
  .word 922926109
  .word 3577361878
  .word 1936830351
  .word 296298824
  .word 2950734593
  .word 1310203066
  .word 3964638835
  .word 2324107308
  .word 683575781
  .word 3338011550
  .word 1697480023
  .word 56948496
  .word 2711384265
  .word 1070852738
  .word 3725288507
  .word 2084756980
  .word 444225453
  .word 3098661222
  .word 1458129695
  .word 4112565464
  .word 2472033937
  .word 831502410
  .word 3485938179
  .word 1845406652
  .word 204875125
  .word 2859310894
  .word 1218779367
  .word 3873215136
  .word 2232683609
  .word 592152082
  .word 3246587851
  .word 1606056324
  .word 4260492093
  .word 2619960566
  .word 979429039
  .word 3633864808
  .word 1993333281
  .word 352801754
  .word 3007237523
  .word 1366705996
  .word 4021141765
.section .bss
.balign 4
snapshot: .space 32
