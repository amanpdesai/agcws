.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 1
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 1697746358
  li a6, 4294967295
  li a7, 509793626
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 51019
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 10
.Lloop0:
  divu a4, a4, a1
  xor a5, a4, a0
  divu a7, a3, a0
  or a2, a6, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 106271
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 210
.Lloop1:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 108621
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 64
.Lloop2:
  bnez a3, .Lskip2_0
  mv a5, a0
.Lskip2_0:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 115076
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 422
.Lloop3:
  srl a5, a2, a1
  xor a6, a6, a0
  and a2, a2, a0
  xor a2, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
.global agcws_segment_4_setup
agcws_segment_4_setup:
  li s9, 119105
  add s9, s9, s10
.global agcws_segment_4_poll
agcws_segment_4_poll:
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
.global agcws_segment_4_body
agcws_segment_4_body:
  li t6, 720
.Lloop4:
  and a5, a5, a3
  addi t6, t6, -1
  bnez t6, .Lloop4
.global agcws_segment_5_setup
agcws_segment_5_setup:
  li s9, 141680
  add s9, s9, s10
.global agcws_segment_5_poll
agcws_segment_5_poll:
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
.global agcws_segment_5_body
agcws_segment_5_body:
  li t6, 70
.Lloop5:
  or a5, a0, a0
  xor a5, a6, a0
  srl a2, a2, a0
  xor a3, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop5
.global agcws_segment_6_setup
agcws_segment_6_setup:
  li s9, 144993
  add s9, s9, s10
.global agcws_segment_6_poll
agcws_segment_6_poll:
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
.global agcws_segment_6_body
agcws_segment_6_body:
  li t6, 116
.Lloop6:
  sll a4, a5, a0
  xor a5, a6, a3
  sll a0, a6, a0
  srl a0, a7, a7
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
  .word 304638304
  .word 2959074073
  .word 1318542546
  .word 3972978315
  .word 2332446788
  .word 691915261
  .word 3346351030
  .word 1705819503
  .word 65287976
  .word 2719723745
  .word 1079192218
  .word 3733627987
  .word 2093096460
  .word 452564933
  .word 3107000702
  .word 1466469175
  .word 4120904944
  .word 2480373417
  .word 839841890
  .word 3494277659
  .word 1853746132
  .word 213214605
  .word 2867650374
  .word 1227118847
  .word 3881554616
  .word 2241023089
  .word 600491562
  .word 3254927331
  .word 1614395804
  .word 4268831573
  .word 2628300046
  .word 987768519
  .word 3642204288
  .word 2001672761
  .word 361141234
  .word 3015577003
  .word 1375045476
  .word 4029481245
  .word 2388949718
  .word 748418191
  .word 3402853960
  .word 1762322433
  .word 121790906
  .word 2776226675
  .word 1135695148
  .word 3790130917
  .word 2149599390
  .word 509067863
  .word 3163503632
  .word 1522972105
  .word 4177407874
  .word 2536876347
  .word 896344820
  .word 3550780589
  .word 1910249062
  .word 269717535
  .word 2924153304
  .word 1283621777
  .word 3938057546
  .word 2297526019
  .word 656994492
  .word 3311430261
  .word 1670898734
  .word 30367207
.section .bss
.balign 4
snapshot: .space 32
