.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 1
  li a3, 17
  li a4, 1244369640
  li a5, 31
  li a6, 0
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 19186
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 408
.Lloop0:
  mul a1, a3, a6
  addi t6, t6, -1
  bnez t6, .Lloop0
.global agcws_segment_1_setup
agcws_segment_1_setup:
  li s9, 22005
  add s9, s9, s10
.global agcws_segment_1_poll
agcws_segment_1_poll:
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
.global agcws_segment_1_body
agcws_segment_1_body:
  li t6, 1344
.Lloop1:
  mul a0, a2, a6
  mul a3, a4, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
.global agcws_segment_2_setup
agcws_segment_2_setup:
  li s9, 53807
  add s9, s9, s10
.global agcws_segment_2_poll
agcws_segment_2_poll:
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
.global agcws_segment_2_body
agcws_segment_2_body:
  li t6, 74
.Lloop2:
  bnez a5, .Lskip2_0
  mv a2, a1
.Lskip2_0:
  bnez a3, .Lskip2_1
  mv a6, a1
.Lskip2_1:
  bnez a4, .Lskip2_2
  mv a2, a1
.Lskip2_2:
  bnez a4, .Lskip2_3
  mv a3, a1
.Lskip2_3:
  addi t6, t6, -1
  bnez t6, .Lloop2
.global agcws_segment_3_setup
agcws_segment_3_setup:
  li s9, 160135
  add s9, s9, s10
.global agcws_segment_3_poll
agcws_segment_3_poll:
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
.global agcws_segment_3_body
agcws_segment_3_body:
  li t6, 176
.Lloop3:
  divu a2, a7, a6
  divu a3, a7, a5
  divu a4, a5, a5
  divu a5, a7, a0
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
  .word 1341324573
  .word 3995760342
  .word 2355228815
  .word 714697288
  .word 3369133057
  .word 1728601530
  .word 88070003
  .word 2742505772
  .word 1101974245
  .word 3756410014
  .word 2115878487
  .word 475346960
  .word 3129782729
  .word 1489251202
  .word 4143686971
  .word 2503155444
  .word 862623917
  .word 3517059686
  .word 1876528159
  .word 235996632
  .word 2890432401
  .word 1249900874
  .word 3904336643
  .word 2263805116
  .word 623273589
  .word 3277709358
  .word 1637177831
  .word 4291613600
  .word 2651082073
  .word 1010550546
  .word 3664986315
  .word 2024454788
  .word 383923261
  .word 3038359030
  .word 1397827503
  .word 4052263272
  .word 2411731745
  .word 771200218
  .word 3425635987
  .word 1785104460
  .word 144572933
  .word 2799008702
  .word 1158477175
  .word 3812912944
  .word 2172381417
  .word 531849890
  .word 3186285659
  .word 1545754132
  .word 4200189901
  .word 2559658374
  .word 919126847
  .word 3573562616
  .word 1933031089
  .word 292499562
  .word 2946935331
  .word 1306403804
  .word 3960839573
  .word 2320308046
  .word 679776519
  .word 3334212288
  .word 1693680761
  .word 53149234
  .word 2707585003
  .word 1067053476
.section .bss
.balign 4
snapshot: .space 32
