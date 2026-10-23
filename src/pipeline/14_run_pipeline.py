
"""Validate existing outputs or launch the Streamlit dashboard.

This script intentionally does NOT re-run estimation or overwrite any results.

Usage from repository root:
    python src/pipeline/14_run_pipeline.py --check
    python src/pipeline/14_run_pipeline.py --dashboard
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs'

REQUIRED = {
    'tables': [
        'descriptive_stats.csv',
        'correlation_matrix.csv'
    ],
    'model_results': [
        'irf_results.csv',
        'lp_results.csv',
        'subperiod_results.csv',
        'regime_results.csv',
        'robustness_results.csv',
        'rolling_sensitivity.csv',
        'model_comparison.csv',
        'forecast_results.csv',
        'forecast_significance.csv',
    ],
}


def validate() -> bool:
    errors = []

    print(f'Project root: {ROOT}')

    for group, files in REQUIRED.items():
        for filename in files:
            path = OUT / group / filename

            if not path.is_file():
                errors.append(
                    f'MISSING: {path.relative_to(ROOT)}'
                )
                continue

            try:
                with path.open(
                    'r',
                    encoding='utf-8-sig',
                    newline=''
                ) as f:
                    reader = csv.reader(f)
                    header = next(reader, [])

                if not header:
                    errors.append(
                        f'EMPTY HEADER: {path.relative_to(ROOT)}'
                    )
                else:
                    print(
                        f'OK: {path.relative_to(ROOT)} '
                        f'({len(header)} columns)'
                    )

            except (
                OSError,
                UnicodeError,
                csv.Error
            ) as exc:
                errors.append(
                    f'INVALID: {path.relative_to(ROOT)}: {exc}'
                )

    if errors:
        print('\nValidation errors:')
        print('\n'.join(errors))
        return False

    print(
        '\nAll required dashboard outputs '
        'are present and readable.'
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            'Read-only output validation '
            'and dashboard launcher'
        )
    )

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument(
        '--check',
        action='store_true',
        help='Validate existing outputs (default)'
    )

    mode.add_argument(
        '--dashboard',
        action='store_true',
        help='Validate and launch Streamlit'
    )

    args = parser.parse_args()

    if not validate():
        return 1

    if args.dashboard:
        app = ROOT / 'dashboard' / '12_dashboard_app.py'

        if not app.is_file():
            print(
                f'Missing dashboard app: {app}',
                file=sys.stderr
            )
            return 1

        return subprocess.call(
            [
                sys.executable,
                '-m',
                'streamlit',
                'run',
                str(app)
            ],
            cwd=ROOT
        )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())


