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
  divu a2, a2, a0
  divu a4, a4, a0
  divu a6, a6, a0
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
  .word 11111
  .word 2654446880
  .word 1013915353
  .word 3668351122
  .word 2027819595
  .word 387288068
  .word 3041723837
  .word 1401192310
  .word 4055628079
  .word 2415096552
  .word 774565025
  .word 3429000794
  .word 1788469267
  .word 147937740
  .word 2802373509
  .word 1161841982
  .word 3816277751
  .word 2175746224
  .word 535214697
  .word 3189650466
  .word 1549118939
  .word 4203554708
  .word 2563023181
  .word 922491654
  .word 3576927423
  .word 1936395896
  .word 295864369
  .word 2950300138
  .word 1309768611
  .word 3964204380
  .word 2323672853
  .word 683141326
  .word 3337577095
  .word 1697045568
  .word 56514041
  .word 2710949810
  .word 1070418283
  .word 3724854052
  .word 2084322525
  .word 443790998
  .word 3098226767
  .word 1457695240
  .word 4112131009
  .word 2471599482
  .word 831067955
  .word 3485503724
  .word 1844972197
  .word 204440670
  .word 2858876439
  .word 1218344912
  .word 3872780681
  .word 2232249154
  .word 591717627
  .word 3246153396
  .word 1605621869
  .word 4260057638
  .word 2619526111
  .word 978994584
  .word 3633430353
  .word 1992898826
  .word 352367299
  .word 3006803068
  .word 1366271541
  .word 4020707310
.section .bss
.balign 4
snapshot: .space 32
