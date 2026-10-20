from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore", category=FutureWarning)

# 1. PROJECT PATHS
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
RESULTS = ROOT / "outputs/model_results"
FIGURES = ROOT / "outputs/figures"

RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    config = json.load(f)

# The actual config uses Vietnamese nested keys
start_date = config["de_tai"]["ngay_bat_dau"]
end_date = config["de_tai"]["ngay_ket_thuc"]

# 2. MODEL VARIABLES
variables = {
    "VIX": "VIX_change_points",
    "DXY": "DXY_log_return_pct",
    "US2Y": "US2Y_change_pp",
    "BTC": "BTC_log_return_pct",
    "ETH": "ETH_log_return_pct",
}
shocks = ["VIX", "DXY", "US2Y"]
assets = ["BTC", "ETH"]
horizon = 30

# 3. LOAD DATA
df = pd.read_csv(DATA, parse_dates=["date"])
df = df.sort_values("date")

df = df[
    df["date"].between(start_date, end_date)
].copy()

# Keep only actual jointly observed macro dates.
observed_cols = [
    "VIX_observed", "DXY_observed", "US2Y_observed"
]
for col in observed_cols:
    if col in df.columns:
        df = df.loc[df[col] == 1]

model = df[
    list(variables.values())
].rename(
    columns={v: k for k, v in variables.items()}
)

model = model.replace(
    [np.inf, -np.inf], np.nan
).dropna()

print("Sample observations:", len(model))
print("VAR columns:", model.columns.tolist())

if len(model) < 100:
    raise ValueError("Insufficient VAR observations.")

# 4. ADF STATIONARITY TEST
adf_rows = []
for variable in model.columns:
    result = adfuller(model[variable], autolag="AIC")
    adf_rows.append({
        "test": "ADF",
        "variable": variable,
        "statistic": result[0],
        "p_value": result[1],
        "lags": result[2],
        "nobs": result[3],
    })

# 5. SELECT LAG BY BIC
# Baseline VAR(5), selected after residual diagnostics.
# VAR(1) is preferred by BIC but exhibits autocorrelation.

p = 5
print("Baseline VAR lag:", p)

# Common comparison sample:
# 1995 observations - 15 initial observations = 1980
max_comparison_lag = 15
model = model.iloc[
    max_comparison_lag - p:
].reset_index(drop=True)

# 6. ESTIMATE VAR
result = VAR(model).fit(p, trend="c")
print(result.summary())

# 7. DIAGNOSTICS
diagnostics = []

for row in adf_rows:
    diagnostics.append({
        "test": "ADF",
        "response": row["variable"],
        "shock": "",
        "statistic": row["statistic"],
        "p_value": row["p_value"],
        "lag": row["lags"],
        "nobs": row["nobs"],
        "interpretation": "unit-root test",
    })

diagnostics.append({
    "test": "VAR_STABILITY",
    "response": "SYSTEM",
    "shock": "",
    "statistic": int(result.is_stable()),
    "p_value": np.nan,
    "lag": p,
    "nobs": result.nobs,
    "interpretation": "1=stable, 0=unstable",
})

# Residual autocorrelation diagnostics
white_12 = result.test_whiteness(
    nlags=max(12, p + 1),
    signif=0.05
)

white_20 = result.test_whiteness(
    nlags=max(20, p + 1),
    signif=0.05
)

# Keep 20-lag result as the primary reported diagnostic
white = white_20

print("\nRESIDUAL DIAGNOSTICS")
print("Portmanteau 12 lags p-value:", white_12.pvalue)
print("Portmanteau 20 lags p-value:", white_20.pvalue)

diagnostics.append({
    "test": "PORTMANTEAU",
    "response": "SYSTEM",
    "shock": "",
    "statistic": white.test_statistic,
    "p_value": white.pvalue,
    "lag": p,
    "nobs": result.nobs,
    "interpretation": "H0: no residual autocorrelation",
})

diagnostics.append({
    "test": "PORTMANTEAU_12",
    "response": "SYSTEM",
    "shock": "",
    "statistic": white_12.test_statistic,
    "p_value": white_12.pvalue,
    "lag": p,
    "nobs": result.nobs,
    "interpretation": "H0: no residual autocorrelation (12 lags)",
})

# 8. GRANGER CAUSALITY
for shock in shocks:
    for asset in assets:
        test = result.test_causality(
            caused=asset,
            causing=[shock],
            kind="f"
        )
        diagnostics.append({
            "test": "GRANGER_F",
            "response": asset,
            "shock": shock,
            "statistic": float(test.test_statistic),
            "p_value": float(test.pvalue),
            "lag": p,
            "nobs": result.nobs,
            "interpretation": "H0: shock does not Granger-cause response",
        })

diag_df = pd.DataFrame(diagnostics)
diag_df.to_csv(
    RESULTS / "var_results.csv", index=False
)

# 9. ORTHOGONALIZED IRF
irf = result.irf(horizon)
irf_values = irf.orth_irfs
irf_se = irf.stderr(orth=True)

z = 1.959963984540054
rows = []

for shock in shocks:
    for asset in assets:
        j = model.columns.get_loc(shock)
        i = model.columns.get_loc(asset)

        for h in range(horizon + 1):
            estimate = float(irf_values[h, i, j])
            se = float(irf_se[h, i, j])

            rows.append({
                "response": asset,
                "shock": shock,
                "horizon": h,
                "estimate": estimate,
                "ci_lower": estimate - z * se,
                "ci_upper": estimate + z * se,
                "model": "VAR",
                "specification": "cholesky_orthogonalized",
                "lag": p,
                "nobs": result.nobs,
                "horizon_unit": "macro_trading_observations",
            })

irf_df = pd.DataFrame(rows)
irf_df.to_csv(
    RESULTS / "irf_results.csv", index=False
)

# 10. PLOTS
for asset in assets:
    fig, axes = plt.subplots(
        1, 3, figsize=(15, 4), sharex=True
    )

    for ax, shock in zip(axes, shocks):
        sub = irf_df[
            (irf_df["response"] == asset)
            & (irf_df["shock"] == shock)
        ].sort_values("horizon")

        ax.plot(
            sub["horizon"], sub["estimate"],
            linewidth=2, label="IRF"
        )
        ax.fill_between(
            sub["horizon"].to_numpy(),
            sub["ci_lower"].to_numpy(),
            sub["ci_upper"].to_numpy(),
            alpha=0.2, label="95% CI"
        )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{shock} -> {asset}")
        ax.set_xlabel("Trading-session horizon")
        ax.grid(alpha=0.2)

    axes[0].set_ylabel("Return response (percentage points)")
    axes[0].legend()

    fig.suptitle(
        f"{asset} responses to macro innovations | VAR({p})"
    )
    fig.tight_layout()
    fig.savefig(
        FIGURES / f"irf_{asset.lower()}.png",
        dpi=200, bbox_inches="tight"
    )
    plt.close(fig)

print("\nVAR completed.")
print("Stability:", result.is_stable())
print("Portmanteau p-value:", white.pvalue)
print("\nGranger causality:")
print(diag_df[diag_df["test"] == "GRANGER_F"][
    ["shock", "response", "statistic", "p_value"]
].to_string(index=False))
print("\nSaved VAR, IRF results and figures.")