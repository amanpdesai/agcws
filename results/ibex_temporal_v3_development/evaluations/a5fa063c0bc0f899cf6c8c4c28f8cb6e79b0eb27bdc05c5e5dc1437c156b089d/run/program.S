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
  li t6, 128
.Lloop0:
  divu a0, a0, a0
  divu a1, a0, a0
  divu a2, a0, a0
  divu a3, a0, a0
  divu a4, a0, a0
  divu a5, a0, a0
  divu a6, a0, a0
  divu a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 128
.Lloop1:
  divu a0, a0, a0
  divu a1, a0, a0
  divu a2, a0, a0
  divu a3, a0, a0
  divu a4, a0, a0
  divu a5, a0, a0
  divu a6, a0, a0
  divu a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 128
.Lloop2:
  divu a0, a0, a0
  divu a1, a0, a0
  divu a2, a0, a0
  divu a3, a0, a0
  divu a4, a0, a0
  divu a5, a0, a0
  divu a6, a0, a0
  divu a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 150000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 128
.Lloop3:
  divu a0, a0, a0
  divu a1, a0, a0
  divu a2, a0, a0
  divu a3, a0, a0
  divu a4, a0, a0
  divu a5, a0, a0
  divu a6, a0, a0
  divu a7, a0, a0
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
  .word 100000000
  .word 2754435769
  .word 1113904242
  .word 3768340011
  .word 2127808484
  .word 487276957
  .word 3141712726
  .word 1501181199
  .word 4155616968
  .word 2515085441
  .word 874553914
  .word 3528989683
  .word 1888458156
  .word 247926629
  .word 2902362398
  .word 1261830871
  .word 3916266640
  .word 2275735113
  .word 635203586
  .word 3289639355
  .word 1649107828
  .word 8576301
  .word 2663012070
  .word 1022480543
  .word 3676916312
  .word 2036384785
  .word 395853258
  .word 3050289027
  .word 1409757500
  .word 4064193269
  .word 2423661742
  .word 783130215
  .word 3437565984
  .word 1797034457
  .word 156502930
  .word 2810938699
  .word 1170407172
  .word 3824842941
  .word 2184311414
  .word 543779887
  .word 3198215656
  .word 1557684129
  .word 4212119898
  .word 2571588371
  .word 931056844
  .word 3585492613
  .word 1944961086
  .word 304429559
  .word 2958865328
  .word 1318333801
  .word 3972769570
  .word 2332238043
  .word 691706516
  .word 3346142285
  .word 1705610758
  .word 65079231
  .word 2719515000
  .word 1078983473
  .word 3733419242
  .word 2092887715
  .word 452356188
  .word 3106791957
  .word 1466260430
  .word 4120696199
.section .bss
.balign 4
snapshot: .space 32
