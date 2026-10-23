
"""Read-only helpers for the macro–crypto research dashboard.

This module never estimates models or modifies source CSV files.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / 'outputs'
RESULTS = OUTPUTS / 'model_results'
TABLES = OUTPUTS / 'tables'
FIGURES = OUTPUTS / 'figures'

REQUIRED = {
    'model_results': [
        'irf_results.csv', 'lp_results.csv', 'subperiod_results.csv',
        'regime_results.csv', 'robustness_results.csv',
        'rolling_sensitivity.csv', 'model_comparison.csv',
        'forecast_results.csv', 'forecast_significance.csv',
    ],
    'tables': ['descriptive_stats.csv', 'correlation_matrix.csv'],
}


def check_outputs() -> list[str]:
    """Return missing required files relative to outputs/."""
    return [
        str(Path(group) / name)
        for group, names in REQUIRED.items()
        for name in names
        if not (OUTPUTS / group / name).is_file()
    ]


def csv_file(name: str, group: str = 'model_results') -> pd.DataFrame:
    """Load a named CSV from the allowed outputs subfolder."""
    if group not in ('model_results', 'tables'):
        raise ValueError(f'Unsupported output group: {group}')
    if Path(name).name != name or not name.endswith('.csv'):
        raise ValueError('Expected a CSV filename, not a path')
    path = OUTPUTS / group / name
    if not path.is_file():
        raise FileNotFoundError(f'Not found: {path}')
    return pd.read_csv(path)


def optional_csv(name: str, group: str = 'model_results') -> pd.DataFrame:
    path = OUTPUTS / group / name
    return csv_file(name, group) if path.is_file() else pd.DataFrame()


def figure_path(name: str) -> Path | None:
    if Path(name).name != name or not name.endswith('.png'):
        raise ValueError('Expected a PNG filename')
    path = FIGURES / name
    return path if path.is_file() else None


def filter_rows(df: pd.DataFrame, **filters) -> pd.DataFrame:
    out = df
    for column, value in filters.items():
        if column in out.columns and value is not None:
            out = out.loc[out[column] == value]
    return out.copy()


def forecast_metrics(forecasts: pd.DataFrame) -> pd.DataFrame:
    """Independently recompute MAE/RMSE from submitted test predictions."""
    needed = {'asset', 'model', 'feature_set', 'actual', 'predicted'}
    if not needed.issubset(forecasts.columns):
        raise ValueError(
            f'Forecast CSV missing: {sorted(needed - set(forecasts.columns))}'
        )

    data = forecasts.copy()
    if 'split' in data.columns:
        data = data.loc[data['split'] == 'test']

    data['error'] = (
        pd.to_numeric(data['actual'], errors='coerce')
        - pd.to_numeric(data['predicted'], errors='coerce')
    )
    data = data.dropna(subset=['error'])
    data['abs_error'] = data['error'].abs()
    data['squared_error'] = data['error'] ** 2

    result = data.groupby(
        ['asset', 'model', 'feature_set'], as_index=False
    ).agg(
        n_obs=('error', 'size'),
        MAE=('abs_error', 'mean'),
        mse=('squared_error', 'mean')
    )
    result['RMSE'] = result['mse'] ** 0.5

    return result.drop(columns=['mse']).sort_values(['asset', 'MAE'])


