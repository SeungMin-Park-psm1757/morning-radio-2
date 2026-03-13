from __future__ import annotations

from .config import build_parser, load_weekly_quantum_config
from .pipeline import run_weekly_quantum_pipeline


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_weekly_quantum_config(args)
    run_dir = run_weekly_quantum_pipeline(config)
    print(f"[weekly-quantum] completed run: {run_dir}")


if __name__ == "__main__":
    main()
