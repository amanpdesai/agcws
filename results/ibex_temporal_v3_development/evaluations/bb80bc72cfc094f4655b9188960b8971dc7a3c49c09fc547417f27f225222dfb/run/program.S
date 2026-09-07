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
  li t6, 192
.Lloop0:
  bnez a0, .Lskip0_0
  mv a0, a1
.Lskip0_0:
  bnez a1, .Lskip0_1
  mv a1, a2
.Lskip0_1:
  bnez a2, .Lskip0_2
  mv a2, a3
.Lskip0_2:
  bnez a3, .Lskip0_3
  mv a3, a4
.Lskip0_3:
  bnez a4, .Lskip0_4
  mv a4, a5
.Lskip0_4:
  bnez a5, .Lskip0_5
  mv a5, a6
.Lskip0_5:
  bnez a6, .Lskip0_6
  mv a6, a7
.Lskip0_6:
  bnez a7, .Lskip0_7
  mv a7, a0
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 320
.Lloop1:
  add a0, a0, a1
  xor a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  sll a4, a4, a5
  srl a5, a5, a6
  mul a6, a6, a7
  add a7, a7, a0
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
  .word 3344556677
  .word 1704025150
  .word 63493623
  .word 2717929392
  .word 1077397865
  .word 3731833634
  .word 2091302107
  .word 450770580
  .word 3105206349
  .word 1464674822
  .word 4119110591
  .word 2478579064
  .word 838047537
  .word 3492483306
  .word 1851951779
  .word 211420252
  .word 2865856021
  .word 1225324494
  .word 3879760263
  .word 2239228736
  .word 598697209
  .word 3253132978
  .word 1612601451
  .word 4267037220
  .word 2626505693
  .word 985974166
  .word 3640409935
  .word 1999878408
  .word 359346881
  .word 3013782650
  .word 1373251123
  .word 4027686892
  .word 2387155365
  .word 746623838
  .word 3401059607
  .word 1760528080
  .word 119996553
  .word 2774432322
  .word 1133900795
  .word 3788336564
  .word 2147805037
  .word 507273510
  .word 3161709279
  .word 1521177752
  .word 4175613521
  .word 2535081994
  .word 894550467
  .word 3548986236
  .word 1908454709
  .word 267923182
  .word 2922358951
  .word 1281827424
  .word 3936263193
  .word 2295731666
  .word 655200139
  .word 3309635908
  .word 1669104381
  .word 28572854
  .word 2683008623
  .word 1042477096
  .word 3696912865
  .word 2056381338
  .word 415849811
  .word 3070285580
.section .bss
.balign 4
snapshot: .space 32
