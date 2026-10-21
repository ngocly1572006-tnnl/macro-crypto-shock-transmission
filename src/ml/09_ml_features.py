import argparse
import numpy as np
import pandas as pd
from ml_common import ROOT,ML,CRYPTO,MACRO,CHANGE_COL,config,ensure_dirs,read_source


def create_features(source=None, output=None):
    df=read_source(source)
    cfg=config()
    if int(cfg.get('macro_availability_lag_days',1))!=1:
        raise ValueError('This implementation explicitly assumes a 1-day conservative macro availability lag.')
    d=pd.DataFrame({'date':df.date})
    d['target_date']=df.date.shift(-1)
    d['weekday_sin']=np.sin(2*np.pi*df.date.dt.dayofweek/7)
    d['weekday_cos']=np.cos(2*np.pi*df.date.dt.dayofweek/7)
    for asset in CRYPTO:
        r=df[f'{asset}_log_return_pct']
        a=r.abs()
        for lag in (0,1,2,3,7):
            d[f'{asset}_ret_lag_{lag}']=r.shift(lag)
        for lag in (0,1,2,3,7,14):
            d[f'{asset}_abs_lag_{lag}']=a.shift(lag)
        for win in (3,7,14,30):
            d[f'{asset}_abs_mean_{win}']=a.rolling(win,min_periods=1).mean()
            d[f'{asset}_abs_std_{win}']=a.rolling(win,min_periods=2).std(ddof=0)
        d[f'{asset}_target_nextday_abs_pct']=a.shift(-1)
        d[f'{asset}_historical_30d']=a.rolling(30,min_periods=1).mean()
    # A market row dated t is only treated as known starting from t+1 UTC.
    # No bfill, no centered windows, no future observations, and no repeated "new" weekend shocks.
    for macro in MACRO:
        raw=df[macro]
        observed=df[f'{macro}_observed'].eq(1) & raw.notna()
        last_obs_value=raw.where(observed).shift(1).ffill()
        last_obs_date=df.date.where(observed).shift(1).ffill()
        new_release=observed.shift(1,fill_value=False)
        d[f'{macro}_asof_level']=last_obs_value
        d[f'{macro}_asof_release_today']=new_release.astype('int8')
        d[f'{macro}_asof_obs_date']=pd.to_datetime(last_obs_date)
        d[f'{macro}_asof_days_since_observation']=(df.date-pd.to_datetime(last_obs_date)).dt.days
        # 0 on no-release dates; publication (and thus change) is NOT repeated over weekends.
        delta=df[CHANGE_COL[macro]].shift(1)
        d[f'{macro}_asof_change_on_release']=delta.where(new_release,0.0)
    # Useful for provenance and verifying forecast origins, not predictors.
    d['has_crypto_features']=df['BTC_log_return_pct'].notna() & df['ETH_log_return_pct'].notna()
    ensure_dirs()
    target=output if output is not None else ML
    d.to_csv(target,index=False,date_format='%Y-%m-%d',float_format='%.10g')
    print(f'[features] saved {len(d)} rows to {target}')
    for a in CRYPTO:print(f'[features] {a}: valid labelled rows={int(d[f"{a}_target_nextday_abs_pct"].notna().sum())}')
    for m in MACRO:
        n=int(d[f'{m}_asof_release_today'].sum())
        print(f'[as-of] {m} safe daily release markers={n}, other days are not counted as new releases')
    print('[timing] Macros dated t are conservatively available at origin date t+1; vendor publication timestamps are not present in the source.')
    return d

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',default=None)
    p.add_argument('--output',default=None)
    a=p.parse_args()
    create_features(a.input,a.output)
