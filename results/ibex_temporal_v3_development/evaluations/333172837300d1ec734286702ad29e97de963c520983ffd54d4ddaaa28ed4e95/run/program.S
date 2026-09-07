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
  li t6, 250
.Lloop0:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a1, a0, a2
  add a3, a1, a3
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 5000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 375
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 274
.Lloop2:
  bnez a0, .Lskip2_0
  mv a0, a1
.Lskip2_0:
  bnez a1, .Lskip2_1
  mv a1, a2
.Lskip2_1:
  bnez a2, .Lskip2_2
  mv a2, a3
.Lskip2_2:
  bnez a3, .Lskip2_3
  mv a3, a4
.Lskip2_3:
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 3333333333
  .word 1692801806
  .word 52270279
  .word 2706706048
  .word 1066174521
  .word 3720610290
  .word 2080078763
  .word 439547236
  .word 3093983005
  .word 1453451478
  .word 4107887247
  .word 2467355720
  .word 826824193
  .word 3481259962
  .word 1840728435
  .word 200196908
  .word 2854632677
  .word 1214101150
  .word 3868536919
  .word 2228005392
  .word 587473865
  .word 3241909634
  .word 1601378107
  .word 4255813876
  .word 2615282349
  .word 974750822
  .word 3629186591
  .word 1988655064
  .word 348123537
  .word 3002559306
  .word 1362027779
  .word 4016463548
  .word 2375932021
  .word 735400494
  .word 3389836263
  .word 1749304736
  .word 108773209
  .word 2763208978
  .word 1122677451
  .word 3777113220
  .word 2136581693
  .word 496050166
  .word 3150485935
  .word 1509954408
  .word 4164390177
  .word 2523858650
  .word 883327123
  .word 3537762892
  .word 1897231365
  .word 256699838
  .word 2911135607
  .word 1270604080
  .word 3925039849
  .word 2284508322
  .word 643976795
  .word 3298412564
  .word 1657881037
  .word 17349510
  .word 2671785279
  .word 1031253752
  .word 3685689521
  .word 2045157994
  .word 404626467
  .word 3059062236
.section .bss
.balign 4
snapshot: .space 32
