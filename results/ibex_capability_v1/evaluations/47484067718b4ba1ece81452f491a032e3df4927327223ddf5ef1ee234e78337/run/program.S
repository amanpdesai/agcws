.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 17
  li a3, 4294967295
  li a4, 1076035761
  li a5, 4294967295
  li a6, 1
  li a7, 4294967295
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 15000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 300
.Lloop0:
  add a0, a0, a1
  mul a2, a2, a3
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 25000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 300
.Lloop1:
  add a0, a0, a1
  mul a2, a2, a3
  sll a4, a4, a1
  srl a5, a5, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 35000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 100
.Lloop2:
  bnez a0, .Lskip2_0
  mv a0, a7
.Lskip2_0:
  bnez a1, .Lskip2_1
  mv a1, a0
.Lskip2_1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 45000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 324
.Lloop3:
  add a6, a6, a7
  or a0, a0, a1
  bnez a2, .Lskip3_2
  mv a2, a3
.Lskip3_2:
  mul a4, a4, a5
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
  .word 500000000
  .word 3154435769
  .word 1513904242
  .word 4168340011
  .word 2527808484
  .word 887276957
  .word 3541712726
  .word 1901181199
  .word 260649672
  .word 2915085441
  .word 1274553914
  .word 3928989683
  .word 2288458156
  .word 647926629
  .word 3302362398
  .word 1661830871
  .word 21299344
  .word 2675735113
  .word 1035203586
  .word 3689639355
  .word 2049107828
  .word 408576301
  .word 3063012070
  .word 1422480543
  .word 4076916312
  .word 2436384785
  .word 795853258
  .word 3450289027
  .word 1809757500
  .word 169225973
  .word 2823661742
  .word 1183130215
  .word 3837565984
  .word 2197034457
  .word 556502930
  .word 3210938699
  .word 1570407172
  .word 4224842941
  .word 2584311414
  .word 943779887
  .word 3598215656
  .word 1957684129
  .word 317152602
  .word 2971588371
  .word 1331056844
  .word 3985492613
  .word 2344961086
  .word 704429559
  .word 3358865328
  .word 1718333801
  .word 77802274
  .word 2732238043
  .word 1091706516
  .word 3746142285
  .word 2105610758
  .word 465079231
  .word 3119515000
  .word 1478983473
  .word 4133419242
  .word 2492887715
  .word 852356188
  .word 3506791957
  .word 1866260430
  .word 225728903
.section .bss
.balign 4
snapshot: .space 32
