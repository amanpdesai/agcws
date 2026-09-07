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
  li s9, 9569
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 280
.Lloop0:
  add a5, a7, a5
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a5, a4, a6
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a3, 0(t2)
  divu a0, a6, a3
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a6, 0(t2)
  srl a3, a4, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 28578
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 44
.Lloop1:
  bnez a4, .Lskip1_0
  mv a3, a0
.Lskip1_0:
  divu a1, a5, a2
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 99114
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 240
.Lloop2:
  bnez a5, .Lskip2_0
  mv a3, a0
.Lskip2_0:
  divu a7, a0, a3
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 122339
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 161
.Lloop3:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  xor a4, a0, a3
  srl a4, a4, a5
  bnez a4, .Lskip3_3
  mv a2, a5
.Lskip3_3:
  divu a7, a7, a7
  add a2, a3, a3
  bnez a3, .Lskip3_6
  mv a3, a7
.Lskip3_6:
  xor a0, a3, a4
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
  .word 999465600
  .word 3653901369
  .word 2013369842
  .word 372838315
  .word 3027274084
  .word 1386742557
  .word 4041178326
  .word 2400646799
  .word 760115272
  .word 3414551041
  .word 1774019514
  .word 133487987
  .word 2787923756
  .word 1147392229
  .word 3801827998
  .word 2161296471
  .word 520764944
  .word 3175200713
  .word 1534669186
  .word 4189104955
  .word 2548573428
  .word 908041901
  .word 3562477670
  .word 1921946143
  .word 281414616
  .word 2935850385
  .word 1295318858
  .word 3949754627
  .word 2309223100
  .word 668691573
  .word 3323127342
  .word 1682595815
  .word 42064288
  .word 2696500057
  .word 1055968530
  .word 3710404299
  .word 2069872772
  .word 429341245
  .word 3083777014
  .word 1443245487
  .word 4097681256
  .word 2457149729
  .word 816618202
  .word 3471053971
  .word 1830522444
  .word 189990917
  .word 2844426686
  .word 1203895159
  .word 3858330928
  .word 2217799401
  .word 577267874
  .word 3231703643
  .word 1591172116
  .word 4245607885
  .word 2605076358
  .word 964544831
  .word 3618980600
  .word 1978449073
  .word 337917546
  .word 2992353315
  .word 1351821788
  .word 4006257557
  .word 2365726030
  .word 725194503
.section .bss
.balign 4
snapshot: .space 32
