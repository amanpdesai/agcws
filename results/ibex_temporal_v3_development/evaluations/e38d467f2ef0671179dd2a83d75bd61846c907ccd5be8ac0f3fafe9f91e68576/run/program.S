.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 0
  li a1, 0
  li a2, 0
  li a3, 0
  li a4, 0
  li a5, 0
  li a6, 0
  li a7, 0
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
  li s9, 0
  add s9, s9, s10
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
  li t6, 819
.Lloop0:
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  divu a0, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a0, a0, a1
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
  .word 12346
  .word 2654448115
  .word 1013916588
  .word 3668352357
  .word 2027820830
  .word 387289303
  .word 3041725072
  .word 1401193545
  .word 4055629314
  .word 2415097787
  .word 774566260
  .word 3429002029
  .word 1788470502
  .word 147938975
  .word 2802374744
  .word 1161843217
  .word 3816278986
  .word 2175747459
  .word 535215932
  .word 3189651701
  .word 1549120174
  .word 4203555943
  .word 2563024416
  .word 922492889
  .word 3576928658
  .word 1936397131
  .word 295865604
  .word 2950301373
  .word 1309769846
  .word 3964205615
  .word 2323674088
  .word 683142561
  .word 3337578330
  .word 1697046803
  .word 56515276
  .word 2710951045
  .word 1070419518
  .word 3724855287
  .word 2084323760
  .word 443792233
  .word 3098228002
  .word 1457696475
  .word 4112132244
  .word 2471600717
  .word 831069190
  .word 3485504959
  .word 1844973432
  .word 204441905
  .word 2858877674
  .word 1218346147
  .word 3872781916
  .word 2232250389
  .word 591718862
  .word 3246154631
  .word 1605623104
  .word 4260058873
  .word 2619527346
  .word 978995819
  .word 3633431588
  .word 1992900061
  .word 352368534
  .word 3006804303
  .word 1366272776
  .word 4020708545
.section .bss
.balign 4
snapshot: .space 32
