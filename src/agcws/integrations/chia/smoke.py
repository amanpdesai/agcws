#!/usr/bin/env python3
"""Verify the locally installed CHIA package and Ray execution substrate."""

import ray


def main() -> None:
    import chia.base.ChiaFunction  # noqa: F401  (verify CHIA package imports)

    ray.init(
        include_dashboard=False,
        num_cpus=1,
        ignore_reinit_error=True,
        logging_level="ERROR",
    )

    @ray.remote
    def identity(value: str) -> str:
        return value

    try:
        result = ray.get(identity.remote("agcws-chia-smoke"))
    finally:
        ray.shutdown()

    if result != "agcws-chia-smoke":
        raise RuntimeError(f"unexpected Ray result: {result!r}")
    print("AGCWS_CHIA_SMOKE_OK")


if __name__ == "__main__":
    main()
