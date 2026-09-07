.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 10
  li a1, 20
  li a2, 30
  li a3, 40
  li a4, 50
  li a5, 60
  li a6, 70
  li a7, 80
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 128
.Lloop0:
  bnez a0, .Lskip0_0
  mv a0, a0
.Lskip0_0:
  bnez a1, .Lskip0_1
  mv a1, a1
.Lskip0_1:
  bnez a2, .Lskip0_2
  mv a2, a2
.Lskip0_2:
  bnez a3, .Lskip0_3
  mv a3, a3
.Lskip0_3:
  bnez a4, .Lskip0_4
  mv a4, a4
.Lskip0_4:
  bnez a5, .Lskip0_5
  mv a5, a5
.Lskip0_5:
  bnez a6, .Lskip0_6
  mv a6, a6
.Lskip0_6:
  bnez a7, .Lskip0_7
  mv a7, a7
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 5000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  mul a0, a0, a1
  mul a1, a1, a2
  mul a2, a2, a3
  mul a3, a3, a4
  mul a4, a4, a5
  mul a5, a5, a6
  mul a6, a6, a7
  mul a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 10000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  xor a0, a0, a1
  xor a1, a1, a2
  xor a2, a2, a3
  xor a3, a3, a4
  xor a4, a4, a5
  xor a5, a5, a6
  xor a6, a6, a7
  xor a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 15000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  sll a0, a0, a1
  sll a1, a1, a2
  sll a2, a2, a3
  sll a3, a3, a4
  sll a4, a4, a5
  sll a5, a5, a6
  sll a6, a6, a7
  sll a7, a7, a0
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
  .word 20240722
  .word 2674676491
  .word 1034144964
  .word 3688580733
  .word 2048049206
  .word 407517679
  .word 3061953448
  .word 1421421921
  .word 4075857690
  .word 2435326163
  .word 794794636
  .word 3449230405
  .word 1808698878
  .word 168167351
  .word 2822603120
  .word 1182071593
  .word 3836507362
  .word 2195975835
  .word 555444308
  .word 3209880077
  .word 1569348550
  .word 4223784319
  .word 2583252792
  .word 942721265
  .word 3597157034
  .word 1956625507
  .word 316093980
  .word 2970529749
  .word 1329998222
  .word 3984433991
  .word 2343902464
  .word 703370937
  .word 3357806706
  .word 1717275179
  .word 76743652
  .word 2731179421
  .word 1090647894
  .word 3745083663
  .word 2104552136
  .word 464020609
  .word 3118456378
  .word 1477924851
  .word 4132360620
  .word 2491829093
  .word 851297566
  .word 3505733335
  .word 1865201808
  .word 224670281
  .word 2879106050
  .word 1238574523
  .word 3893010292
  .word 2252478765
  .word 611947238
  .word 3266383007
  .word 1625851480
  .word 4280287249
  .word 2639755722
  .word 999224195
  .word 3653659964
  .word 2013128437
  .word 372596910
  .word 3027032679
  .word 1386501152
  .word 4040936921
.section .bss
.balign 4
snapshot: .space 32
