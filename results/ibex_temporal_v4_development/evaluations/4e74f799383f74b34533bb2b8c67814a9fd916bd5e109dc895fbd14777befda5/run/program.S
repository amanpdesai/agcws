.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
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
  li t6, 220
.Lloop0:
  add a2, a0, a1
  mul a4, a2, a3
  sll a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 40000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 237
.Lloop1:
  xor a1, a7, a0
  srl a3, a1, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  divu a0, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  xor a1, a7, a0
  srl a3, a1, a2
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 80000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 250
.Lloop2:
  bnez a0, .Lskip2_0
  mv a2, a1
.Lskip2_0:
  and a4, a2, a3
  or a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 120000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 261
.Lloop3:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  sll a3, a1, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a4, 0(t2)
  mul a7, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  sll a3, a1, a2
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
  .word 12345
  .word 2654448114
  .word 1013916587
  .word 3668352356
  .word 2027820829
  .word 387289302
  .word 3041725071
  .word 1401193544
  .word 4055629313
  .word 2415097786
  .word 774566259
  .word 3429002028
  .word 1788470501
  .word 147938974
  .word 2802374743
  .word 1161843216
  .word 3816278985
  .word 2175747458
  .word 535215931
  .word 3189651700
  .word 1549120173
  .word 4203555942
  .word 2563024415
  .word 922492888
  .word 3576928657
  .word 1936397130
  .word 295865603
  .word 2950301372
  .word 1309769845
  .word 3964205614
  .word 2323674087
  .word 683142560
  .word 3337578329
  .word 1697046802
  .word 56515275
  .word 2710951044
  .word 1070419517
  .word 3724855286
  .word 2084323759
  .word 443792232
  .word 3098228001
  .word 1457696474
  .word 4112132243
  .word 2471600716
  .word 831069189
  .word 3485504958
  .word 1844973431
  .word 204441904
  .word 2858877673
  .word 1218346146
  .word 3872781915
  .word 2232250388
  .word 591718861
  .word 3246154630
  .word 1605623103
  .word 4260058872
  .word 2619527345
  .word 978995818
  .word 3633431587
  .word 1992900060
  .word 352368533
  .word 3006804302
  .word 1366272775
  .word 4020708544
.section .bss
.balign 4
snapshot: .space 32
