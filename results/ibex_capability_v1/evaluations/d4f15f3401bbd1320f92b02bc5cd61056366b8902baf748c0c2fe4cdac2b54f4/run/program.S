.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 123
  li a1, 456
  li a2, 789
  li a3, 101112
  li a4, 131415
  li a5, 161718
  li a6, 192021
  li a7, 222324
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 5000
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 341
.Lloop0:
  mul a1, a0, a1
  add a2, a1, a2
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  mul a1, a0, a1
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 30000
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 341
.Lloop1:
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  xor a5, a4, a5
  mul a4, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 55000
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 341
.Lloop2:
  sll a6, a5, a2
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  add a7, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
  sll a6, a5, a2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 80000
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 341
.Lloop3:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  mul a1, a0, a1
  srl a2, a1, a2
  addi t6, t6, -1
  bnez t6, .Lloop3
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
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
  .word 555555555
  .word 3209991324
  .word 1569459797
  .word 4223895566
  .word 2583364039
  .word 942832512
  .word 3597268281
  .word 1956736754
  .word 316205227
  .word 2970640996
  .word 1330109469
  .word 3984545238
  .word 2344013711
  .word 703482184
  .word 3357917953
  .word 1717386426
  .word 76854899
  .word 2731290668
  .word 1090759141
  .word 3745194910
  .word 2104663383
  .word 464131856
  .word 3118567625
  .word 1478036098
  .word 4132471867
  .word 2491940340
  .word 851408813
  .word 3505844582
  .word 1865313055
  .word 224781528
  .word 2879217297
  .word 1238685770
  .word 3893121539
  .word 2252590012
  .word 612058485
  .word 3266494254
  .word 1625962727
  .word 4280398496
  .word 2639866969
  .word 999335442
  .word 3653771211
  .word 2013239684
  .word 372708157
  .word 3027143926
  .word 1386612399
  .word 4041048168
  .word 2400516641
  .word 759985114
  .word 3414420883
  .word 1773889356
  .word 133357829
  .word 2787793598
  .word 1147262071
  .word 3801697840
  .word 2161166313
  .word 520634786
  .word 3175070555
  .word 1534539028
  .word 4188974797
  .word 2548443270
  .word 907911743
  .word 3562347512
  .word 1921815985
  .word 281284458
.section .bss
.balign 4
snapshot: .space 32
