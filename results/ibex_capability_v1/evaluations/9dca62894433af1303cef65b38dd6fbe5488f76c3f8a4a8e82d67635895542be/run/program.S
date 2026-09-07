.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 31
  li a1, 1
  li a2, 17
  li a3, 0
  li a4, 4294967295
  li a5, 0
  li a6, 4294967295
  li a7, 3375499307
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 27891
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 20
.Lloop0:
  mul a0, a5, a2
  mul a5, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 92970
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 164
.Lloop1:
  divu a6, a0, a1
  divu a6, a2, a1
  divu a7, a4, a1
  divu a6, a1, a0
  divu a7, a4, a1
  divu a2, a3, a0
  divu a6, a2, a1
  divu a2, a4, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 117511
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 2744
.Lloop2:
  mul a6, a6, a2
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
  .word 3939178002
  .word 2298646475
  .word 658114948
  .word 3312550717
  .word 1672019190
  .word 31487663
  .word 2685923432
  .word 1045391905
  .word 3699827674
  .word 2059296147
  .word 418764620
  .word 3073200389
  .word 1432668862
  .word 4087104631
  .word 2446573104
  .word 806041577
  .word 3460477346
  .word 1819945819
  .word 179414292
  .word 2833850061
  .word 1193318534
  .word 3847754303
  .word 2207222776
  .word 566691249
  .word 3221127018
  .word 1580595491
  .word 4235031260
  .word 2594499733
  .word 953968206
  .word 3608403975
  .word 1967872448
  .word 327340921
  .word 2981776690
  .word 1341245163
  .word 3995680932
  .word 2355149405
  .word 714617878
  .word 3369053647
  .word 1728522120
  .word 87990593
  .word 2742426362
  .word 1101894835
  .word 3756330604
  .word 2115799077
  .word 475267550
  .word 3129703319
  .word 1489171792
  .word 4143607561
  .word 2503076034
  .word 862544507
  .word 3516980276
  .word 1876448749
  .word 235917222
  .word 2890352991
  .word 1249821464
  .word 3904257233
  .word 2263725706
  .word 623194179
  .word 3277629948
  .word 1637098421
  .word 4291534190
  .word 2651002663
  .word 1010471136
  .word 3664906905
.section .bss
.balign 4
snapshot: .space 32
