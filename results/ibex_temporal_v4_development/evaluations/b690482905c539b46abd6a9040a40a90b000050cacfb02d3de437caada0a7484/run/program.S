.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4294967295
  li a2, 17
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 31
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 28390
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 207
.Lloop0:
  bnez a4, .Lskip0_0
  mv a2, a6
.Lskip0_0:
  bnez a2, .Lskip0_1
  mv a1, a3
.Lskip0_1:
  bnez a3, .Lskip0_2
  mv a6, a0
.Lskip0_2:
  bnez a5, .Lskip0_3
  mv a2, a2
.Lskip0_3:
  bnez a0, .Lskip0_4
  mv a3, a5
.Lskip0_4:
  bnez a5, .Lskip0_5
  mv a3, a6
.Lskip0_5:
  bnez a7, .Lskip0_6
  mv a3, a0
.Lskip0_6:
  bnez a0, .Lskip0_7
  mv a7, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 50211
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1344
.Lloop1:
  divu a0, a2, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 126554
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 274
.Lloop2:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
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
  .word 367617083
  .word 3022052852
  .word 1381521325
  .word 4035957094
  .word 2395425567
  .word 754894040
  .word 3409329809
  .word 1768798282
  .word 128266755
  .word 2782702524
  .word 1142170997
  .word 3796606766
  .word 2156075239
  .word 515543712
  .word 3169979481
  .word 1529447954
  .word 4183883723
  .word 2543352196
  .word 902820669
  .word 3557256438
  .word 1916724911
  .word 276193384
  .word 2930629153
  .word 1290097626
  .word 3944533395
  .word 2304001868
  .word 663470341
  .word 3317906110
  .word 1677374583
  .word 36843056
  .word 2691278825
  .word 1050747298
  .word 3705183067
  .word 2064651540
  .word 424120013
  .word 3078555782
  .word 1438024255
  .word 4092460024
  .word 2451928497
  .word 811396970
  .word 3465832739
  .word 1825301212
  .word 184769685
  .word 2839205454
  .word 1198673927
  .word 3853109696
  .word 2212578169
  .word 572046642
  .word 3226482411
  .word 1585950884
  .word 4240386653
  .word 2599855126
  .word 959323599
  .word 3613759368
  .word 1973227841
  .word 332696314
  .word 2987132083
  .word 1346600556
  .word 4001036325
  .word 2360504798
  .word 719973271
  .word 3374409040
  .word 1733877513
  .word 93345986
.section .bss
.balign 4
snapshot: .space 32
