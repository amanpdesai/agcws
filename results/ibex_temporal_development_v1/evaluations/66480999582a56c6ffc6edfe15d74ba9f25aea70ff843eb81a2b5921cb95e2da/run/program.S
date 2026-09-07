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
  sll a0, a0, a1
  srl a1, a1, a2
  and a2, a2, a3
  or a3, a3, a4
  add a4, a4, a5
  xor a5, a5, a6
  andi t2, a7, 63
  slli t2, t2, 2
  add t2, s1, t2
  lw a6, 0(t2)
  andi t2, a0, 63
  slli t2, t2, 2
  add t2, s1, t2
  sw a1, 0(t2)
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
