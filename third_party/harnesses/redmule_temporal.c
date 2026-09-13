/* AGCWS timed FP16 GEMM stimulus. Uses the upstream RedMulE HAL and reference data. */
#include <stdint.h>
#include "archi_redmule.h"
#include "hal_redmule.h"
#include "redmule_utils.h"
#include "tensor_dim.h"
#include "golden.h"
#include "w_input.h"
#include "x_input.h"
#include "y_input.h"
#include "workload.h"

int main(void) {
  uint16_t initial_y[M_SIZE * K_SIZE];
  volatile uint16_t *output = y_inp;
  volatile uint32_t *timer = (volatile uint32_t *)0x80000008;
  int errors = 0;
  for (unsigned i = 0; i < M_SIZE * K_SIZE; ++i) initial_y[i] = output[i];
  for (unsigned job = 0; job < sizeof(releases) / sizeof(releases[0]); ++job) {
    while (*timer < releases[job]) {}
    for (unsigned i = 0; i < M_SIZE * K_SIZE; ++i) output[i] = initial_y[i];
    hwpe_cg_enable();
    hwpe_soft_clear();
    while (hwpe_acquire_job() < 0) {}
    redmule_cfg((unsigned)x_inp, (unsigned)w_inp, (unsigned)y_inp,
                M_SIZE, N_SIZE, K_SIZE, 0, GEMM, Float16);
    hwpe_trigger_job();
    asm volatile("wfi" ::: "memory");
    hwpe_cg_disable();
    errors += redmule16_compare_int((uint32_t *)y_inp, golden, M_SIZE * K_SIZE / 2, 0);
    tfp_printf("AGCWS_REDMULE_JOB job=%u cycle=%u errors=%d\n", job, *timer, errors);
    if (errors) break;
  }
  *(volatile int *)0x80000000 = errors;
  return errors;
}
