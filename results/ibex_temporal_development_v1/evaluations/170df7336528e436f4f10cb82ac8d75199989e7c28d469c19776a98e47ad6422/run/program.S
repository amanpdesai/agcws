.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 4294967295
  li a2, 0
  li a3, 4294967295
  li a4, 0
  li a5, 4294967295
  li a6, 0
  li a7, 4294967295
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
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a0, 0(t2)
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 40000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 256
.Lloop1:
  sll a2, a0, a1
  srl a4, a2, a3
  and a6, a4, a5
  or a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 80000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  bnez a0, .Lskip2_0
  mv a1, a0
.Lskip2_0:
  bnez a1, .Lskip2_1
  mv a2, a1
.Lskip2_1:
  bnez a2, .Lskip2_2
  mv a3, a2
.Lskip2_2:
  bnez a3, .Lskip2_3
  mv a4, a3
.Lskip2_3:
  addi t6, t6, -1
  bnez t6, .Lloop2
  li s9, 120000
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 256
.Lloop3:
  mul a2, a0, a1
  mul a4, a2, a3
  divu a6, a4, a5
  andi t2, a6, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a7, 0(t2)
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
  .word 2468135790
  .word 827604263
  .word 3482040032
  .word 1841508505
  .word 200976978
  .word 2855412747
  .word 1214881220
  .word 3869316989
  .word 2228785462
  .word 588253935
  .word 3242689704
  .word 1602158177
  .word 4256593946
  .word 2616062419
  .word 975530892
  .word 3629966661
  .word 1989435134
  .word 348903607
  .word 3003339376
  .word 1362807849
  .word 4017243618
  .word 2376712091
  .word 736180564
  .word 3390616333
  .word 1750084806
  .word 109553279
  .word 2763989048
  .word 1123457521
  .word 3777893290
  .word 2137361763
  .word 496830236
  .word 3151266005
  .word 1510734478
  .word 4165170247
  .word 2524638720
  .word 884107193
  .word 3538542962
  .word 1898011435
  .word 257479908
  .word 2911915677
  .word 1271384150
  .word 3925819919
  .word 2285288392
  .word 644756865
  .word 3299192634
  .word 1658661107
  .word 18129580
  .word 2672565349
  .word 1032033822
  .word 3686469591
  .word 2045938064
  .word 405406537
  .word 3059842306
  .word 1419310779
  .word 4073746548
  .word 2433215021
  .word 792683494
  .word 3447119263
  .word 1806587736
  .word 166056209
  .word 2820491978
  .word 1179960451
  .word 3834396220
  .word 2193864693
.section .bss
.balign 4
snapshot: .space 32
