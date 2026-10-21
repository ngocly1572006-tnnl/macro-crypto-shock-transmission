import json
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
from ml_common import ML,RESULTS,MODELS,CRYPTO,config,ensure_dirs,selected_features,splits,temporal_cv

MODEL_GRIDS={
    'ElasticNet':[
      {'alpha':a,'l1_ratio':l} for a in (0.01,0.1,0.5) for l in (0.2,0.8)
    ],
    'XGBoost':[
      {'n_estimators':200,'max_depth':2,'learning_rate':0.04},
      {'n_estimators':250,'max_depth':3,'learning_rate':0.04},
      {'n_estimators':200,'max_depth':2,'learning_rate':0.08},
    ],
}

def build_model(name, params):
    if name=='ElasticNet':
        return Pipeline([
            ('impute',SimpleImputer(strategy='median',keep_empty_features=True)),
            ('scale',StandardScaler()),
            ('reg',ElasticNet(**params,max_iter=12000,random_state=42))
        ])
    if name=='XGBoost':
        return Pipeline([
            ('impute',SimpleImputer(strategy='median',keep_empty_features=True)),
            ('reg',XGBRegressor(**params,objective='reg:squarederror',
                                  subsample=0.9,colsample_bytree=0.9,
                                  min_child_weight=6,reg_lambda=10.0,
                                  tree_method='hist',n_jobs=2,random_state=42))
        ])
    raise ValueError(name)


def train_and_forecast(ml_csv=None):
    ensure_dirs()
    d=pd.read_csv(ml_csv or ML,parse_dates=['date','target_date'])
    all_feats=selected_features(d)
    cfg=config()
    training_mask,testing_mask=splits(d)
    n_t=int(testing_mask.sum())
    print(f'[split] 2025 test dates (target day, not feature day): {n_t}; training cutoff {cfg["ml_train_validation_end"]}')
    if n_t<350:raise ValueError('Unexpected 2025 coverage')
    predictions=[]
    features_importance=[]
    tuning=[]
    for asset in CRYPTO:
        y_col=f'{asset}_target_nextday_abs_pct'
        ok=d['has_crypto_features'].astype(bool) & d[y_col].notna()
        train=d.loc[ok & training_mask].copy().reset_index(drop=True)
        test=d.loc[ok & testing_mask].copy().reset_index(drop=True)
        if len(test)!=365:print(f'[WARNING] {asset} 2025 has {len(test)} test targets; check source coverage')
        ytr=train[y_col].to_numpy(dtype=float)
        yte=test[y_col].to_numpy(dtype=float)
        common_cols={
            'date':test['target_date'].dt.strftime('%Y-%m-%d').to_numpy(),
            'origin_date':test['date'].dt.strftime('%Y-%m-%d').to_numpy(),
            'asset':asset, 'target':'next_day_abs_log_return_pct',
            'actual':yte, 'split':'test',
            'benchmark':test[f'{asset}_historical_30d'].to_numpy(dtype=float)
        }
        pred_base=common_cols.copy()
        pred_base.update(model='Historical30',feature_set='crypto_only',predicted=pred_base['benchmark'],selected_params='{}')
        predictions.append(pd.DataFrame(pred_base))
        for fset,columns in all_feats.items():
            xtr=train[columns].astype(float)
            xte=test[columns].astype(float)
            for name,grid in MODEL_GRIDS.items():
                scored=[]
                for params in grid:
                    fold_errors=[]
                    for val_year,tri,vai in temporal_cv(train.target_date):
                        fitted=build_model(name,params)
                        fitted.fit(xtr.iloc[tri],ytr[tri])
                        phat=np.maximum(0,fitted.predict(xtr.iloc[vai]))
                        mae=float(mean_absolute_error(ytr[vai],phat))
                        fold_errors.append(mae)
                        tuning.append({'asset':asset,'model':name,'feature_set':fset,
                                       'params':json.dumps(params,sort_keys=True),
                                       'validation_year':val_year,'mae':mae,'n_val':len(vai)})
                    scored.append((float(np.mean(fold_errors)), params))
                best_mae,best_params=min(scored,key=lambda t:t[0])
                final=build_model(name,best_params)
                final.fit(xtr,ytr)
                phat=np.maximum(0,final.predict(xte))
                p=common_cols.copy()
                p.update(model=name,feature_set=fset,predicted=phat,selected_params=json.dumps(best_params,sort_keys=True))
                predictions.append(pd.DataFrame(p))
                path=MODELS/f'{asset}_{name}_{fset}.joblib'
                joblib.dump({'estimator':final,'feature_columns':columns,'asset':asset,
                             'feature_set':fset,'target':y_col,
                             'train_end':str(train.target_date.max().date()),
                             'asof_macro_calendar_lag_days':1},path)
                est=final.named_steps['reg']
                if name=='ElasticNet':
                    imp=np.asarray(est.coef_,dtype=float)
                    importance=np.abs(imp)
                    signed=imp
                else:
                    importance=np.asarray(est.feature_importances_,dtype=float)
                    signed=np.full(len(columns),np.nan)
                for col,im,si in zip(columns,importance,signed):
                    features_importance.append({'asset':asset,'model':name,'feature_set':fset,
                                                'feature':col,'importance':float(im),
                                                'signed_coefficient':float(si) if np.isfinite(si) else np.nan,
                                                'importance_definition':'absolute standardized coefficient' if name=='ElasticNet' else 'normalized feature importance (XGBoost gain)'})
                print(f'[fit] {asset:3s} {name:10s} {fset:12s} CV-MAE={best_mae:.4f} test-MAE={mean_absolute_error(yte,phat):.4f} params={best_params}',flush=True)
    pr=pd.concat(predictions,ignore_index=True)
    pr=pr[['date','origin_date','asset','target','actual','predicted','benchmark','split','model','feature_set','selected_params']]
    pr.to_csv(RESULTS/'forecast_results.csv',index=False,float_format='%.8f')
    pd.DataFrame(tuning).to_csv(RESULTS/'cv_tuning_results.csv',index=False)
    pd.DataFrame(features_importance).to_csv(RESULTS/'feature_importance.csv',index=False)
    print('[saved] forecast_results.csv, cv_tuning_results.csv, feature_importance.csv, 8 model joblibs')
    return pr

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default=None); args=p.parse_args()
    train_and_forecast(args.input)
