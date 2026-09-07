.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 2195220240
  li a1, 1
  li a2, 31
  li a3, 4294967295
  li a4, 4294967295
  li a5, 31
  li a6, 31
  li a7, 951586712
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 25951
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 112
.Lloop0:
  xor a2, a7, a0
  sll a4, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 26934
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 124
.Lloop1:
  bnez a2, .Lskip1_0
  mv a6, a0
.Lskip1_0:
  bnez a3, .Lskip1_1
  mv a4, a0
.Lskip1_1:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 37518
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 79
.Lloop2:
  divu a2, a3, a1
  mul a5, a0, a0
  divu a3, a2, a1
  divu a2, a0, a0
  xor a2, a2, a1
  and a5, a3, a0
  srl a7, a2, a0
  mul a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 53111
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 48
.Lloop3:
  add a1, a4, a2
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 85810
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 114
.Lloop4:
  divu a0, a5, a1
  divu a5, a5, a0
  divu a2, a4, a5
  divu a5, a6, a6
  divu a3, a2, a5
  divu a7, a3, a2
  divu a1, a6, a2
  divu a3, a7, a5
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 145622
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 584
.Lloop5:
  divu a2, a7, a3
  divu a5, a0, a2
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 160975
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 108
.Lloop6:
  mul a6, a0, a1
  mul a3, a3, a0
  mul a4, a2, a0
  mul a6, a1, a0
  mul a7, a5, a0
  mul a6, a1, a1
  mul a3, a3, a1
  mul a5, a0, a1
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
  .word 2119126912
  .word 478595385
  .word 3133031154
  .word 1492499627
  .word 4146935396
  .word 2506403869
  .word 865872342
  .word 3520308111
  .word 1879776584
  .word 239245057
  .word 2893680826
  .word 1253149299
  .word 3907585068
  .word 2267053541
  .word 626522014
  .word 3280957783
  .word 1640426256
  .word 4294862025
  .word 2654330498
  .word 1013798971
  .word 3668234740
  .word 2027703213
  .word 387171686
  .word 3041607455
  .word 1401075928
  .word 4055511697
  .word 2414980170
  .word 774448643
  .word 3428884412
  .word 1788352885
  .word 147821358
  .word 2802257127
  .word 1161725600
  .word 3816161369
  .word 2175629842
  .word 535098315
  .word 3189534084
  .word 1549002557
  .word 4203438326
  .word 2562906799
  .word 922375272
  .word 3576811041
  .word 1936279514
  .word 295747987
  .word 2950183756
  .word 1309652229
  .word 3964087998
  .word 2323556471
  .word 683024944
  .word 3337460713
  .word 1696929186
  .word 56397659
  .word 2710833428
  .word 1070301901
  .word 3724737670
  .word 2084206143
  .word 443674616
  .word 3098110385
  .word 1457578858
  .word 4112014627
  .word 2471483100
  .word 830951573
  .word 3485387342
  .word 1844855815
.section .bss
.balign 4
snapshot: .space 32
