"""Evaluate frozen 2025 predictions, baseline vs crypto-only vs crypto+macro, and draw figures."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="DejaVu Sans"
from sklearn.metrics import mean_absolute_error,mean_squared_error
from ml_common import RESULTS,FIGURES,ensure_dirs


def evaluate(forecasts=None):
    ensure_dirs()
    p=pd.read_csv(forecasts or RESULTS/'forecast_results.csv',parse_dates=['date','origin_date'])
    required=['date','asset','actual','predicted','benchmark','split','model','feature_set']
    if any(c not in p.columns for c in required):raise KeyError('Missing forecast schema columns')
    if (p['date'].dt.year!=2025).any() or not (p['split']=='test').all():
        raise ValueError('Forecasts must evaluate on untouched test calendar 2025 only')
    records=[]
    for (asset,model,fset),g in p.groupby(['asset','model','feature_set'],sort=True):
        g=g.sort_values('date')
        if len(g)!=365 or g.date.duplicated().any():
            raise ValueError(f'Expected 365 unique 2025 target days: {asset}, {model}, {fset}')
        y=g.actual.to_numpy(dtype=float)
        pred=g.predicted.to_numpy(dtype=float)
        for metric,value in [('MAE',mean_absolute_error(y,pred)),('RMSE',np.sqrt(mean_squared_error(y,pred)))]:
            records.append({'asset':asset,'model':model,'feature_set':fset,
                            'metric':metric,'value':float(value),
                            'sample_period':'2025','n_obs':len(g),
                            'test_start':g.date.min().strftime('%Y-%m-%d'),
                            'test_end':g.date.max().strftime('%Y-%m-%d')})
    result=pd.DataFrame(records)
    base=result.query("model=='Historical30'").set_index(['asset','metric'])['value'].to_dict()
    crypto=result.query("feature_set=='crypto_only' and model!='Historical30'").set_index(['asset','model','metric'])['value'].to_dict()
    result['improvement_over_historical_pct']=result.apply(lambda r:100*(base[(r.asset,r.metric)]-r.value)/base[(r.asset,r.metric)],axis=1)
    result['macro_incremental_gain_pct']=result.apply(lambda r:100*(crypto.get((r.asset,r.model,r.metric),np.nan)-r.value)/crypto.get((r.asset,r.model,r.metric),np.nan) if r.feature_set=='crypto_macro' and r.model!='Historical30' else np.nan,axis=1)
    # Macro gain >0: smaller error once global variables were added.
    result=result.sort_values(['asset','metric','model','feature_set']).reset_index(drop=True)
    result.to_csv(RESULTS/'model_comparison.csv',index=False,float_format='%.7f')
    # Weekly circular moving-block bootstrap (descriptive 95% CI for MAE reduction).
    # We do not reselect predictors or tune hyperparameters from 2025.
    rng=np.random.default_rng(42)
    contrasts=[]
    for asset in ('BTC','ETH'):
        asset_df=p[p.asset.eq(asset)]
        by_key={(m,f):q.set_index('date').sort_index() for (m,f),q in asset_df.groupby(['model','feature_set'])}
        comparisons=[]
        base=('Historical30','crypto_only')
        for mod in ('ElasticNet','XGBoost'):
            comparisons.extend([(base,(mod,'crypto_only')),
                                ((mod,'crypto_only'),(mod,'crypto_macro'))])
        for left,right in comparisons:
            g0=by_key[left]; g1=by_key[right]
            if not g0.index.equals(g1.index):raise ValueError('Mismatched test dates in model contrast')
            if not np.allclose(g0.actual,g1.actual):raise ValueError('Different actual target in model contrast')
            reduction=np.abs(g0.actual.to_numpy()-g0.predicted.to_numpy())-np.abs(g1.actual.to_numpy()-g1.predicted.to_numpy())
            n=len(reduction);block=7;num=2000
            starts=rng.integers(0,n,size=(num,(n+block-1)//block))
            idx=(starts[:,:,None]+np.arange(block)[None,None,:])%n
            boot=reduction[idx.reshape(num,-1)[:,:n]].mean(axis=1)
            lo,hi=np.quantile(boot,[.025,.975])
            contrasts.append({'asset':asset,'reference_model':left[0],'reference_feature_set':left[1],
                              'candidate_model':right[0],'candidate_feature_set':right[1],
                              'mae_reduction':reduction.mean(),'ci95_lower':lo,'ci95_upper':hi,
                              'n_obs':n,'block_days':block,'bootstrap_reps':num,
                              'ci_excludes_zero':bool(lo>0 or hi<0)})
    pd.DataFrame(contrasts).to_csv(RESULTS/'forecast_significance.csv',index=False,float_format='%.8f')
    # All four fitted specifications must appear alongside the historical baseline.
    # Same color = same algorithm; dashed = crypto-only; solid = crypto + macro.
    styles = [
        ('ElasticNet','crypto_only','#2457a6','--','Elastic Net · Chỉ crypto'),
        ('ElasticNet','crypto_macro','#2457a6','-','Elastic Net · Crypto + Vĩ mô'),
        ('XGBoost','crypto_only','#087e73','--','XGBoost · Chỉ crypto'),
        ('XGBoost','crypto_macro','#087e73','-','XGBoost · Crypto + Vĩ mô'),
    ]
    fig,axes=plt.subplots(2,1,figsize=(15,9.3),sharex=True)
    for ax,asset in zip(axes,('BTC','ETH')):
        rows=p.loc[p.asset.eq(asset)].sort_values('date')
        ref=rows.loc[rows.model.eq('Historical30')]
        if len(ref)!=365:
            raise ValueError(f'Missing historical benchmark on 365 test days for {asset}')
        ax.plot(ref.date,ref.actual,color='#494949',alpha=.35,lw=1.0,
                label='|Lợi suất log| thực tế',zorder=1)
        ax.plot(ref.date,ref.predicted,color='#cd8a26',lw=1.6,alpha=.92,
                label='Trung bình lịch sử 30 ngày',zorder=3)
        for name,fset,color,linestyle,label in styles:
            x=rows.loc[rows.model.eq(name) & rows.feature_set.eq(fset)]
            if len(x)!=365 or not np.array_equal(x.date.to_numpy(),ref.date.to_numpy()):
                raise ValueError(f'Missing/misaligned forecast for {asset}/{name}/{fset}')
            ax.plot(x.date,x.predicted,lw=1.22,color=color,ls=linestyle,alpha=.86,
                    label=label,zorder=4)
        ax.set_ylabel(asset+' · |Lợi suất log| ngày tiếp theo (%)')
        ax.set_title(asset+' — kiểm tra ngoài mẫu năm 2025 (365 ngày)',loc='left',weight='bold',fontsize=12)
        ax.grid(alpha=.20)
        ax.spines[['top','right']].set_visible(False)
    handles, labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=10,
               bbox_to_anchor=(.5,.008),frameon=False)
    fig.suptitle('So sánh dự báo 2025 — bốn cấu hình học máy và benchmark lịch sử',
                 fontweight='bold',fontsize=15,y=.992)
    fig.tight_layout(rect=(0,.075,1,.97),h_pad=1.75)
    fig.savefig(FIGURES/'forecast_comparison.png',dpi=190,bbox_inches='tight')
    plt.close(fig)

    # Optional faceted plot makes crypto-only vs macro variants easy to inspect visually.
    fig,axes=plt.subplots(2,2,figsize=(16,8),sharex=True,sharey='row')
    for i,asset in enumerate(('BTC','ETH')):
        rows=p.loc[p.asset.eq(asset)].sort_values('date')
        ref=rows.loc[rows.model.eq('Historical30')]
        for j,(fset,suffix) in enumerate((('crypto_only','Chỉ crypto'),('crypto_macro','Crypto + Vĩ mô'))):
            ax=axes[i,j]
            ax.plot(ref.date,ref.actual,color='#4f4f4f',alpha=.36,lw=.9,label='Thực tế')
            ax.plot(ref.date,ref.predicted,color='#c98a23',lw=1.4,label='Trung bình lịch sử 30 ngày')
            for mod,color in (('ElasticNet','#2457a6'),('XGBoost','#087e73')):
                x=rows.loc[rows.model.eq(mod) & rows.feature_set.eq(fset)]
                ax.plot(x.date,x.predicted,color=color,lw=1.25,label=mod)
            ax.set_title(f'{asset}: {suffix}',fontsize=12,weight='bold')
            ax.set_ylabel('|Lợi suất log| (%)' if j==0 else '')
            ax.grid(alpha=.18)
            ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,-.005),ncol=4,frameon=False)
    fig.suptitle('So sánh dự báo theo bộ biến — tập kiểm tra 2025',weight='bold',fontsize=15,y=1.)
    fig.tight_layout(rect=(0,.055,1,.96))
    fig.savefig(FIGURES/'forecast_comparison_by_feature_set.png',dpi=190,bbox_inches='tight')
    plt.close(fig)

    # The CSV contains every feature from all eight trained models (2 assets × 2 models × 2 sets).
    # The older plot showed only XGBoost+Macro; this version visualizes all eight groups.
    imp_path=RESULTS/'feature_importance.csv'
    if imp_path.exists():
        imp=pd.read_csv(imp_path)
        expected={(a,m,fs) for a in ('BTC','ETH') for m in ('ElasticNet','XGBoost')
                  for fs in ('crypto_only','crypto_macro')}
        actual=set(map(tuple,imp[['asset','model','feature_set']].drop_duplicates().to_numpy()))
        if expected!=actual:
            raise ValueError(f'Incomplete feature-importance results: missing {expected-actual}')

        def top_features(ax,asset,model,fset,limit=10):
            subset=imp.loc[(imp.asset==asset)&imp.model.eq(model)&imp.feature_set.eq(fset)]
            if len(subset)!= (40 if fset=='crypto_only' else 52):
                raise ValueError(f'Incomplete features: {asset}/{model}/{fset}: {len(subset)}')
            if subset.feature.duplicated().any():
                raise ValueError(f'Duplicated importance features: {asset}/{model}/{fset}')
            top=subset.nlargest(limit,'importance').iloc[::-1]
            color='#2457a6' if model=='ElasticNet' else '#087e73'
            bars=ax.barh(top.feature,top.importance,color=color,alpha=.85)
            ax.set_title(f'{asset} · {"Chỉ crypto" if fset=="crypto_only" else "Crypto + Vĩ mô"}',
                         fontsize=10.5,weight='bold')
            ax.set_xlabel('|Hệ số chuẩn hóa|' if model=='ElasticNet' else 'Gain XGBoost chuẩn hóa',fontsize=9)
            ax.tick_params(axis='y',labelsize=8.0)
            ax.tick_params(axis='x',labelsize=8.0)
            ax.grid(axis='x',alpha=.18)
            ax.set_axisbelow(True)
            ax.spines[['top','right']].set_visible(False)
            return bars

        for model,filename in (('ElasticNet','feature_importance_elasticnet.png'),
                               ('XGBoost','feature_importance_xgboost.png')):
            fig,axes=plt.subplots(2,2,figsize=(16,11))
            for i,asset in enumerate(('BTC','ETH')):
                for j,fset in enumerate(('crypto_only','crypto_macro')):
                    top_features(axes[i,j],asset,model,fset,limit=12)
            fig.suptitle(f'{model} — 12 biến quan trọng nhất của bốn cấu hình',
                         fontsize=15,weight='bold',y=.998)
            fig.tight_layout(rect=(0,0,1,.965),w_pad=3,h_pad=3)
            fig.savefig(FIGURES/filename,dpi=175,bbox_inches='tight')
            plt.close(fig)

        fig,axes=plt.subplots(4,2,figsize=(17,19))
        for row,(model,fset) in enumerate((('ElasticNet','crypto_only'),('ElasticNet','crypto_macro'),
                                           ('XGBoost','crypto_only'),('XGBoost','crypto_macro'))):
            for j,asset in enumerate(('BTC','ETH')):
                top_features(axes[row,j],asset,model,fset,limit=10)
            axes[row,0].set_ylabel(model+' / '+('Chỉ crypto' if fset=='crypto_only' else 'Crypto + Vĩ mô'),fontsize=10)
        fig.suptitle('Độ quan trọng đặc trưng — 8 cấu hình mô hình (top 10 mỗi cấu hình)',
                     fontsize=15,weight='bold',y=.997)
        fig.tight_layout(rect=(0,0,1,.976),h_pad=2.7,w_pad=3.3)
        fig.savefig(FIGURES/'feature_importance.png',dpi=185,bbox_inches='tight')
        plt.close(fig)
    for a in ['BTC','ETH']:
        print(f'\n=== {a} (2025 test, n=365) ===')
        table=result.loc[(result.asset==a) & result.metric.eq('MAE'),['model','feature_set','value','improvement_over_historical_pct','macro_incremental_gain_pct']]
        print(table.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
    print('\n[saved] model_comparison.csv, forecast_significance.csv, forecast_comparison.png (+ by-feature-set), feature_importance.png (+ per-model)')
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',default=None);args=a.parse_args()
    evaluate(args.input)
