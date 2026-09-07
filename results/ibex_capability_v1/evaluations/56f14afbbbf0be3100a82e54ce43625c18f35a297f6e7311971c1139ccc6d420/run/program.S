.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 31
  li a3, 4294967295
  li a4, 0
  li a5, 1
  li a6, 4294967295
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 84412
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 2048
.Lloop0:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a3, 0(t2)
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
  .word 2423915847
  .word 783384320
  .word 3437820089
  .word 1797288562
  .word 156757035
  .word 2811192804
  .word 1170661277
  .word 3825097046
  .word 2184565519
  .word 544033992
  .word 3198469761
  .word 1557938234
  .word 4212374003
  .word 2571842476
  .word 931310949
  .word 3585746718
  .word 1945215191
  .word 304683664
  .word 2959119433
  .word 1318587906
  .word 3973023675
  .word 2332492148
  .word 691960621
  .word 3346396390
  .word 1705864863
  .word 65333336
  .word 2719769105
  .word 1079237578
  .word 3733673347
  .word 2093141820
  .word 452610293
  .word 3107046062
  .word 1466514535
  .word 4120950304
  .word 2480418777
  .word 839887250
  .word 3494323019
  .word 1853791492
  .word 213259965
  .word 2867695734
  .word 1227164207
  .word 3881599976
  .word 2241068449
  .word 600536922
  .word 3254972691
  .word 1614441164
  .word 4268876933
  .word 2628345406
  .word 987813879
  .word 3642249648
  .word 2001718121
  .word 361186594
  .word 3015622363
  .word 1375090836
  .word 4029526605
  .word 2388995078
  .word 748463551
  .word 3402899320
  .word 1762367793
  .word 121836266
  .word 2776272035
  .word 1135740508
  .word 3790176277
  .word 2149644750
.section .bss
.balign 4
snapshot: .space 32
