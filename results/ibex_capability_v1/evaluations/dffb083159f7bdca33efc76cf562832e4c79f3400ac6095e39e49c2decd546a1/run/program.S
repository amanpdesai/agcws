.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 2
  li a2, 3
  li a3, 4
  li a4, 5
  li a5, 6
  li a6, 7
  li a7, 8
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 0
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
  mul a1, a1, a2
  add a2, a2, a3
  mul a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 50000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 250
.Lloop1:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  and a6, a6, a7
  or a7, a7, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 125000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 166
.Lloop2:
  divu a0, a0, a1
  divu a2, a2, a3
  divu a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a1
  divu a2, a2, a3
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 160000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 532
.Lloop3:
  sll a6, a6, a7
  bnez a0, .Lskip3_1
  mv a7, a1
.Lskip3_1:
  add a7, a7, a6
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
  .word 19951121
  .word 2674386890
  .word 1033855363
  .word 3688291132
  .word 2047759605
  .word 407228078
  .word 3061663847
  .word 1421132320
  .word 4075568089
  .word 2435036562
  .word 794505035
  .word 3448940804
  .word 1808409277
  .word 167877750
  .word 2822313519
  .word 1181781992
  .word 3836217761
  .word 2195686234
  .word 555154707
  .word 3209590476
  .word 1569058949
  .word 4223494718
  .word 2582963191
  .word 942431664
  .word 3596867433
  .word 1956335906
  .word 315804379
  .word 2970240148
  .word 1329708621
  .word 3984144390
  .word 2343612863
  .word 703081336
  .word 3357517105
  .word 1716985578
  .word 76454051
  .word 2730889820
  .word 1090358293
  .word 3744794062
  .word 2104262535
  .word 463731008
  .word 3118166777
  .word 1477635250
  .word 4132071019
  .word 2491539492
  .word 851007965
  .word 3505443734
  .word 1864912207
  .word 224380680
  .word 2878816449
  .word 1238284922
  .word 3892720691
  .word 2252189164
  .word 611657637
  .word 3266093406
  .word 1625561879
  .word 4279997648
  .word 2639466121
  .word 998934594
  .word 3653370363
  .word 2012838836
  .word 372307309
  .word 3026743078
  .word 1386211551
  .word 4040647320
.section .bss
.balign 4
snapshot: .space 32
