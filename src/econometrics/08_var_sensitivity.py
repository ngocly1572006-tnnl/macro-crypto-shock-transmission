from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR

warnings.filterwarnings("ignore", category=FutureWarning)

# =====================================================
# VAR sensitivity: lag length, Cholesky ordering.
# Reproduces the checks required before locking results
# and links LP (per unit) to VAR IRF (per 1 s.d.) at h=0.
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
HORIZON = 30
MAX_LAG = 15            # common estimation sample, as in 05_var_irf.py
Z = 1.959963984540054

# Select the needed columns BEFORE renaming (avoids duplicate names
# with the price/level columns BTC, ETH, VIX, DXY, US2Y).
raw = pd.read_csv(DATA, parse_dates=["date"], encoding="utf-8-sig")
raw = raw.sort_values("date")
raw = raw[raw["date"].between(START, END)]
raw = raw[["date"] + list(MAPPING) + OBSERVED]
raw = raw.rename(columns=MAPPING)
assert raw.columns.is_unique

valid = (
    raw["VIX_observed"].eq(1)
    & raw["DXY_observed"].eq(1)
    & raw["US2Y_observed"].eq(1)
)
data = (
    raw.loc[valid, SHOCKS + ASSETS]
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
    .reset_index(drop=True)
)
print("Observations:", len(data))

SPECS = [
    ("baseline_var5", 5, ["VIX", "DXY", "US2Y", "BTC", "ETH"]),
    ("var6_same_order", 6, ["VIX", "DXY", "US2Y", "BTC", "ETH"]),
    ("order_us2y_dxy_vix", 5, ["US2Y", "DXY", "VIX", "BTC", "ETH"]),
    ("order_dxy_us2y_vix", 5, ["DXY", "US2Y", "VIX", "BTC", "ETH"]),
    ("eth_before_btc", 5, ["VIX", "DXY", "US2Y", "ETH", "BTC"]),
]

rows = []
for name, p, order in SPECS:
    sample = data[order].iloc[MAX_LAG - p:].reset_index(drop=True)
    fit = VAR(sample).fit(p, trend="c")
    irf = fit.irf(HORIZON)
    values = irf.orth_irfs
    se = irf.stderr(orth=True)

    for shock in SHOCKS:
        for asset in ASSETS:
            j = order.index(shock)
            i = order.index(asset)
            for h in range(HORIZON + 1):
                est = float(values[h, i, j])
                s = float(se[h, i, j])
                rows.append({
                    "response": asset,
                    "shock": shock,
                    "horizon": h,
                    "estimate": est,
                    "ci_lower": est - Z * s,
                    "ci_upper": est + Z * s,
                    "model": "VAR",
                    "specification": name,
                    "lag": p,
                    "ordering": " > ".join(order),
                    "nobs": int(fit.nobs),
                    "horizon_unit": "macro_trading_observations",
                })
    print("Done:", name)

sens = pd.DataFrame(rows)
sens.to_csv(
    OUT / "var_sensitivity_results.csv",
    index=False, encoding="utf-8-sig"
)

# ----- LP (per unit) vs VAR (per 1 s.d.) at h=0 -----
lp = pd.read_csv(OUT / "lp_results.csv", encoding="utf-8-sig")
lp0 = lp[lp["horizon"] == 0].set_index(["response", "shock"])
sd = data[SHOCKS].std()

base = sens[
    (sens["specification"] == "baseline_var5") & (sens["horizon"] == 0)
].set_index(["response", "shock"])

comp = []
for (asset, shock), r in lp0.iterrows():
    lp_unit = float(r["estimate"])
    comp.append({
        "response": asset,
        "shock": shock,
        "lp_h0_per_unit": lp_unit,
        "shock_sd": float(sd[shock]),
        "lp_h0_per_1sd": lp_unit * float(sd[shock]),
        "var_orth_irf_h0": float(base.loc[(asset, shock), "estimate"]),
        "note": "VAR IRF is per 1 s.d. of the orthogonalised innovation; "
                "approximate comparison only",
    })

comp_df = pd.DataFrame(comp)
comp_df.to_csv(
    OUT / "lp_var_h0_comparison.csv",
    index=False, encoding="utf-8-sig"
)

print("\nIRF SENSITIVITY (h = 0, 1, 5, 10)")
show = sens[sens["horizon"].isin([0, 1, 5, 10])]
print(
    show.pivot_table(
        index=["response", "shock", "horizon"],
        columns="specification",
        values="estimate",
    ).round(3).to_string()
)
print("\nLP vs VAR at h=0")
print(comp_df.drop(columns="note").round(4).to_string(index=False))
print("\nVAR SENSITIVITY FINISHED")