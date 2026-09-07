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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  xor a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  sll a2, a2, a3
  mul a3, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 20000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  and a4, a4, a5
  or a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 30000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  srl a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 40000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 256
.Lloop4:
  divu a0, a0, a1
  xor a1, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 50000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 256
.Lloop5:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  mul a3, a3, a4
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 60000
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 256
.Lloop6:
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  or a5, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 70000
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 256
.Lloop7:
  sll a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 1122334491
  .word 3776770260
  .word 2136238733
  .word 495707206
  .word 3150142975
  .word 1509611448
  .word 4164047217
  .word 2523515690
  .word 882984163
  .word 3537419932
  .word 1896888405
  .word 256356878
  .word 2910792647
  .word 1270261120
  .word 3924696889
  .word 2284165362
  .word 643633835
  .word 3298069604
  .word 1657538077
  .word 17006550
  .word 2671442319
  .word 1030910792
  .word 3685346561
  .word 2044815034
  .word 404283507
  .word 3058719276
  .word 1418187749
  .word 4072623518
  .word 2432091991
  .word 791560464
  .word 3445996233
  .word 1805464706
  .word 164933179
  .word 2819368948
  .word 1178837421
  .word 3833273190
  .word 2192741663
  .word 552210136
  .word 3206645905
  .word 1566114378
  .word 4220550147
  .word 2580018620
  .word 939487093
  .word 3593922862
  .word 1953391335
  .word 312859808
  .word 2967295577
  .word 1326764050
  .word 3981199819
  .word 2340668292
  .word 700136765
  .word 3354572534
  .word 1714041007
  .word 73509480
  .word 2727945249
  .word 1087413722
  .word 3741849491
  .word 2101317964
  .word 460786437
  .word 3115222206
  .word 1474690679
  .word 4129126448
  .word 2488594921
  .word 848063394
.section .bss
.balign 4
snapshot: .space 32
