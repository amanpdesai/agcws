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
  li t6, 273
.Lloop0:
  add a2, a0, a1
  mul a4, a2, a3
  xor a6, a4, a5
  sll a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 273
.Lloop1:
  add a2, a0, a1
  mul a4, a2, a3
  xor a6, a4, a5
  srl a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 273
.Lloop2:
  add a2, a0, a1
  mul a4, a2, a3
  xor a6, a4, a5
  and a0, a6, a7
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  add a2, a0, a1
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
  .word 2718281828
  .word 1077750301
  .word 3732186070
  .word 2091654543
  .word 451123016
  .word 3105558785
  .word 1465027258
  .word 4119463027
  .word 2478931500
  .word 838399973
  .word 3492835742
  .word 1852304215
  .word 211772688
  .word 2866208457
  .word 1225676930
  .word 3880112699
  .word 2239581172
  .word 599049645
  .word 3253485414
  .word 1612953887
  .word 4267389656
  .word 2626858129
  .word 986326602
  .word 3640762371
  .word 2000230844
  .word 359699317
  .word 3014135086
  .word 1373603559
  .word 4028039328
  .word 2387507801
  .word 746976274
  .word 3401412043
  .word 1760880516
  .word 120348989
  .word 2774784758
  .word 1134253231
  .word 3788689000
  .word 2148157473
  .word 507625946
  .word 3162061715
  .word 1521530188
  .word 4175965957
  .word 2535434430
  .word 894902903
  .word 3549338672
  .word 1908807145
  .word 268275618
  .word 2922711387
  .word 1282179860
  .word 3936615629
  .word 2296084102
  .word 655552575
  .word 3309988344
  .word 1669456817
  .word 28925290
  .word 2683361059
  .word 1042829532
  .word 3697265301
  .word 2056733774
  .word 416202247
  .word 3070638016
  .word 1430106489
  .word 4084542258
  .word 2444010731
.section .bss
.balign 4
snapshot: .space 32
