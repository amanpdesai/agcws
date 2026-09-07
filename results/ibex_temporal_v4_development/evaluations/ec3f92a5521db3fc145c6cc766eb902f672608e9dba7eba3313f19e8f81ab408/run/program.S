.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 17
  li a3, 4294967295
  li a4, 1076035761
  li a5, 4294967295
  li a6, 1
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 5000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 312
.Lloop0:
  add a5, a7, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a5, a4, a6
  divu a1, a3, a3
  divu a0, a6, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  srl a3, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a5, a7, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a5, a4, a6
  divu a1, a3, a3
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 20000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 50
.Lloop1:
  bnez a4, .Lskip1_0
  mv a3, a0
.Lskip1_0:
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 100000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 200
.Lloop2:
  bnez a5, .Lskip2_0
  mv a3, a0
.Lskip2_0:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 150000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 168
.Lloop3:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  xor a4, a0, a3
  srl a4, a4, a5
  bnez a4, .Lskip3_3
  mv a2, a5
.Lskip3_3:
  divu a7, a7, a7
  add a2, a3, a3
  bnez a3, .Lskip3_6
  mv a3, a7
.Lskip3_6:
  xor a0, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  xor a4, a0, a3
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
  .word 999465599
  .word 3653901368
  .word 2013369841
  .word 372838314
  .word 3027274083
  .word 1386742556
  .word 4041178325
  .word 2400646798
  .word 760115271
  .word 3414551040
  .word 1774019513
  .word 133487986
  .word 2787923755
  .word 1147392228
  .word 3801827997
  .word 2161296470
  .word 520764943
  .word 3175200712
  .word 1534669185
  .word 4189104954
  .word 2548573427
  .word 908041900
  .word 3562477669
  .word 1921946142
  .word 281414615
  .word 2935850384
  .word 1295318857
  .word 3949754626
  .word 2309223099
  .word 668691572
  .word 3323127341
  .word 1682595814
  .word 42064287
  .word 2696500056
  .word 1055968529
  .word 3710404298
  .word 2069872771
  .word 429341244
  .word 3083777013
  .word 1443245486
  .word 4097681255
  .word 2457149728
  .word 816618201
  .word 3471053970
  .word 1830522443
  .word 189990916
  .word 2844426685
  .word 1203895158
  .word 3858330927
  .word 2217799400
  .word 577267873
  .word 3231703642
  .word 1591172115
  .word 4245607884
  .word 2605076357
  .word 964544830
  .word 3618980599
  .word 1978449072
  .word 337917545
  .word 2992353314
  .word 1351821787
  .word 4006257556
  .word 2365726029
  .word 725194502
.section .bss
.balign 4
snapshot: .space 32
