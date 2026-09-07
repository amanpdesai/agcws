.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 10
  li a1, 20
  li a2, 30
  li a3, 40
  li a4, 50
  li a5, 60
  li a6, 70
  li a7, 80
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
  add a2, a0, a1
  add a2, a0, a1
  add a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop0
  li s9, 10000
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 2048
.Lloop1:
  divu a2, a0, a1
  addi t6, t6, -1
  bnez t6, .Lloop1
  li s9, 30000
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 256
.Lloop2:
  add a2, a0, a1
  add a2, a0, a1
  add a2, a0, a1
  add a2, a0, a1
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
  .word 2002
  .word 2654437771
  .word 1013906244
  .word 3668342013
  .word 2027810486
  .word 387278959
  .word 3041714728
  .word 1401183201
  .word 4055618970
  .word 2415087443
  .word 774555916
  .word 3428991685
  .word 1788460158
  .word 147928631
  .word 2802364400
  .word 1161832873
  .word 3816268642
  .word 2175737115
  .word 535205588
  .word 3189641357
  .word 1549109830
  .word 4203545599
  .word 2563014072
  .word 922482545
  .word 3576918314
  .word 1936386787
  .word 295855260
  .word 2950291029
  .word 1309759502
  .word 3964195271
  .word 2323663744
  .word 683132217
  .word 3337567986
  .word 1697036459
  .word 56504932
  .word 2710940701
  .word 1070409174
  .word 3724844943
  .word 2084313416
  .word 443781889
  .word 3098217658
  .word 1457686131
  .word 4112121900
  .word 2471590373
  .word 831058846
  .word 3485494615
  .word 1844963088
  .word 204431561
  .word 2858867330
  .word 1218335803
  .word 3872771572
  .word 2232240045
  .word 591708518
  .word 3246144287
  .word 1605612760
  .word 4260048529
  .word 2619517002
  .word 978985475
  .word 3633421244
  .word 1992889717
  .word 352358190
  .word 3006793959
  .word 1366262432
  .word 4020698201
.section .bss
.balign 4
snapshot: .space 32
