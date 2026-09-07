.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 0
  li a2, 17
  li a3, 842910243
  li a4, 0
  li a5, 4294967295
  li a6, 1
  li a7, 817793791
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 4566
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 28
.Lloop0:
  mul a6, a7, a0
  mul a4, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 25250
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 288
.Lloop1:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 40142
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 636
.Lloop2:
  xor a4, a7, a0
  xor a4, a4, a1
  srl a6, a0, a1
  or a7, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 75954
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 24
.Lloop3:
  and a4, a5, a1
  and a4, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 122724
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 104
.Lloop4:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 141287
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 17
.Lloop5:
  mul a5, a7, a1
  mul a6, a4, a0
  mul a3, a1, a0
  mul a4, a2, a0
  mul a3, a1, a0
  mul a5, a3, a0
  mul a3, a3, a0
  mul a7, a3, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 169121
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 608
.Lloop6:
  divu a5, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop6
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
  .word 2296699338
  .word 656167811
  .word 3310603580
  .word 1670072053
  .word 29540526
  .word 2683976295
  .word 1043444768
  .word 3697880537
  .word 2057349010
  .word 416817483
  .word 3071253252
  .word 1430721725
  .word 4085157494
  .word 2444625967
  .word 804094440
  .word 3458530209
  .word 1817998682
  .word 177467155
  .word 2831902924
  .word 1191371397
  .word 3845807166
  .word 2205275639
  .word 564744112
  .word 3219179881
  .word 1578648354
  .word 4233084123
  .word 2592552596
  .word 952021069
  .word 3606456838
  .word 1965925311
  .word 325393784
  .word 2979829553
  .word 1339298026
  .word 3993733795
  .word 2353202268
  .word 712670741
  .word 3367106510
  .word 1726574983
  .word 86043456
  .word 2740479225
  .word 1099947698
  .word 3754383467
  .word 2113851940
  .word 473320413
  .word 3127756182
  .word 1487224655
  .word 4141660424
  .word 2501128897
  .word 860597370
  .word 3515033139
  .word 1874501612
  .word 233970085
  .word 2888405854
  .word 1247874327
  .word 3902310096
  .word 2261778569
  .word 621247042
  .word 3275682811
  .word 1635151284
  .word 4289587053
  .word 2649055526
  .word 1008523999
  .word 3662959768
  .word 2022428241
.section .bss
.balign 4
snapshot: .space 32
