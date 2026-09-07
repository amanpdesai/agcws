.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 3563155778
  li a1, 17
  li a2, 17
  li a3, 31
  li a4, 2985640943
  li a5, 530674170
  li a6, 1448331047
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 55759
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 176
.Lloop0:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 67518
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1704
.Lloop1:
  xor a7, a0, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 97971
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 1012
.Lloop2:
  mul a6, a7, a0
  mul a5, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 101619
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 16
.Lloop3:
  divu a0, a6, a1
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
  .word 4117426259
  .word 2476894732
  .word 836363205
  .word 3490798974
  .word 1850267447
  .word 209735920
  .word 2864171689
  .word 1223640162
  .word 3878075931
  .word 2237544404
  .word 597012877
  .word 3251448646
  .word 1610917119
  .word 4265352888
  .word 2624821361
  .word 984289834
  .word 3638725603
  .word 1998194076
  .word 357662549
  .word 3012098318
  .word 1371566791
  .word 4026002560
  .word 2385471033
  .word 744939506
  .word 3399375275
  .word 1758843748
  .word 118312221
  .word 2772747990
  .word 1132216463
  .word 3786652232
  .word 2146120705
  .word 505589178
  .word 3160024947
  .word 1519493420
  .word 4173929189
  .word 2533397662
  .word 892866135
  .word 3547301904
  .word 1906770377
  .word 266238850
  .word 2920674619
  .word 1280143092
  .word 3934578861
  .word 2294047334
  .word 653515807
  .word 3307951576
  .word 1667420049
  .word 26888522
  .word 2681324291
  .word 1040792764
  .word 3695228533
  .word 2054697006
  .word 414165479
  .word 3068601248
  .word 1428069721
  .word 4082505490
  .word 2441973963
  .word 801442436
  .word 3455878205
  .word 1815346678
  .word 174815151
  .word 2829250920
  .word 1188719393
  .word 3843155162
.section .bss
.balign 4
snapshot: .space 32
