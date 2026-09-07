.section .text
.option norvc
.global main
main:
  csrwi mcountinhibit, 0
  la s1, data_words
  li a0, 17
  li a1, 1154789837
  li a2, 4294967295
  li a3, 1
  li a4, 17
  li a5, 602019163
  li a6, 4185563966
  li a7, 1
  csrr s10, mcycle
.global measure_start
measure_start:
  addi s11, zero, 1
.global agcws_segment_0_setup
agcws_segment_0_setup:
  li s9, 190885
  add s9, s9, s10
.global agcws_segment_0_poll
agcws_segment_0_poll:
.Lrelease0:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease0
.global agcws_segment_0_body
agcws_segment_0_body:
  li t6, 1024
.Lloop0:
  bnez a2, .Lskip0_0
  mv a5, a2
.Lskip0_0:
  bnez a5, .Lskip0_1
  mv a3, a3
.Lskip0_1:
  bnez a1, .Lskip0_2
  mv a6, a2
.Lskip0_2:
  bnez a1, .Lskip0_3
  mv a5, a1
.Lskip0_3:
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
  .word 3269698266
  .word 1629166739
  .word 4283602508
  .word 2643070981
  .word 1002539454
  .word 3656975223
  .word 2016443696
  .word 375912169
  .word 3030347938
  .word 1389816411
  .word 4044252180
  .word 2403720653
  .word 763189126
  .word 3417624895
  .word 1777093368
  .word 136561841
  .word 2790997610
  .word 1150466083
  .word 3804901852
  .word 2164370325
  .word 523838798
  .word 3178274567
  .word 1537743040
  .word 4192178809
  .word 2551647282
  .word 911115755
  .word 3565551524
  .word 1925019997
  .word 284488470
  .word 2938924239
  .word 1298392712
  .word 3952828481
  .word 2312296954
  .word 671765427
  .word 3326201196
  .word 1685669669
  .word 45138142
  .word 2699573911
  .word 1059042384
  .word 3713478153
  .word 2072946626
  .word 432415099
  .word 3086850868
  .word 1446319341
  .word 4100755110
  .word 2460223583
  .word 819692056
  .word 3474127825
  .word 1833596298
  .word 193064771
  .word 2847500540
  .word 1206969013
  .word 3861404782
  .word 2220873255
  .word 580341728
  .word 3234777497
  .word 1594245970
  .word 4248681739
  .word 2608150212
  .word 967618685
  .word 3622054454
  .word 1981522927
  .word 340991400
  .word 2995427169
.section .bss
.balign 4
snapshot: .space 32
