.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 31
  li a2, 1767434204
  li a3, 17
  li a4, 17
  li a5, 4294967295
  li a6, 31
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 5529
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 94
.Lloop0:
  mul a5, a2, a0
  mul a4, a3, a0
  mul a3, a1, a1
  mul a5, a2, a0
  mul a2, a5, a1
  mul a7, a4, a0
  mul a7, a2, a1
  mul a7, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 44990
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 552
.Lloop1:
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 59754
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 22
.Lloop2:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a5, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 59825
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 16
.Lloop3:
  mul a3, a3, a0
  mul a4, a2, a0
  addi t6, t6, -1
  bnez t6, .Lloop3
  li s9, 108579
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 224
.Lloop4:
  mul a7, a0, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  li s9, 111706
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 85
.Lloop5:
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a2, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a3, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop5
  li s9, 128894
  add s9, s9, s10
.Lrelease6:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease6
  li t6, 460
.Lloop6:
  andi t2, a5, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
  andi t2, a4, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop6
  li s9, 135784
  add s9, s9, s10
.Lrelease7:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease7
  li t6, 190
.Lloop7:
  and a5, a4, a5
  xor a2, a0, a0
  xor a2, a1, a4
  sll a0, a4, a6
  addi t6, t6, -1
  bnez t6, .Lloop7
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
  .word 2308195915
  .word 667664388
  .word 3322100157
  .word 1681568630
  .word 41037103
  .word 2695472872
  .word 1054941345
  .word 3709377114
  .word 2068845587
  .word 428314060
  .word 3082749829
  .word 1442218302
  .word 4096654071
  .word 2456122544
  .word 815591017
  .word 3470026786
  .word 1829495259
  .word 188963732
  .word 2843399501
  .word 1202867974
  .word 3857303743
  .word 2216772216
  .word 576240689
  .word 3230676458
  .word 1590144931
  .word 4244580700
  .word 2604049173
  .word 963517646
  .word 3617953415
  .word 1977421888
  .word 336890361
  .word 2991326130
  .word 1350794603
  .word 4005230372
  .word 2364698845
  .word 724167318
  .word 3378603087
  .word 1738071560
  .word 97540033
  .word 2751975802
  .word 1111444275
  .word 3765880044
  .word 2125348517
  .word 484816990
  .word 3139252759
  .word 1498721232
  .word 4153157001
  .word 2512625474
  .word 872093947
  .word 3526529716
  .word 1885998189
  .word 245466662
  .word 2899902431
  .word 1259370904
  .word 3913806673
  .word 2273275146
  .word 632743619
  .word 3287179388
  .word 1646647861
  .word 6116334
  .word 2660552103
  .word 1020020576
  .word 3674456345
  .word 2033924818
.section .bss
.balign 4
snapshot: .space 32
