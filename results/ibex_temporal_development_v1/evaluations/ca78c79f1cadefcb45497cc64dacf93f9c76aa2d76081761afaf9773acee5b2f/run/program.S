.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 1
  li a2, 2
  li a3, 3
  li a4, 4
  li a5, 5
  li a6, 6
  li a7, 7
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 512
.Lloop0:
  add a1, a0, a1
  xor a2, a1, a2
  mul a3, a2, a3
  add a4, a3, a4
  xor a5, a4, a5
  and a6, a5, a6
  or a7, a6, a7
  sll a0, a7, a0
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
  .word 987654323
  .word 3642090092
  .word 2001558565
  .word 361027038
  .word 3015462807
  .word 1374931280
  .word 4029367049
  .word 2388835522
  .word 748303995
  .word 3402739764
  .word 1762208237
  .word 121676710
  .word 2776112479
  .word 1135580952
  .word 3790016721
  .word 2149485194
  .word 508953667
  .word 3163389436
  .word 1522857909
  .word 4177293678
  .word 2536762151
  .word 896230624
  .word 3550666393
  .word 1910134866
  .word 269603339
  .word 2924039108
  .word 1283507581
  .word 3937943350
  .word 2297411823
  .word 656880296
  .word 3311316065
  .word 1670784538
  .word 30253011
  .word 2684688780
  .word 1044157253
  .word 3698593022
  .word 2058061495
  .word 417529968
  .word 3071965737
  .word 1431434210
  .word 4085869979
  .word 2445338452
  .word 804806925
  .word 3459242694
  .word 1818711167
  .word 178179640
  .word 2832615409
  .word 1192083882
  .word 3846519651
  .word 2205988124
  .word 565456597
  .word 3219892366
  .word 1579360839
  .word 4233796608
  .word 2593265081
  .word 952733554
  .word 3607169323
  .word 1966637796
  .word 326106269
  .word 2980542038
  .word 1340010511
  .word 3994446280
  .word 2353914753
  .word 713383226
.section .bss
.balign 4
snapshot: .space 32
