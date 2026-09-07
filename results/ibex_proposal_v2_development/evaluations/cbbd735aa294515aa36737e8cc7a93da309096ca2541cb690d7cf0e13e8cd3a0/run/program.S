.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 1
  li a2, 0
  li a3, 1
  li a4, 4294967295
  li a5, 2807450333
  li a6, 0
  li a7, 2671303109
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 6504
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 233
.Lloop0:
  bnez a4, .Lskip0_0
  mv a0, a0
.Lskip0_0:
  bnez a5, .Lskip0_1
  mv a1, a0
.Lskip0_1:
  bnez a4, .Lskip0_2
  mv a7, a7
.Lskip0_2:
  bnez a2, .Lskip0_3
  mv a4, a6
.Lskip0_3:
  bnez a2, .Lskip0_4
  mv a3, a2
.Lskip0_4:
  bnez a2, .Lskip0_5
  mv a5, a2
.Lskip0_5:
  bnez a7, .Lskip0_6
  mv a2, a3
.Lskip0_6:
  bnez a5, .Lskip0_7
  mv a4, a7
.Lskip0_7:
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 25996
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 262
.Lloop1:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 78171
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 57
.Lloop2:
  add a0, a6, a4
  and a0, a6, a2
  add a4, a2, a6
  sll a7, a1, a2
  divu a2, a3, a0
  add a6, a1, a5
  add a4, a4, a0
  and a6, a5, a6
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 83296
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 276
.Lloop3:
  bnez a0, .Lskip3_0
  mv a0, a3
.Lskip3_0:
  bnez a2, .Lskip3_1
  mv a1, a5
.Lskip3_1:
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 116220
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 22
.Lloop4:
  srl a6, a2, a0
  sll a4, a4, a1
  xor a3, a3, a0
  xor a7, a7, a0
  sll a5, a2, a0
  sll a6, a0, a0
  srl a3, a6, a1
  add a7, a4, a1
  addi t6, t6, -1
  bnez t6, .Lloop4
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
  .word 2559078401
  .word 918546874
  .word 3572982643
  .word 1932451116
  .word 291919589
  .word 2946355358
  .word 1305823831
  .word 3960259600
  .word 2319728073
  .word 679196546
  .word 3333632315
  .word 1693100788
  .word 52569261
  .word 2707005030
  .word 1066473503
  .word 3720909272
  .word 2080377745
  .word 439846218
  .word 3094281987
  .word 1453750460
  .word 4108186229
  .word 2467654702
  .word 827123175
  .word 3481558944
  .word 1841027417
  .word 200495890
  .word 2854931659
  .word 1214400132
  .word 3868835901
  .word 2228304374
  .word 587772847
  .word 3242208616
  .word 1601677089
  .word 4256112858
  .word 2615581331
  .word 975049804
  .word 3629485573
  .word 1988954046
  .word 348422519
  .word 3002858288
  .word 1362326761
  .word 4016762530
  .word 2376231003
  .word 735699476
  .word 3390135245
  .word 1749603718
  .word 109072191
  .word 2763507960
  .word 1122976433
  .word 3777412202
  .word 2136880675
  .word 496349148
  .word 3150784917
  .word 1510253390
  .word 4164689159
  .word 2524157632
  .word 883626105
  .word 3538061874
  .word 1897530347
  .word 256998820
  .word 2911434589
  .word 1270903062
  .word 3925338831
  .word 2284807304
.section .bss
.balign 4
snapshot: .space 32
