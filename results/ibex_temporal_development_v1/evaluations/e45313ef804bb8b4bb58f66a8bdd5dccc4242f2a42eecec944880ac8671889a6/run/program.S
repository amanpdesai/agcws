.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 3948686884
  li a1, 17
  li a2, 3654569246
  li a3, 1074478309
  li a4, 4294967295
  li a5, 0
  li a6, 4294967295
  li a7, 680922082
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 114404
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 1240
.Lloop0:
  mul a7, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 164524
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 714
.Lloop1:
  divu a4, a4, a7
  divu a7, a3, a1
  divu a4, a5, a4
  divu a2, a7, a2
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
  .word 993862420
  .word 3648298189
  .word 2007766662
  .word 367235135
  .word 3021670904
  .word 1381139377
  .word 4035575146
  .word 2395043619
  .word 754512092
  .word 3408947861
  .word 1768416334
  .word 127884807
  .word 2782320576
  .word 1141789049
  .word 3796224818
  .word 2155693291
  .word 515161764
  .word 3169597533
  .word 1529066006
  .word 4183501775
  .word 2542970248
  .word 902438721
  .word 3556874490
  .word 1916342963
  .word 275811436
  .word 2930247205
  .word 1289715678
  .word 3944151447
  .word 2303619920
  .word 663088393
  .word 3317524162
  .word 1676992635
  .word 36461108
  .word 2690896877
  .word 1050365350
  .word 3704801119
  .word 2064269592
  .word 423738065
  .word 3078173834
  .word 1437642307
  .word 4092078076
  .word 2451546549
  .word 811015022
  .word 3465450791
  .word 1824919264
  .word 184387737
  .word 2838823506
  .word 1198291979
  .word 3852727748
  .word 2212196221
  .word 571664694
  .word 3226100463
  .word 1585568936
  .word 4240004705
  .word 2599473178
  .word 958941651
  .word 3613377420
  .word 1972845893
  .word 332314366
  .word 2986750135
  .word 1346218608
  .word 4000654377
  .word 2360122850
  .word 719591323
.section .bss
.balign 4
snapshot: .space 32
