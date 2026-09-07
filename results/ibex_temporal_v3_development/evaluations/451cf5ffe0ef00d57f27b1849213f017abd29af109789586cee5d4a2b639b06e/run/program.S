.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 1
  li a3, 1
  li a4, 1
  li a5, 1
  li a6, 1
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 113
.Lloop0:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  li s9, 25000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 76
.Lloop1:
  bnez a0, .Lskip1_0
  mv a0, a1
.Lskip1_0:
  bnez a1, .Lskip1_1
  mv a1, a2
.Lskip1_1:
  bnez a2, .Lskip1_2
  mv a2, a3
.Lskip1_2:
  bnez a3, .Lskip1_3
  mv a3, a4
.Lskip1_3:
  bnez a4, .Lskip1_4
  mv a4, a5
.Lskip1_4:
  bnez a5, .Lskip1_5
  mv a5, a6
.Lskip1_5:
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 50000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 233
.Lloop2:
  divu a0, a0, a0
  divu a1, a2, a0
  divu a2, a4, a0
  divu a3, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a0
  li s9, 100000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 233
.Lloop3:
  divu a4, a0, a0
  divu a5, a2, a0
  divu a6, a4, a0
  divu a7, a6, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  divu a4, a0, a0
  li s9, 150000
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 75
.Lloop4:
  bnez a0, .Lskip4_0
  mv a0, a1
.Lskip4_0:
  bnez a1, .Lskip4_1
  mv a1, a2
.Lskip4_1:
  bnez a2, .Lskip4_2
  mv a2, a3
.Lskip4_2:
  bnez a3, .Lskip4_3
  mv a3, a4
.Lskip4_3:
  bnez a4, .Lskip4_4
  mv a4, a5
.Lskip4_4:
  bnez a5, .Lskip4_5
  mv a5, a6
.Lskip4_5:
  addi t6, t6, -1
  bnez t6, .Lloop4
  bnez a0, .Ltail_skip4_0
  mv a0, a1
.Ltail_skip4_0:
  bnez a1, .Ltail_skip4_1
  mv a1, a2
.Ltail_skip4_1:
  bnez a2, .Ltail_skip4_2
  mv a2, a3
.Ltail_skip4_2:
  bnez a3, .Ltail_skip4_3
  mv a3, a4
.Ltail_skip4_3:
  bnez a4, .Ltail_skip4_4
  mv a4, a5
.Ltail_skip4_4:
  li s9, 175000
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 51
.Lloop5:
  add a0, a0, a1
  add a1, a1, a2
  add a2, a2, a3
  add a3, a3, a4
  add a4, a4, a5
  add a5, a5, a6
  add a6, a6, a7
  add a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop5
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
  .word 12345
  .word 2654448114
  .word 1013916587
  .word 3668352356
  .word 2027820829
  .word 387289302
  .word 3041725071
  .word 1401193544
  .word 4055629313
  .word 2415097786
  .word 774566259
  .word 3429002028
  .word 1788470501
  .word 147938974
  .word 2802374743
  .word 1161843216
  .word 3816278985
  .word 2175747458
  .word 535215931
  .word 3189651700
  .word 1549120173
  .word 4203555942
  .word 2563024415
  .word 922492888
  .word 3576928657
  .word 1936397130
  .word 295865603
  .word 2950301372
  .word 1309769845
  .word 3964205614
  .word 2323674087
  .word 683142560
  .word 3337578329
  .word 1697046802
  .word 56515275
  .word 2710951044
  .word 1070419517
  .word 3724855286
  .word 2084323759
  .word 443792232
  .word 3098228001
  .word 1457696474
  .word 4112132243
  .word 2471600716
  .word 831069189
  .word 3485504958
  .word 1844973431
  .word 204441904
  .word 2858877673
  .word 1218346146
  .word 3872781915
  .word 2232250388
  .word 591718861
  .word 3246154630
  .word 1605623103
  .word 4260058872
  .word 2619527345
  .word 978995818
  .word 3633431587
  .word 1992900060
  .word 352368533
  .word 3006804302
  .word 1366272775
  .word 4020708544
.section .bss
.balign 4
snapshot: .space 32
