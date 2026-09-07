.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 1638900404
  li a1, 17
  li a2, 4137086435
  li a3, 31
  li a4, 1
  li a5, 17
  li a6, 31
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 26067
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 1520
.Lloop0:
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a2, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a7, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 144058
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 41
.Lloop1:
  or a6, a4, a2
  xor a2, a3, a2
  xor a3, a2, a0
  or a5, a2, a2
  or a6, a7, a3
  or a5, a6, a1
  sll a6, a6, a6
  sll a3, a5, a5
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 87906
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 364
.Lloop2:
  mul a5, a4, a1
  mul a0, a7, a0
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
  .word 882933601
  .word 3537369370
  .word 1896837843
  .word 256306316
  .word 2910742085
  .word 1270210558
  .word 3924646327
  .word 2284114800
  .word 643583273
  .word 3298019042
  .word 1657487515
  .word 16955988
  .word 2671391757
  .word 1030860230
  .word 3685295999
  .word 2044764472
  .word 404232945
  .word 3058668714
  .word 1418137187
  .word 4072572956
  .word 2432041429
  .word 791509902
  .word 3445945671
  .word 1805414144
  .word 164882617
  .word 2819318386
  .word 1178786859
  .word 3833222628
  .word 2192691101
  .word 552159574
  .word 3206595343
  .word 1566063816
  .word 4220499585
  .word 2579968058
  .word 939436531
  .word 3593872300
  .word 1953340773
  .word 312809246
  .word 2967245015
  .word 1326713488
  .word 3981149257
  .word 2340617730
  .word 700086203
  .word 3354521972
  .word 1713990445
  .word 73458918
  .word 2727894687
  .word 1087363160
  .word 3741798929
  .word 2101267402
  .word 460735875
  .word 3115171644
  .word 1474640117
  .word 4129075886
  .word 2488544359
  .word 848012832
  .word 3502448601
  .word 1861917074
  .word 221385547
  .word 2875821316
  .word 1235289789
  .word 3889725558
  .word 2249194031
  .word 608662504
.section .bss
.balign 4
snapshot: .space 32
