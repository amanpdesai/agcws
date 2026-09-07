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
  li t6, 56
.Lloop0:
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop0
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  li s9, 0
  add s9, s9, s10
.Lrelease1:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease1
  li t6, 113
.Lloop1:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop1
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  li s9, 0
  add s9, s9, s10
.Lrelease2:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease2
  li t6, 56
.Lloop2:
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop2
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  li s9, 0
  add s9, s9, s10
.Lrelease3:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease3
  li t6, 113
.Lloop3:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop3
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
  li s9, 0
  add s9, s9, s10
.Lrelease4:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease4
  li t6, 56
.Lloop4:
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  divu a7, a7, a0
  addi t6, t6, -1
  bnez t6, .Lloop4
  divu a0, a0, a0
  divu a1, a1, a0
  divu a2, a2, a0
  divu a3, a3, a0
  divu a4, a4, a0
  divu a5, a5, a0
  divu a6, a6, a0
  li s9, 0
  add s9, s9, s10
.Lrelease5:
  csrr t0, mcycle
  bltu t0, s9, .Lrelease5
  li t6, 113
.Lloop5:
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  addi t6, t6, -1
  bnez t6, .Lloop5
  add a2, a0, a1
  add a4, a2, a3
  add a6, a4, a5
  add a0, a6, a7
  add a2, a0, a1
  add a4, a2, a3
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
  .word 3341289840
  .word 1700758313
  .word 60226786
  .word 2714662555
  .word 1074131028
  .word 3728566797
  .word 2088035270
  .word 447503743
  .word 3101939512
  .word 1461407985
  .word 4115843754
  .word 2475312227
  .word 834780700
  .word 3489216469
  .word 1848684942
  .word 208153415
  .word 2862589184
  .word 1222057657
  .word 3876493426
  .word 2235961899
  .word 595430372
  .word 3249866141
  .word 1609334614
  .word 4263770383
  .word 2623238856
  .word 982707329
  .word 3637143098
  .word 1996611571
  .word 356080044
  .word 3010515813
  .word 1369984286
  .word 4024420055
  .word 2383888528
  .word 743357001
  .word 3397792770
  .word 1757261243
  .word 116729716
  .word 2771165485
  .word 1130633958
  .word 3785069727
  .word 2144538200
  .word 504006673
  .word 3158442442
  .word 1517910915
  .word 4172346684
  .word 2531815157
  .word 891283630
  .word 3545719399
  .word 1905187872
  .word 264656345
  .word 2919092114
  .word 1278560587
  .word 3932996356
  .word 2292464829
  .word 651933302
  .word 3306369071
  .word 1665837544
  .word 25306017
  .word 2679741786
  .word 1039210259
  .word 3693646028
  .word 2053114501
  .word 412582974
  .word 3067018743
.section .bss
.balign 4
snapshot: .space 32
