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
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 512
.Lloop1:
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop1
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
  .word 11223344
  .word 2665659113
  .word 1025127586
  .word 3679563355
  .word 2039031828
  .word 398500301
  .word 3052936070
  .word 1412404543
  .word 4066840312
  .word 2426308785
  .word 785777258
  .word 3440213027
  .word 1799681500
  .word 159149973
  .word 2813585742
  .word 1173054215
  .word 3827489984
  .word 2186958457
  .word 546426930
  .word 3200862699
  .word 1560331172
  .word 4214766941
  .word 2574235414
  .word 933703887
  .word 3588139656
  .word 1947608129
  .word 307076602
  .word 2961512371
  .word 1320980844
  .word 3975416613
  .word 2334885086
  .word 694353559
  .word 3348789328
  .word 1708257801
  .word 67726274
  .word 2722162043
  .word 1081630516
  .word 3736066285
  .word 2095534758
  .word 455003231
  .word 3109439000
  .word 1468907473
  .word 4123343242
  .word 2482811715
  .word 842280188
  .word 3496715957
  .word 1856184430
  .word 215652903
  .word 2870088672
  .word 1229557145
  .word 3883992914
  .word 2243461387
  .word 602929860
  .word 3257365629
  .word 1616834102
  .word 4271269871
  .word 2630738344
  .word 990206817
  .word 3644642586
  .word 2004111059
  .word 363579532
  .word 3018015301
  .word 1377483774
  .word 4031919543
.section .bss
.balign 4
snapshot: .space 32
