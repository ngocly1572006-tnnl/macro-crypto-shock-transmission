
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR

warnings.filterwarnings(
    "ignore", category=FutureWarning
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUTPUT = ROOT / "outputs/model_results"
OUTPUT.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    config = json.load(f)

start = config["de_tai"]["ngay_bat_dau"]
end = config["de_tai"]["ngay_ket_thuc"]

cols = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH",
}

df = pd.read_csv(DATA, parse_dates=["date"])
df = df.sort_values("date")
df = df[df["date"].between(start, end)].copy()

for col in [
    "VIX_observed",
    "DXY_observed",
    "US2Y_observed",
]:
    if col in df.columns:
        df = df[df[col] == 1]

data = (
    df[list(cols.keys())]
    .rename(columns=cols)
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
    .reset_index(drop=True)
)

print("Observations:", len(data))
print("Variables:", data.columns.tolist())

results = []

# Common estimation sample for fair lag comparisons.

results = []
max_lag = 15

for p in range(1, max_lag + 1):
    try:
        fit = VAR(
            data.iloc[max_lag - p:].reset_index(drop=True)
        ).fit(
            maxlags=p,
            ic=None,
            trend="c"
        )

        test = fit.test_whiteness(
            nlags=20,
            signif=0.05
        )

        results.append({
            "lag": p,
            "nobs": fit.nobs,
            "aic": fit.aic,
            "bic": fit.bic,
            "hqic": fit.hqic,
            "stable": bool(fit.is_stable()),
            "portmanteau_p": float(test.pvalue),
            "no_autocorr_5pct": bool(
                test.pvalue >= 0.05
            )
        })

    except Exception as e:
        print(f"VAR({p}) failed: {e}")

result_df = pd.DataFrame(results)

if result_df.empty:
    raise RuntimeError("No valid models estimated.")

result_df.to_csv(
    OUTPUT / "var_lag_diagnostics.csv",
    index=False
)

print("\nVAR LAG COMPARISON")
print(result_df.to_string(index=False))

valid = result_df[
    result_df["stable"]
    & result_df["no_autocorr_5pct"]
]

print("\nSTABLE MODELS WITHOUT DETECTED")
print("RESIDUAL AUTOCORRELATION AT 5%:")

if valid.empty:
    print("No candidate passed all diagnostics.")
else:
    print(valid.to_string(index=False))
    best = valid.sort_values("bic").iloc[0]
    print(
        "\nCandidate with lowest BIC among "
        "diagnostically acceptable models:",
        int(best["lag"])
    )

print("\nSaved: var_lag_diagnostics.csv")
