.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
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
  divu a0, a0, a1
  divu a1, a2, a3
  divu a2, a4, a5
  divu a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  divu a4, a0, a1
  divu a5, a2, a3
  divu a6, a4, a5
  divu a7, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
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
  li t6, 256
.Lloop3:
  divu a4, a0, a1
  divu a5, a2, a3
  divu a6, a4, a5
  divu a7, a6, a7
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
  .word 100
  .word 2654435869
  .word 1013904342
  .word 3668340111
  .word 2027808584
  .word 387277057
  .word 3041712826
  .word 1401181299
  .word 4055617068
  .word 2415085541
  .word 774554014
  .word 3428989783
  .word 1788458256
  .word 147926729
  .word 2802362498
  .word 1161830971
  .word 3816266740
  .word 2175735213
  .word 535203686
  .word 3189639455
  .word 1549107928
  .word 4203543697
  .word 2563012170
  .word 922480643
  .word 3576916412
  .word 1936384885
  .word 295853358
  .word 2950289127
  .word 1309757600
  .word 3964193369
  .word 2323661842
  .word 683130315
  .word 3337566084
  .word 1697034557
  .word 56503030
  .word 2710938799
  .word 1070407272
  .word 3724843041
  .word 2084311514
  .word 443779987
  .word 3098215756
  .word 1457684229
  .word 4112119998
  .word 2471588471
  .word 831056944
  .word 3485492713
  .word 1844961186
  .word 204429659
  .word 2858865428
  .word 1218333901
  .word 3872769670
  .word 2232238143
  .word 591706616
  .word 3246142385
  .word 1605610858
  .word 4260046627
  .word 2619515100
  .word 978983573
  .word 3633419342
  .word 1992887815
  .word 352356288
  .word 3006792057
  .word 1366260530
  .word 4020696299
.section .bss
.balign 4
snapshot: .space 32
