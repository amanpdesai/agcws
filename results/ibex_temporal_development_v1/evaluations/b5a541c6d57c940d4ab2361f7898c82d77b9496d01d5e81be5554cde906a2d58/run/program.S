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
  li t6, 256
.Lloop0:
  add a0, a0, a1
  xor a1, a2, a3
  mul a2, a4, a5
  divu a3, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 50000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a4, 0(t2)
  andi t2, a1, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a5, 0(t2)
  sll a5, a2, a6
  srl a6, a3, a7
  bnez a4, .Lskip1_4
  mv a7, a0
.Lskip1_4:
  or a0, a5, a1
  and a1, a6, a2
  add a2, a7, a3
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 100000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  xor a3, a0, a1
  sll a4, a2, a3
  divu a5, a4, a5
  mul a6, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop2
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
  .word 3456789012
  .word 1816257485
  .word 175725958
  .word 2830161727
  .word 1189630200
  .word 3844065969
  .word 2203534442
  .word 563002915
  .word 3217438684
  .word 1576907157
  .word 4231342926
  .word 2590811399
  .word 950279872
  .word 3604715641
  .word 1964184114
  .word 323652587
  .word 2978088356
  .word 1337556829
  .word 3991992598
  .word 2351461071
  .word 710929544
  .word 3365365313
  .word 1724833786
  .word 84302259
  .word 2738738028
  .word 1098206501
  .word 3752642270
  .word 2112110743
  .word 471579216
  .word 3126014985
  .word 1485483458
  .word 4139919227
  .word 2499387700
  .word 858856173
  .word 3513291942
  .word 1872760415
  .word 232228888
  .word 2886664657
  .word 1246133130
  .word 3900568899
  .word 2260037372
  .word 619505845
  .word 3273941614
  .word 1633410087
  .word 4287845856
  .word 2647314329
  .word 1006782802
  .word 3661218571
  .word 2020687044
  .word 380155517
  .word 3034591286
  .word 1394059759
  .word 4048495528
  .word 2407964001
  .word 767432474
  .word 3421868243
  .word 1781336716
  .word 140805189
  .word 2795240958
  .word 1154709431
  .word 3809145200
  .word 2168613673
  .word 528082146
  .word 3182517915
.section .bss
.balign 4
snapshot: .space 32
