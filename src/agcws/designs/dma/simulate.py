"""Invoke the packaged DMA tool recipe without depending on a source checkout."""

import subprocess
import sys
from pathlib import Path


def main(argv=None):
    subprocess.run(["bash", str(Path(__file__).with_name("run_rtl.sh")),
                    *(sys.argv[1:] if argv is None else argv)], check=True)


if __name__ == "__main__":
    main()
