.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 3391942914
  li a2, 4294967295
  li a3, 1553030968
  li a4, 17
  li a5, 17
  li a6, 4294967295
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 1000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 266
.Lloop0:
  divu a7, a5, a0
  divu a5, a6, a1
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a7, a5, a0
  divu a5, a6, a1
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 250
.Lloop1:
  bnez a3, .Lskip1_0
  mv a2, a5
.Lskip1_0:
  bnez a2, .Lskip1_1
  mv a1, a1
.Lskip1_1:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 60000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 250
.Lloop2:
  and a2, a5, a0
  or a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 90000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 250
.Lloop3:
  bnez a0, .Lskip3_0
  mv a0, a1
.Lskip3_0:
  bnez a6, .Lskip3_1
  mv a3, a4
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 120000
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 299
.Lloop4:
  divu a3, a4, a0
  divu a3, a5, a1
  divu a4, a0, a1
  divu a3, a2, a0
  divu a6, a7, a2
  divu a3, a7, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
  divu a3, a4, a0
  divu a3, a5, a1
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
  .word 3329196734
  .word 1688665207
  .word 48133680
  .word 2702569449
  .word 1062037922
  .word 3716473691
  .word 2075942164
  .word 435410637
  .word 3089846406
  .word 1449314879
  .word 4103750648
  .word 2463219121
  .word 822687594
  .word 3477123363
  .word 1836591836
  .word 196060309
  .word 2850496078
  .word 1209964551
  .word 3864400320
  .word 2223868793
  .word 583337266
  .word 3237773035
  .word 1597241508
  .word 4251677277
  .word 2611145750
  .word 970614223
  .word 3625049992
  .word 1984518465
  .word 343986938
  .word 2998422707
  .word 1357891180
  .word 4012326949
  .word 2371795422
  .word 731263895
  .word 3385699664
  .word 1745168137
  .word 104636610
  .word 2759072379
  .word 1118540852
  .word 3772976621
  .word 2132445094
  .word 491913567
  .word 3146349336
  .word 1505817809
  .word 4160253578
  .word 2519722051
  .word 879190524
  .word 3533626293
  .word 1893094766
  .word 252563239
  .word 2906999008
  .word 1266467481
  .word 3920903250
  .word 2280371723
  .word 639840196
  .word 3294275965
  .word 1653744438
  .word 13212911
  .word 2667648680
  .word 1027117153
  .word 3681552922
  .word 2041021395
  .word 400489868
  .word 3054925637
.section .bss
.balign 4
snapshot: .space 32
