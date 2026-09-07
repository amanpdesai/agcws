.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
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
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  add a0, a0, a1
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  divu a2, a0, a0
  divu a4, a0, a0
  divu a6, a0, a0
  divu a0, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  add a0, a0, a1
  mul a0, a0, a1
  xor a0, a0, a1
  sll a0, a0, a1
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
  .word 112233
  .word 2654548002
  .word 1014016475
  .word 3668452244
  .word 2027920717
  .word 387389190
  .word 3041824959
  .word 1401293432
  .word 4055729201
  .word 2415197674
  .word 774666147
  .word 3429101916
  .word 1788570389
  .word 148038862
  .word 2802474631
  .word 1161943104
  .word 3816378873
  .word 2175847346
  .word 535315819
  .word 3189751588
  .word 1549220061
  .word 4203655830
  .word 2563124303
  .word 922592776
  .word 3577028545
  .word 1936497018
  .word 295965491
  .word 2950401260
  .word 1309869733
  .word 3964305502
  .word 2323773975
  .word 683242448
  .word 3337678217
  .word 1697146690
  .word 56615163
  .word 2711050932
  .word 1070519405
  .word 3724955174
  .word 2084423647
  .word 443892120
  .word 3098327889
  .word 1457796362
  .word 4112232131
  .word 2471700604
  .word 831169077
  .word 3485604846
  .word 1845073319
  .word 204541792
  .word 2858977561
  .word 1218446034
  .word 3872881803
  .word 2232350276
  .word 591818749
  .word 3246254518
  .word 1605722991
  .word 4260158760
  .word 2619627233
  .word 979095706
  .word 3633531475
  .word 1992999948
  .word 352468421
  .word 3006904190
  .word 1366372663
  .word 4020808432
.section .bss
.balign 4
snapshot: .space 32
