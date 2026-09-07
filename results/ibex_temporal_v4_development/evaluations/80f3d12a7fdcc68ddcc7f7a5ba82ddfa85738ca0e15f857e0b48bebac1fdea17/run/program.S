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
  li s9, 10000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 250
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  sll a4, a4, a1
  srl a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  li t6, 375
.Lloop1:
  mul a0, a0, a1
  add a2, a2, a3
  bnez a4, .Lskip1_2
  mv a4, a5
.Lskip1_2:
  or a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 30000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 50
.Lloop2:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 40000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 349
.Lloop3:
  add a0, a0, a1
  xor a2, a2, a3
  mul a4, a4, a5
  divu a6, a6, a7
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
  .word 999465598
  .word 3653901367
  .word 2013369840
  .word 372838313
  .word 3027274082
  .word 1386742555
  .word 4041178324
  .word 2400646797
  .word 760115270
  .word 3414551039
  .word 1774019512
  .word 133487985
  .word 2787923754
  .word 1147392227
  .word 3801827996
  .word 2161296469
  .word 520764942
  .word 3175200711
  .word 1534669184
  .word 4189104953
  .word 2548573426
  .word 908041899
  .word 3562477668
  .word 1921946141
  .word 281414614
  .word 2935850383
  .word 1295318856
  .word 3949754625
  .word 2309223098
  .word 668691571
  .word 3323127340
  .word 1682595813
  .word 42064286
  .word 2696500055
  .word 1055968528
  .word 3710404297
  .word 2069872770
  .word 429341243
  .word 3083777012
  .word 1443245485
  .word 4097681254
  .word 2457149727
  .word 816618200
  .word 3471053969
  .word 1830522442
  .word 189990915
  .word 2844426684
  .word 1203895157
  .word 3858330926
  .word 2217799399
  .word 577267872
  .word 3231703641
  .word 1591172114
  .word 4245607883
  .word 2605076356
  .word 964544829
  .word 3618980598
  .word 1978449071
  .word 337917544
  .word 2992353313
  .word 1351821786
  .word 4006257555
  .word 2365726028
  .word 725194501
.section .bss
.balign 4
snapshot: .space 32
