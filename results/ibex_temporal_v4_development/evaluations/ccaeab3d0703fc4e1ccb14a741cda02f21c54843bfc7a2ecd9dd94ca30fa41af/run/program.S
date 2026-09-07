.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 290900373
  li a1, 0
  li a2, 1845852657
  li a3, 17
  li a4, 4084027705
  li a5, 31
  li a6, 687549298
  li a7, 1039938737
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 140453
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1024
.Lloop0:
  sll a3, a7, a0
  sll a2, a3, a1
  srl a5, a3, a1
  divu a2, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 2998771510
  .word 1358239983
  .word 4012675752
  .word 2372144225
  .word 731612698
  .word 3386048467
  .word 1745516940
  .word 104985413
  .word 2759421182
  .word 1118889655
  .word 3773325424
  .word 2132793897
  .word 492262370
  .word 3146698139
  .word 1506166612
  .word 4160602381
  .word 2520070854
  .word 879539327
  .word 3533975096
  .word 1893443569
  .word 252912042
  .word 2907347811
  .word 1266816284
  .word 3921252053
  .word 2280720526
  .word 640188999
  .word 3294624768
  .word 1654093241
  .word 13561714
  .word 2667997483
  .word 1027465956
  .word 3681901725
  .word 2041370198
  .word 400838671
  .word 3055274440
  .word 1414742913
  .word 4069178682
  .word 2428647155
  .word 788115628
  .word 3442551397
  .word 1802019870
  .word 161488343
  .word 2815924112
  .word 1175392585
  .word 3829828354
  .word 2189296827
  .word 548765300
  .word 3203201069
  .word 1562669542
  .word 4217105311
  .word 2576573784
  .word 936042257
  .word 3590478026
  .word 1949946499
  .word 309414972
  .word 2963850741
  .word 1323319214
  .word 3977754983
  .word 2337223456
  .word 696691929
  .word 3351127698
  .word 1710596171
  .word 70064644
  .word 2724500413
.section .bss
.balign 4
snapshot: .space 32
