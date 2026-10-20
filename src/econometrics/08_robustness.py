from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

# ==================================================
# 1. CONFIG
# ==================================================
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUT = ROOT / "outputs/model_results"
OUT.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    cfg = json.load(f)

START = cfg["de_tai"]["ngay_bat_dau"]
END = cfg["de_tai"]["ngay_ket_thuc"]

SHOCKS = ["VIX", "DXY", "US2Y"]
ASSETS = ["BTC", "ETH"]
VARIABLES = SHOCKS + ASSETS

LAGS = 5
MAX_H = 30
Z = norm.ppf(0.975)

MAPPING = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH",
}

# ==================================================
# 2. LOAD AND VALIDATE DATA
# ==================================================
raw = pd.read_csv(DATA, parse_dates=["date"])
raw = raw.sort_values("date")
raw = raw.loc[raw["date"].between(START, END)].copy()

required = (
    ["date", "VIX"]
    + list(MAPPING.keys())
    + ["VIX_observed", "DXY_observed", "US2Y_observed"]
)

missing = sorted(set(required) - set(raw.columns))
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = raw.loc[:, required].copy()

# Retain the VIX level separately from VIX changes.
df = df.rename(columns={"VIX": "VIX_level"})
df = df.rename(columns=MAPPING)

if not df.columns.is_unique:
    raise ValueError("Duplicate column names")

df = df.set_index("date").sort_index()
df.index = df.index.normalize()

if df.index.has_duplicates:
    raise ValueError("Duplicate dates")

for col in VARIABLES + ["VIX_level"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

valid = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
    & df[VARIABLES + ["VIX_level"]].notna().all(axis=1)
)

events = df.loc[
    valid, VARIABLES + ["VIX_level"]
].copy()

# Lags use the previous actual macro observations.
lag_cols = []

for variable in VARIABLES:
    for lag in range(1, LAGS + 1):
        name = f"{variable}_lag{lag}"
        events[name] = events[variable].shift(lag)
        lag_cols.append(name)

# Lagged stress status, known before today's changes.
events["VIX_previous"] = events["VIX_level"].shift(1)

BASE_X = SHOCKS + lag_cols

def prepare_sample(asset, horizon, date_start, date_end):
    work = events[
        events.index.to_series().between(
            pd.Timestamp(date_start),
            pd.Timestamp(date_end)
        )
    ].copy()

    future_dates = work.index + pd.Timedelta(
        days=horizon
    )

    # Never use a response outside the subperiod.
    valid_future = (
        (future_dates >= pd.Timestamp(date_start))
        & (future_dates <= pd.Timestamp(date_end))
    )

    work["target"] = df[asset].reindex(
        future_dates
    ).to_numpy()

    work.loc[~valid_future, "target"] = np.nan

    return work.replace(
        [np.inf, -np.inf], np.nan
    )

def estimate_lp(work, regressors, hac_lags):
    usable = work.dropna(
        subset=regressors + ["target"]
    ).copy()

    if len(usable) < 100:
        return None, usable

    X = sm.add_constant(
        usable[regressors], has_constant="add"
    )

    fit = sm.OLS(usable["target"], X).fit(
        cov_type="HAC",
        cov_kwds={
            "maxlags": hac_lags,
            "use_correction": True,
        }
    )

    return fit, usable

# ==================================================
# 3. SUBPERIOD ANALYSIS
# ==================================================
PERIODS = {
    "pre_2020": ("2018-01-01", "2019-12-31"),
    "post_2020": ("2020-01-01", "2025-12-31"),
}

subperiod_rows = []

for period, (date_start, date_end) in PERIODS.items():
    print(f"\nEstimating {period}")

    for asset in ASSETS:
        for h in range(MAX_H + 1):
            work = prepare_sample(
                asset, h, date_start, date_end
            )

            fit, usable = estimate_lp(
                work, BASE_X, max(5, h + 1)
            )

            if fit is None:
                raise ValueError(
                    f"Insufficient data: {period}, "
                    f"{asset}, h={h}"
                )

            for shock in SHOCKS:
                beta = float(fit.params[shock])
                se = float(fit.bse[shock])

                subperiod_rows.append({
                    "response": asset,
                    "shock": shock,
                    "period": period,
                    "horizon": h,
                    "estimate": beta,
                    "ci_lower": beta - Z * se,
                    "ci_upper": beta + Z * se,
                    "std_error": se,
                    "p_value": float(fit.pvalues[shock]),
                    "nobs": int(fit.nobs),
                    "model": "LP",
                    "specification": "subperiod_ols_hac",
                    "horizon_unit": "calendar_days",
                })

subperiod = pd.DataFrame(subperiod_rows)

subperiod.to_csv(
    OUT / "subperiod_results.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Saved subperiod_results.csv")
print("Subperiod rows:", len(subperiod))

# ==================================================
# 4. BALANCED WINDOW ROBUSTNESS
# ==================================================
BALANCED = {
    "pre_2020": ("2018-01-01", "2019-12-31"),
    "post_2020_balanced": (
        "2020-01-01", "2021-12-31"
    ),
}

robust_rows = []

for period, (date_start, date_end) in BALANCED.items():
    for asset in ASSETS:
        for h in [0, 1, 5, 10, 20, 30]:
            work = prepare_sample(
                asset, h, date_start, date_end
            )

            fit, usable = estimate_lp(
                work, BASE_X, max(5, h + 1)
            )

            if fit is None:
                raise ValueError(
                    f"Insufficient balanced data: "
                    f"{period}, {asset}, h={h}"
                )

            for shock in SHOCKS:
                beta = float(fit.params[shock])
                se = float(fit.bse[shock])

                robust_rows.append({
                    "test": "balanced_subperiod",
                    "response": asset,
                    "shock": shock,
                    "period": period,
                    "regime": "",
                    "threshold": np.nan,
                    "horizon": h,
                    "estimate": beta,
                    "ci_lower": beta - Z * se,
                    "ci_upper": beta + Z * se,
                    "p_value": float(fit.pvalues[shock]),
                    "difference_p_value": np.nan,
                    "nobs": int(fit.nobs),
                    "specification": "balanced_sample_hac",
                })

# ==================================================
# 5. ALTERNATIVE STRESS THRESHOLDS
# ==================================================
for threshold in [25, 30, 35]:
    work_events = events.copy()

    work_events["Stress"] = np.where(
        work_events["VIX_previous"].isna(),
        np.nan,
        (
            work_events["VIX_previous"] >= threshold
        ).astype(float)
    )

    interactions = []

    for shock in SHOCKS:
        col = f"{shock}_x_Stress"
        work_events[col] = (
            work_events[shock] * work_events["Stress"]
        )
        interactions.append(col)

    regressors = (
        SHOCKS + ["Stress"]
        + interactions + lag_cols
    )

    complete = work_events.dropna(
        subset=regressors
    )

    count_stress = int(
        (complete["Stress"] == 1).sum()
    )

    print(
        f"Threshold={threshold}, "
        f"Stress observations={count_stress}"
    )

    if count_stress < 50:
        print("WARNING: Small stress sample")

    for asset in ASSETS:
        for h in [0, 1, 5, 10, 20, 30]:
            work = work_events.copy()

            future_dates = (
                work.index
                + pd.Timedelta(days=h)
            )

            work["target"] = df[asset].reindex(
                future_dates
            ).to_numpy()

            # Full-sample horizon cannot pass END.
            work.loc[
                future_dates > pd.Timestamp(END),
                "target"
            ] = np.nan

            fit, usable = estimate_lp(
                work, regressors, max(5, h + 1)
            )

            if fit is None:
                raise ValueError(
                    f"Insufficient regime data: "
                    f"threshold={threshold}, h={h}"
                )

            covariance = fit.cov_params()

            for shock in SHOCKS:
                interaction = f"{shock}_x_Stress"

                calm = float(fit.params[shock])
                delta = float(fit.params[interaction])
                stress = calm + delta

                var_stress = (
                    covariance.loc[shock, shock]
                    + covariance.loc[
                        interaction, interaction
                    ]
                    + 2 * covariance.loc[
                        shock, interaction
                    ]
                )

                se_stress = np.sqrt(
                    max(float(var_stress), 0)
                )

                robust_rows.append({
                    "test": "stress_threshold",
                    "response": asset,
                    "shock": shock,
                    "period": "full_sample",
                    "regime": "Stress",
                    "threshold": threshold,
                    "horizon": h,
                    "estimate": stress,
                    "ci_lower": stress - Z * se_stress,
                    "ci_upper": stress + Z * se_stress,
                    "p_value": np.nan,
                    "difference_p_value": float(
                        fit.pvalues[interaction]
                    ),
                    "nobs": int(fit.nobs),
                    "specification": (
                        "joint_interactions_ols_hac"
                    ),
                })

# ==================================================
# 6. EXPORT AND SUMMARIZE
# ==================================================
robustness = pd.DataFrame(robust_rows)

robustness.to_csv(
    OUT / "robustness_results.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nSUBPERIOD SUMMARY (h=0)")
print(
    subperiod[
        subperiod["horizon"] == 0
    ][[
        "response", "shock", "period",
        "estimate", "p_value", "nobs"
    ]].round(5).to_string(index=False)
)

print("\nROBUSTNESS SUMMARY")
print(
    robustness.groupby(["test", "response"])
    .size()
    .to_string()
)

print("\nSaved robustness_results.csv")
print("Robustness rows:", len(robustness))
print("ROBUSTNESS ANALYSIS FINISHED")
