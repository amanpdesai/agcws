.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 464432913
  li a1, 31
  li a2, 1
  li a3, 17
  li a4, 4294967295
  li a5, 1
  li a6, 0
  li a7, 17
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 8595
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 4096
.Lloop0:
  divu a7, a2, a6
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
  .word 4076711433
  .word 2436179906
  .word 795648379
  .word 3450084148
  .word 1809552621
  .word 169021094
  .word 2823456863
  .word 1182925336
  .word 3837361105
  .word 2196829578
  .word 556298051
  .word 3210733820
  .word 1570202293
  .word 4224638062
  .word 2584106535
  .word 943575008
  .word 3598010777
  .word 1957479250
  .word 316947723
  .word 2971383492
  .word 1330851965
  .word 3985287734
  .word 2344756207
  .word 704224680
  .word 3358660449
  .word 1718128922
  .word 77597395
  .word 2732033164
  .word 1091501637
  .word 3745937406
  .word 2105405879
  .word 464874352
  .word 3119310121
  .word 1478778594
  .word 4133214363
  .word 2492682836
  .word 852151309
  .word 3506587078
  .word 1866055551
  .word 225524024
  .word 2879959793
  .word 1239428266
  .word 3893864035
  .word 2253332508
  .word 612800981
  .word 3267236750
  .word 1626705223
  .word 4281140992
  .word 2640609465
  .word 1000077938
  .word 3654513707
  .word 2013982180
  .word 373450653
  .word 3027886422
  .word 1387354895
  .word 4041790664
  .word 2401259137
  .word 760727610
  .word 3415163379
  .word 1774631852
  .word 134100325
  .word 2788536094
  .word 1148004567
  .word 3802440336
.section .bss
.balign 4
snapshot: .space 32
