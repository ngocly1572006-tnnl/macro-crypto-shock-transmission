

from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUT = ROOT / "outputs/model_results"
FIG = ROOT / "outputs/figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    cfg = json.load(f)

START = cfg["de_tai"]["ngay_bat_dau"]
END = cfg["de_tai"]["ngay_ket_thuc"]

SHOCKS = ["VIX", "DXY", "US2Y"]
ASSETS = ["BTC", "ETH"]
ALL = SHOCKS + ASSETS
LAGS = 5
MAX_H = 30
THRESHOLD = 30.0
Z = norm.ppf(0.975)

mapping = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH",
}

raw = pd.read_csv(DATA, parse_dates=["date"])
raw = raw.sort_values("date")
raw = raw[raw["date"].between(START, END)].copy()

required = (
    ["date", "VIX"] + list(mapping)
    + ["VIX_observed", "DXY_observed", "US2Y_observed"]
)
missing = sorted(set(required) - set(raw.columns))
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = raw.loc[:, required].copy()
df = df.rename(columns={"VIX": "VIX_level"})
df = df.rename(columns=mapping)

assert df.columns.is_unique, "Duplicate column names."
df = df.set_index("date").sort_index()
df.index = df.index.normalize()

if df.index.has_duplicates:
    raise ValueError("Duplicate dates.")

for c in ALL + ["VIX_level"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

valid = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
    & df[ALL + ["VIX_level"]].notna().all(axis=1)
)

events = df.loc[valid, ALL + ["VIX_level"]].copy()

# Previous observed macro session, NOT same-day VIX.
events["VIX_previous"] = events["VIX_level"].shift(1)
events["Stress"] = np.where(
    events["VIX_previous"].isna(),
    np.nan,
    (events["VIX_previous"] >= THRESHOLD).astype(float)
)

lag_cols = []
for variable in ALL:
    for lag in range(1, LAGS + 1):
        col = f"{variable}_lag{lag}"
        events[col] = events[variable].shift(lag)
        lag_cols.append(col)

# Joint interaction model:
# All 3 macro shocks and all 3 interactions.
interaction_cols = []
for shock in SHOCKS:
    col = f"{shock}_x_Stress"
    events[col] = events[shock] * events["Stress"]
    interaction_cols.append(col)

XCOLS = SHOCKS + ["Stress"] + interaction_cols + lag_cols

print("Macro observations:", len(events))
print("Regime threshold: previous-session VIX >= 30")

base = events.dropna(subset=XCOLS)
counts = base["Stress"].value_counts().sort_index()
print("Calm observations:", int(counts.get(0.0, 0)))
print("Stress observations:", int(counts.get(1.0, 0)))

if counts.get(0.0, 0) < 50 or counts.get(1.0, 0) < 50:
    raise ValueError(
        "Too few observations in one regime; "
        "review the threshold before estimating."
    )

results = []
diagnostics = []

for asset in ASSETS:
    daily_crypto = df[asset]

    for h in range(MAX_H + 1):
        work = events[XCOLS].copy()
        target_dates = events.index + pd.Timedelta(days=h)
        work["target"] = daily_crypto.reindex(
            target_dates
        ).to_numpy()

        work = work.replace(
            [np.inf, -np.inf], np.nan
        ).dropna()

        regime_counts = work["Stress"].value_counts()
        n_calm = int(regime_counts.get(0.0, 0))
        n_stress = int(regime_counts.get(1.0, 0))

        if min(n_calm, n_stress) < 30:
            raise ValueError(
                f"Too few observations: {asset}, h={h}"
            )

        X = sm.add_constant(
            work[XCOLS], has_constant="add"
        )
        y = work["target"]

        hac_lags = max(5, h + 1)
        fit = sm.OLS(y, X).fit(
            cov_type="HAC",
            cov_kwds={
                "maxlags": hac_lags,
                "use_correction": True,
            }
        )

        covariance = fit.cov_params()

        diagnostics.append({
            "response": asset,
            "horizon": h,
            "nobs": int(fit.nobs),
            "n_calm": n_calm,
            "n_stress": n_stress,
            "r_squared": float(fit.rsquared),
            "hac_lags": hac_lags,
        })

        for shock in SHOCKS:
            inter = f"{shock}_x_Stress"

            beta_calm = float(fit.params[shock])
            delta = float(fit.params[inter])
            beta_stress = beta_calm + delta

            var_calm = float(covariance.loc[shock, shock])
            var_delta = float(covariance.loc[inter, inter])
            cov_cross = float(covariance.loc[shock, inter])

            se_calm = np.sqrt(max(var_calm, 0))
            se_delta = np.sqrt(max(var_delta, 0))
            se_stress = np.sqrt(
                max(var_calm + var_delta + 2 * cov_cross, 0)
            )

            p_difference = float(fit.pvalues[inter])

            for regime, beta, se, n_regime in [
                ("Calm", beta_calm, se_calm, n_calm),
                ("Stress", beta_stress, se_stress, n_stress),
            ]:
                results.append({
                    "response": asset,
                    "shock": shock,
                    "regime": regime,
                    "horizon": h,
                    "estimate": beta,
                    "std_error": se,
                    "ci_lower": beta - Z * se,
                    "ci_upper": beta + Z * se,
                    "difference_stress_minus_calm": delta,
                    "difference_se": se_delta,
                    "difference_ci_lower": delta - Z * se_delta,
                    "difference_ci_upper": delta + Z * se_delta,
                    "difference_p_value": p_difference,
                    "nobs": int(fit.nobs),
                    "n_regime": n_regime,
                    "model": "LP_INTERACTION",
                    "specification": "joint_macro_interactions_hac",
                    "hac_lags": hac_lags,
                    "horizon_unit": "calendar_days",
                    "stress_threshold": THRESHOLD,
                    "stress_definition": "previous_macro_session_vix",
                })

    print(f"Completed regime LP: {asset}")

result = pd.DataFrame(results)
expected = len(ASSETS) * len(SHOCKS) * 2 * (MAX_H + 1)

if len(result) != expected:
    raise RuntimeError(
        f"Expected {expected} rows, got {len(result)}."
    )

if not np.isfinite(
    result[[
        "estimate", "ci_lower", "ci_upper",
        "difference_p_value"
    ]].to_numpy()
).all():
    raise RuntimeError("Nonfinite results.")

result = result.sort_values(
    ["response", "shock", "regime", "horizon"]
)

result.to_csv(
    OUT / "regime_results.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(diagnostics).to_csv(
    OUT / "regime_diagnostics.csv",
    index=False,
    encoding="utf-8-sig"
)

# ================================================
# FIGURE: CALM VS STRESS
# ================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 9))

for i, asset in enumerate(ASSETS):
    for j, shock in enumerate(SHOCKS):
        ax = axes[i, j]

        for regime in ["Calm", "Stress"]:
            part = result[
                (result["response"] == asset)
                & (result["shock"] == shock)
                & (result["regime"] == regime)
            ].sort_values("horizon")

            h = part["horizon"].to_numpy()
            estimate = part["estimate"].to_numpy()

            ax.plot(
                h, estimate,
                linewidth=2,
                label=regime
            )
            ax.fill_between(
                h,
                part["ci_lower"].to_numpy(),
                part["ci_upper"].to_numpy(),
                alpha=0.12
            )

        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{shock} -> {asset}")
        ax.set_xlabel("Horizon (calendar days)")
        ax.set_ylabel("Return response (pp)")
        ax.grid(alpha=0.2)

        if i == 0 and j == 0:
            ax.legend()

fig.suptitle(
    "Conditional Local Projections: Calm vs Stress\n"
    "Stress based on previous-session VIX >= 30"
)
fig.tight_layout()
fig.savefig(
    FIG / "regime_comparison.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close(fig)

# ================================================
# TERMINAL SUMMARY
# ================================================
print("\nREGIME ANALYSIS SUMMARY")
selected = result[
    result["horizon"].isin([0, 1, 5, 10, 20, 30])
]

summary = selected[
    selected["regime"] == "Stress"
][[
    "response", "shock", "horizon",
    "estimate", "difference_stress_minus_calm",
    "difference_p_value", "n_regime"
]]

print(summary.round(5).to_string(index=False))
print("\nSaved regime_results.csv")
print("Saved regime_diagnostics.csv")
print("Saved regime_comparison.png")
print("REGIME ANALYSIS FINISHED")
