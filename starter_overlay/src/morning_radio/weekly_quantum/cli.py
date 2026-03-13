from __future__ import annotations

from .config import load_weekly_quantum_config
from .pipeline import run_weekly_quantum_pipeline


def main() -> None:
    config = load_weekly_quantum_config()
    run_dir = run_weekly_quantum_pipeline(config)
    print(f"[weekly-quantum] completed scaffold run: {run_dir}")


if __name__ == "__main__":
    main()
