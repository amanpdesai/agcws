.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 4294967295
  li a2, 0
  li a3, 31
  li a4, 1
  li a5, 0
  li a6, 4294967295
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 86377
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 512
.Lloop0:
  mul a7, a0, a1
  mul a4, a2, a0
  mul a7, a3, a1
  mul a7, a0, a0
  mul a6, a7, a1
  mul a2, a4, a0
  mul a4, a2, a1
  mul a6, a1, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
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
  .word 4080293214
  .word 2439761687
  .word 799230160
  .word 3453665929
  .word 1813134402
  .word 172602875
  .word 2827038644
  .word 1186507117
  .word 3840942886
  .word 2200411359
  .word 559879832
  .word 3214315601
  .word 1573784074
  .word 4228219843
  .word 2587688316
  .word 947156789
  .word 3601592558
  .word 1961061031
  .word 320529504
  .word 2974965273
  .word 1334433746
  .word 3988869515
  .word 2348337988
  .word 707806461
  .word 3362242230
  .word 1721710703
  .word 81179176
  .word 2735614945
  .word 1095083418
  .word 3749519187
  .word 2108987660
  .word 468456133
  .word 3122891902
  .word 1482360375
  .word 4136796144
  .word 2496264617
  .word 855733090
  .word 3510168859
  .word 1869637332
  .word 229105805
  .word 2883541574
  .word 1243010047
  .word 3897445816
  .word 2256914289
  .word 616382762
  .word 3270818531
  .word 1630287004
  .word 4284722773
  .word 2644191246
  .word 1003659719
  .word 3658095488
  .word 2017563961
  .word 377032434
  .word 3031468203
  .word 1390936676
  .word 4045372445
  .word 2404840918
  .word 764309391
  .word 3418745160
  .word 1778213633
  .word 137682106
  .word 2792117875
  .word 1151586348
  .word 3806022117
.section .bss
.balign 4
snapshot: .space 32
