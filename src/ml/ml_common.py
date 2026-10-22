"""Common utilities for TV4 ML forecasts. Do not modify source model_dataset.csv."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'data/processed/model_dataset.csv'
ML = ROOT / 'data/processed/ml_dataset.csv'
RESULTS = ROOT / 'outputs/model_results'
FIGURES = ROOT / 'outputs/figures'
MODELS = ROOT / 'outputs/models'
CRYPTO = ('BTC', 'ETH')
MACRO = ('US2Y', 'DXY', 'VIX')
CHANGE_COL = {'US2Y':'US2Y_change_pp','DXY':'DXY_log_return_pct','VIX':'VIX_change_points'}


def config():
    p = ROOT/'config/research_config.json'
    defaults = {
        'sample_start': '2018-01-01', 'sample_end':'2025-12-31',
        'ml_train_validation_end':'2024-12-31',
        'ml_test_start':'2025-01-01', 'ml_test_end':'2025-12-31',
        'macro_availability_lag_days':1, 'macro_availability_assumption':'Conservative one calendar-day lag; verify vendor timestamps before claiming real-time availability.',
    }
    if p.exists(): defaults.update(json.loads(p.read_text(encoding='utf-8')))
    return defaults


def ensure_dirs():
    for d in (ML.parent, RESULTS, FIGURES, MODELS): d.mkdir(parents=True, exist_ok=True)


def read_source(path=None):
    path = Path(path) if path else SRC
    if not path.is_file(): raise FileNotFoundError(f'Missing input {path}; Colab: copy/upload to /content/model_dataset.csv')
    df = pd.read_csv(path,parse_dates=['date']).sort_values('date').reset_index(drop=True)
    if df['date'].isna().any() or df['date'].duplicated().any():
        raise ValueError('date must be nonempty and unique')
    cfg = config()
    df=df.loc[(df.date >= pd.Timestamp(cfg['sample_start'])) & (df.date <= pd.Timestamp(cfg['sample_end']))].reset_index(drop=True)
    if len(df)<700: raise ValueError('Too few days: check data coverage')
    if (df['date'].diff().dropna() != pd.Timedelta(days=1)).any():
        raise ValueError('Crypto calendar is not daily continuous. Avoid shifting targets across gaps.')
    needed=['BTC','ETH','BTC_log_return_pct','ETH_log_return_pct'] + list(MACRO)
    needed += [f'{m}_observed' for m in MACRO]+[CHANGE_COL[m] for m in MACRO]
    missing=sorted(set(needed)-set(df.columns))
    if missing:raise KeyError(f'Missing columns: {missing}')
    for name in needed:df[name]=pd.to_numeric(df[name],errors='coerce')
    if (df[list(CRYPTO)] <= 0).any().any(): raise ValueError('Crypto prices must be positive')
    for asset in CRYPTO:
        expected=100*np.log(df[asset]/df[asset].shift(1))
        valid=expected.notna() & df[f'{asset}_log_return_pct'].notna()
        delta=(expected[valid]-df.loc[valid,f'{asset}_log_return_pct']).abs()
        if (delta>1e-4).any(): raise ValueError(f'{asset} returns inconsistent with prices. Do not silently recompute after filtering.')
    return df


def selected_features(df):
    crypto_cols=[c for c in df.columns if c.startswith(('BTC_ret_', 'BTC_abs_', 'ETH_ret_', 'ETH_abs_'))]
    crypto_cols += ['weekday_sin', 'weekday_cos']
    macro_cols=[f'{m}_asof_{suffix}' for m in MACRO for suffix in ('level','release_today','days_since_observation','change_on_release')]
    if len(macro_cols)<9:raise ValueError('Missing macro as-of fields in ml_dataset')
    return {'crypto_only':sorted(set(crypto_cols)), 'crypto_macro':sorted(set(crypto_cols+macro_cols))}


def splits(df):
    cfg=config()
    dates=pd.to_datetime(df['target_date'])
    train=dates <= pd.Timestamp(cfg['ml_train_validation_end'])
    test=(dates>=pd.Timestamp(cfg['ml_test_start'])) & (dates<=pd.Timestamp(cfg['ml_test_end']))
    return train, test


def temporal_cv(dates):
    """Expanding train to each validation year 2022, 2023, 2024."""
    dates=pd.to_datetime(dates)
    for valyear in (2022,2023,2024):
        tr=np.flatnonzero(dates<pd.Timestamp(f'{valyear}-01-01'))
        va=np.flatnonzero((dates>=pd.Timestamp(f'{valyear}-01-01')) & (dates<=pd.Timestamp(f'{valyear}-12-31')))
        if len(tr)<700 or len(va)<300:
            raise ValueError(f'Insufficient temporal data for {valyear} (train {len(tr)}, val {len(va)})')
        yield (valyear,tr,va)
