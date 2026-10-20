from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore", category=FutureWarning)

# =====================================================
# HAC bandwidth sensitivity for the baseline LP
# (same specification as 06_local_projection.py;
#  only the Newey-West bandwidth L is varied).
# =====================================================
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUT = ROOT / "outputs/model_results"
OUT.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    cfg = json.load(f)

START = cfg["de_tai"]["ngay_bat_dau"]
END = cfg["de_tai"]["ngay_ket_thuc"]

MAPPING = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH",
}
OBSERVED = ["VIX_observed", "DXY_observed", "US2Y_observed"]
SHOCKS = ["VIX", "DXY", "US2Y"]
ASSETS = ["BTC", "ETH"]
VARIABLES = SHOCKS + ASSETS
LAGS = 5
BANDWIDTHS = [1, 5, 10, 20, 40]

# Select columns BEFORE renaming to avoid duplicate names.
raw = pd.read_csv(DATA, parse_dates=["date"], encoding="utf-8-sig")
raw = raw.sort_values("date")
raw = raw[raw["date"].between(START, END)]
raw = raw[["date"] + list(MAPPING) + OBSERVED].rename(columns=MAPPING)
assert raw.columns.is_unique

df = raw.set_index("date").sort_index()
df.index = df.index.normalize()

valid = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
    & df[VARIABLES].notna().all(axis=1)
)
events = df.loc[valid, VARIABLES].copy()

lag_cols = []
for variable in VARIABLES:
    for lag in range(1, LAGS + 1):
        name = f"{variable}_lag{lag}"
        events[name] = events[variable].shift(lag)
        lag_cols.append(name)

X_COLUMNS = SHOCKS + lag_cols

rows = []
for asset in ASSETS:
    for h in range(31):
        work = events[X_COLUMNS].copy()
        work["target"] = df[asset].reindex(
            events.index + pd.Timedelta(days=h)
        ).to_numpy()
        work = work.replace([np.inf, -np.inf], np.nan).dropna()

        X = sm.add_constant(work[X_COLUMNS], has_constant="add")
        for L in BANDWIDTHS:
            fit = sm.OLS(work["target"], X).fit(
                cov_type="HAC",
                cov_kwds={"maxlags": L, "use_correction": True},
            )
            for shock in SHOCKS:
                rows.append({
                    "response": asset,
                    "shock": shock,
                    "horizon": h,
                    "hac_lags": L,
                    "estimate": float(fit.params[shock]),
                    "std_error": float(fit.bse[shock]),
                    "p_value": float(fit.pvalues[shock]),
                    "significant_5pct": bool(fit.pvalues[shock] < 0.05),
                    "model": "LP",
                    "specification": "hac_bandwidth_sensitivity",
                })

result = pd.DataFrame(rows)
result.to_csv(
    OUT / "hac_sensitivity_results.csv",
    index=False, encoding="utf-8-sig"
)

# How many (response, shock, horizon) cells change significance at 5%
# relative to the baseline bandwidth used in 06 (max(5, h+1))?
cells = result.pivot_table(
    index=["response", "shock", "horizon"],
    columns="hac_lags",
    values="significant_5pct",
    aggfunc="first",
)
varies = cells.nunique(axis=1) > 1

print("HAC BANDWIDTH SENSITIVITY")
print("Cells:", len(cells))
print("Cells whose 5% significance depends on bandwidth:",
      int(varies.sum()))
print(cells[varies].to_string())
print("\nBandwidths:", BANDWIDTHS)
print("HAC SENSITIVITY FINISHED")