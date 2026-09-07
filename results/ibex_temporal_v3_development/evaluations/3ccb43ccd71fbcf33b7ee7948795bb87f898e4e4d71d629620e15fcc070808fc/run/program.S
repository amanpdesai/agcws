.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 85
.Lloop0:
  add a2, a0, a1
  add a3, a0, a1
  add a4, a0, a1
  add a5, a0, a1
  add a6, a0, a1
  add a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a2, a0, a1
  add a3, a0, a1
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 170
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a1, a2
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a2, a3
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a3, a4
.Lskip1_3:
  bnez a4, .Lskip1_4
  mv a4, a5
.Lskip1_4:
  bnez a5, .Lskip1_5
  mv a5, a6
.Lskip1_5:
  addi t6, t6, -1
  bnez t6, .Lloop1
  bnez a0, .Ltail_skip1_0
  mv a0, a1
.Ltail_skip1_0:
  bnez a1, .Ltail_skip1_1
  mv a1, a2
.Ltail_skip1_1:
  bnez a2, .Ltail_skip1_2
  mv a2, a3
.Ltail_skip1_2:
  bnez a3, .Ltail_skip1_3
  mv a3, a4
.Ltail_skip1_3:
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 384
.Lloop2:
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 204
.Lloop3:
  add a0, a0, a1
  add a1, a0, a1
  add a2, a0, a1
  add a3, a0, a1
  add a4, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  add a1, a0, a1
  add a2, a0, a1
  add a3, a0, a1
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
  .word 1658392131
  .word 17860604
  .word 2672296373
  .word 1031764846
  .word 3686200615
  .word 2045669088
  .word 405137561
  .word 3059573330
  .word 1419041803
  .word 4073477572
  .word 2432946045
  .word 792414518
  .word 3446850287
  .word 1806318760
  .word 165787233
  .word 2820223002
  .word 1179691475
  .word 3834127244
  .word 2193595717
  .word 553064190
  .word 3207499959
  .word 1566968432
  .word 4221404201
  .word 2580872674
  .word 940341147
  .word 3594776916
  .word 1954245389
  .word 313713862
  .word 2968149631
  .word 1327618104
  .word 3982053873
  .word 2341522346
  .word 700990819
  .word 3355426588
  .word 1714895061
  .word 74363534
  .word 2728799303
  .word 1088267776
  .word 3742703545
  .word 2102172018
  .word 461640491
  .word 3116076260
  .word 1475544733
  .word 4129980502
  .word 2489448975
  .word 848917448
  .word 3503353217
  .word 1862821690
  .word 222290163
  .word 2876725932
  .word 1236194405
  .word 3890630174
  .word 2250098647
  .word 609567120
  .word 3264002889
  .word 1623471362
  .word 4277907131
  .word 2637375604
  .word 996844077
  .word 3651279846
  .word 2010748319
  .word 370216792
  .word 3024652561
  .word 1384121034
.section .bss
.balign 4
snapshot: .space 32
