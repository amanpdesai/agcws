# ibex — bit-activity v2 qualification

18/18 requests qualified under the corrected known-bit-transition metric:
eight nonflat families and one control in each of two engineering splits.
These are activity targets, not watts and not unseen tasks.

- [Bank and selected witnesses](bank.json)
- [Compressed audit inputs](inputs.json.gz)
- `fixed-replay/`: round-trip-verified compact evidence for all 82 programs,
  including invalid calibration attempts.
- [Independent waveform checks](../../bit_activity_v2/README.md)

Offline check: `.venv/bin/python analysis/verify_bit_archive.py results/ibex/bit-activity-v2`.
Raw VCD/FST files are scratch; they are not embedded in the compact archive.
The input bundle retains target and calibration freezes, original programs,
measurements, all qualification attempts and cross-solve arithmetic.

The runtime correction is commit b77cd9c56. The frozen manifest records exact
source hashes, image identity and the simulator binary hash where applicable.
Old v6 banks and first-round diagnostics remain unchanged.
No LLM calls were made; full comparative runs are not launched or authorized.
