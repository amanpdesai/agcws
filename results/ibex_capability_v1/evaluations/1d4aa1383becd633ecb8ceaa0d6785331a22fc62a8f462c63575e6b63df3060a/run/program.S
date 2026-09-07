.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1092998618
  li a1, 31
  li a2, 0
  li a3, 31
  li a4, 17
  li a5, 1644901137
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 154490
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 2048
.Lloop0:
  and a5, a4, a4
  or a7, a7, a6
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
  .word 329005646
  .word 2983441415
  .word 1342909888
  .word 3997345657
  .word 2356814130
  .word 716282603
  .word 3370718372
  .word 1730186845
  .word 89655318
  .word 2744091087
  .word 1103559560
  .word 3757995329
  .word 2117463802
  .word 476932275
  .word 3131368044
  .word 1490836517
  .word 4145272286
  .word 2504740759
  .word 864209232
  .word 3518645001
  .word 1878113474
  .word 237581947
  .word 2892017716
  .word 1251486189
  .word 3905921958
  .word 2265390431
  .word 624858904
  .word 3279294673
  .word 1638763146
  .word 4293198915
  .word 2652667388
  .word 1012135861
  .word 3666571630
  .word 2026040103
  .word 385508576
  .word 3039944345
  .word 1399412818
  .word 4053848587
  .word 2413317060
  .word 772785533
  .word 3427221302
  .word 1786689775
  .word 146158248
  .word 2800594017
  .word 1160062490
  .word 3814498259
  .word 2173966732
  .word 533435205
  .word 3187870974
  .word 1547339447
  .word 4201775216
  .word 2561243689
  .word 920712162
  .word 3575147931
  .word 1934616404
  .word 294084877
  .word 2948520646
  .word 1307989119
  .word 3962424888
  .word 2321893361
  .word 681361834
  .word 3335797603
  .word 1695266076
  .word 54734549
.section .bss
.balign 4
snapshot: .space 32
