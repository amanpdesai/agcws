.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 4294967295
  li a1, 17
  li a2, 31
  li a3, 0
  li a4, 4294967295
  li a5, 1
  li a6, 31
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 119330
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 208
.Lloop0:
  divu a4, a1, a1
  divu a7, a5, a1
  divu a5, a5, a0
  divu a3, a0, a1
  divu a6, a5, a0
  divu a4, a1, a1
  divu a6, a7, a0
  divu a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 154155
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 496
.Lloop1:
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 167635
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 1440
.Lloop2:
  srl a4, a3, a4
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
  .word 417563189
  .word 3071998958
  .word 1431467431
  .word 4085903200
  .word 2445371673
  .word 804840146
  .word 3459275915
  .word 1818744388
  .word 178212861
  .word 2832648630
  .word 1192117103
  .word 3846552872
  .word 2206021345
  .word 565489818
  .word 3219925587
  .word 1579394060
  .word 4233829829
  .word 2593298302
  .word 952766775
  .word 3607202544
  .word 1966671017
  .word 326139490
  .word 2980575259
  .word 1340043732
  .word 3994479501
  .word 2353947974
  .word 713416447
  .word 3367852216
  .word 1727320689
  .word 86789162
  .word 2741224931
  .word 1100693404
  .word 3755129173
  .word 2114597646
  .word 474066119
  .word 3128501888
  .word 1487970361
  .word 4142406130
  .word 2501874603
  .word 861343076
  .word 3515778845
  .word 1875247318
  .word 234715791
  .word 2889151560
  .word 1248620033
  .word 3903055802
  .word 2262524275
  .word 621992748
  .word 3276428517
  .word 1635896990
  .word 4290332759
  .word 2649801232
  .word 1009269705
  .word 3663705474
  .word 2023173947
  .word 382642420
  .word 3037078189
  .word 1396546662
  .word 4050982431
  .word 2410450904
  .word 769919377
  .word 3424355146
  .word 1783823619
  .word 143292092
.section .bss
.balign 4
snapshot: .space 32
