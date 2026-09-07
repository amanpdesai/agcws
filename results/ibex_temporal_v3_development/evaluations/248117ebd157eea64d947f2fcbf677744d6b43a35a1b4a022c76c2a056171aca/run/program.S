.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1
  li a1, 1
  li a2, 0
  li a3, 17
  li a4, 4294967295
  li a5, 31
  li a6, 17
  li a7, 31
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 29922
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 2048
.Lloop0:
  or a6, a5, a6
  divu a6, a4, a3
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
  .word 200127142
  .word 2854562911
  .word 1214031384
  .word 3868467153
  .word 2227935626
  .word 587404099
  .word 3241839868
  .word 1601308341
  .word 4255744110
  .word 2615212583
  .word 974681056
  .word 3629116825
  .word 1988585298
  .word 348053771
  .word 3002489540
  .word 1361958013
  .word 4016393782
  .word 2375862255
  .word 735330728
  .word 3389766497
  .word 1749234970
  .word 108703443
  .word 2763139212
  .word 1122607685
  .word 3777043454
  .word 2136511927
  .word 495980400
  .word 3150416169
  .word 1509884642
  .word 4164320411
  .word 2523788884
  .word 883257357
  .word 3537693126
  .word 1897161599
  .word 256630072
  .word 2911065841
  .word 1270534314
  .word 3924970083
  .word 2284438556
  .word 643907029
  .word 3298342798
  .word 1657811271
  .word 17279744
  .word 2671715513
  .word 1031183986
  .word 3685619755
  .word 2045088228
  .word 404556701
  .word 3058992470
  .word 1418460943
  .word 4072896712
  .word 2432365185
  .word 791833658
  .word 3446269427
  .word 1805737900
  .word 165206373
  .word 2819642142
  .word 1179110615
  .word 3833546384
  .word 2193014857
  .word 552483330
  .word 3206919099
  .word 1566387572
  .word 4220823341
.section .bss
.balign 4
snapshot: .space 32
