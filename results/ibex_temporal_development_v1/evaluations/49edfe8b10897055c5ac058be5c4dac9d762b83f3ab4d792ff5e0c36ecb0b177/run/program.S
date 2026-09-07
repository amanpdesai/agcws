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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  xor a2, a2, a3
  sll a4, a4, a5
  divu a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  divu a1, a1, a2
  mul a3, a3, a4
  srl a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  bnez a0, .Lskip2_1
  mv a0, a1
.Lskip2_1:
  add a2, a2, a3
  xor a4, a4, a5
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 75000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  divu a6, a6, a7
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  divu a0, a0, a1
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
  .word 100000007
  .word 2754435776
  .word 1113904249
  .word 3768340018
  .word 2127808491
  .word 487276964
  .word 3141712733
  .word 1501181206
  .word 4155616975
  .word 2515085448
  .word 874553921
  .word 3528989690
  .word 1888458163
  .word 247926636
  .word 2902362405
  .word 1261830878
  .word 3916266647
  .word 2275735120
  .word 635203593
  .word 3289639362
  .word 1649107835
  .word 8576308
  .word 2663012077
  .word 1022480550
  .word 3676916319
  .word 2036384792
  .word 395853265
  .word 3050289034
  .word 1409757507
  .word 4064193276
  .word 2423661749
  .word 783130222
  .word 3437565991
  .word 1797034464
  .word 156502937
  .word 2810938706
  .word 1170407179
  .word 3824842948
  .word 2184311421
  .word 543779894
  .word 3198215663
  .word 1557684136
  .word 4212119905
  .word 2571588378
  .word 931056851
  .word 3585492620
  .word 1944961093
  .word 304429566
  .word 2958865335
  .word 1318333808
  .word 3972769577
  .word 2332238050
  .word 691706523
  .word 3346142292
  .word 1705610765
  .word 65079238
  .word 2719515007
  .word 1078983480
  .word 3733419249
  .word 2092887722
  .word 452356195
  .word 3106791964
  .word 1466260437
  .word 4120696206
.section .bss
.balign 4
snapshot: .space 32
