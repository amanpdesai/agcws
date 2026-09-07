.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 4294967295
  li a2, 2752864629
  li a3, 31
  li a4, 31
  li a5, 17
  li a6, 17
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 1386
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 174
.Lloop0:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 27025
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 54
.Lloop1:
  or a3, a3, a0
  add a2, a1, a0
  srl a6, a0, a1
  srl a4, a2, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 113522
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 1244
.Lloop2:
  bnez a4, .Lskip2_0
  mv a3, a7
.Lskip2_0:
  bnez a3, .Lskip2_1
  mv a2, a2
.Lskip2_1:
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
  .word 3755779838
  .word 2115248311
  .word 474716784
  .word 3129152553
  .word 1488621026
  .word 4143056795
  .word 2502525268
  .word 861993741
  .word 3516429510
  .word 1875897983
  .word 235366456
  .word 2889802225
  .word 1249270698
  .word 3903706467
  .word 2263174940
  .word 622643413
  .word 3277079182
  .word 1636547655
  .word 4290983424
  .word 2650451897
  .word 1009920370
  .word 3664356139
  .word 2023824612
  .word 383293085
  .word 3037728854
  .word 1397197327
  .word 4051633096
  .word 2411101569
  .word 770570042
  .word 3425005811
  .word 1784474284
  .word 143942757
  .word 2798378526
  .word 1157846999
  .word 3812282768
  .word 2171751241
  .word 531219714
  .word 3185655483
  .word 1545123956
  .word 4199559725
  .word 2559028198
  .word 918496671
  .word 3572932440
  .word 1932400913
  .word 291869386
  .word 2946305155
  .word 1305773628
  .word 3960209397
  .word 2319677870
  .word 679146343
  .word 3333582112
  .word 1693050585
  .word 52519058
  .word 2706954827
  .word 1066423300
  .word 3720859069
  .word 2080327542
  .word 439796015
  .word 3094231784
  .word 1453700257
  .word 4108136026
  .word 2467604499
  .word 827072972
  .word 3481508741
.section .bss
.balign 4
snapshot: .space 32
