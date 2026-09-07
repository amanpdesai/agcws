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
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 286
.Lloop0:
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
  mul a1, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
  li s9, 15000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 51
.Lloop1:
  add a2, a2, a3
  srl a3, a3, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 30000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 51
.Lloop2:
  add a4, a4, a5
  xor a5, a5, a4
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 70000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 245
.Lloop3:
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
  mul a1, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
  li s9, 90000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 245
.Lloop4:
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
  mul a1, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
  add a0, a0, a1
  sll a1, a1, a0
  xor a6, a6, a7
  or a7, a7, a6
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
  .word 112233445
  .word 2766669214
  .word 1126137687
  .word 3780573456
  .word 2140041929
  .word 499510402
  .word 3153946171
  .word 1513414644
  .word 4167850413
  .word 2527318886
  .word 886787359
  .word 3541223128
  .word 1900691601
  .word 260160074
  .word 2914595843
  .word 1274064316
  .word 3928500085
  .word 2287968558
  .word 647437031
  .word 3301872800
  .word 1661341273
  .word 20809746
  .word 2675245515
  .word 1034713988
  .word 3689149757
  .word 2048618230
  .word 408086703
  .word 3062522472
  .word 1421990945
  .word 4076426714
  .word 2435895187
  .word 795363660
  .word 3449799429
  .word 1809267902
  .word 168736375
  .word 2823172144
  .word 1182640617
  .word 3837076386
  .word 2196544859
  .word 556013332
  .word 3210449101
  .word 1569917574
  .word 4224353343
  .word 2583821816
  .word 943290289
  .word 3597726058
  .word 1957194531
  .word 316663004
  .word 2971098773
  .word 1330567246
  .word 3985003015
  .word 2344471488
  .word 703939961
  .word 3358375730
  .word 1717844203
  .word 77312676
  .word 2731748445
  .word 1091216918
  .word 3745652687
  .word 2105121160
  .word 464589633
  .word 3119025402
  .word 1478493875
  .word 4132929644
.section .bss
.balign 4
snapshot: .space 32
