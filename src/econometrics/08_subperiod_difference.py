
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUT = ROOT / "outputs/model_results"
OUT.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    cfg = json.load(f)

raw = pd.read_csv(DATA, parse_dates=["date"])
raw = raw.sort_values("date")
raw = raw[raw["date"].between(
    cfg["de_tai"]["ngay_bat_dau"],
    cfg["de_tai"]["ngay_ket_thuc"]
)].copy()

mapping = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH"
}

shocks = ["VIX", "DXY", "US2Y"]
assets = ["BTC", "ETH"]
variables = shocks + assets

cols = (
    ["date"] + list(mapping)
    + ["VIX_observed", "DXY_observed", "US2Y_observed"]
)

df = raw[cols].rename(columns=mapping).copy()
assert df.columns.is_unique

df = df.set_index("date").sort_index()

for col in variables:
    df[col] = pd.to_numeric(df[col], errors="coerce")

valid = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
    & df[variables].notna().all(axis=1)
)

events = df.loc[valid, variables].copy()

events["Post2020"] = (
    events.index >= pd.Timestamp("2020-01-01")
).astype(int)

lag_cols = []
for variable in variables:
    for lag in range(1, 6):
        col = f"{variable}_lag{lag}"
        events[col] = events[variable].shift(lag)
        lag_cols.append(col)

# Let every slope differ across periods.
base_cols = shocks + lag_cols
interaction_cols = []

for col in base_cols:
    new_col = f"{col}_x_Post2020"
    events[new_col] = events[col] * events["Post2020"]
    interaction_cols.append(new_col)

regressors = (
    base_cols + ["Post2020"] + interaction_cols
)

rows = []

for asset in assets:
    for h in range(31):
        work = events[regressors].copy()

        future_dates = (
            events.index + pd.Timedelta(days=h)
        )
        work["target"] = df[asset].reindex(
            future_dates
        ).to_numpy()

        # Exclude responses that cross the 2020 split.
        crosses_boundary = (
            (events.index < pd.Timestamp("2020-01-01"))
            & (future_dates >= pd.Timestamp("2020-01-01"))
        )
        work.loc[crosses_boundary, "target"] = np.nan

        work = work.replace(
            [np.inf, -np.inf], np.nan
        ).dropna()

        X = sm.add_constant(
            work[regressors], has_constant="add"
        )

        fit = sm.OLS(
            work["target"], X
        ).fit(
            cov_type="HAC",
            cov_kwds={
                "maxlags": max(5, h + 1),
                "use_correction": True
            }
        )

        for shock in shocks:
            delta_name = f"{shock}_x_Post2020"

            pre = float(fit.params[shock])
            delta = float(fit.params[delta_name])
            post = pre + delta

            rows.append({
                "response": asset,
                "shock": shock,
                "horizon": h,
                "pre_beta": pre,
                "post_beta": post,
                "difference": delta,
                "difference_se": float(
                    fit.bse[delta_name]
                ),
                "difference_p_value": float(
                    fit.pvalues[delta_name]
                ),
                "nobs": int(fit.nobs),
                "specification": (
                    "fully_interacted_post2020_hac"
                )
            })

result = pd.DataFrame(rows)

assert len(result) == 186
assert np.isfinite(
    result[["pre_beta", "post_beta", "difference"]]
).all().all()

result.to_csv(
    OUT / "subperiod_difference_tests.csv",
    index=False,
    encoding="utf-8-sig"
)

selected = result[
    result["horizon"].isin([0, 1, 5, 10, 20, 30])
]

print("\nPRE/POST DIFFERENCE TESTS")
print(
    selected[[
        "response", "shock", "horizon",
        "pre_beta", "post_beta",
        "difference", "difference_p_value"
    ]].round(5).to_string(index=False)
)

print("\nSignificant differences at 5%:")
print(
    (result["difference_p_value"] < 0.05).sum(),
    "of", len(result)
)

print("\nSaved subperiod_difference_tests.csv")
print("SUBPERIOD DIFFERENCE TEST FINISHED")
