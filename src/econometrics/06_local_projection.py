
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# =====================================================
# 1. PATHS AND CONFIG
# =====================================================
ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "data/processed/model_dataset.csv"
CONFIG_PATH = ROOT / "config/research_config.json"

RESULTS_DIR = ROOT / "outputs/model_results"
FIGURES_DIR = ROOT / "outputs/figures"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH, encoding="utf-8") as f:
    config = json.load(f)

START = config["de_tai"]["ngay_bat_dau"]
END = config["de_tai"]["ngay_ket_thuc"]

HORIZONS = range(0, 31)
LAGS = 5
CI_Z = 1.959963984540054

VARIABLES = {
    "VIX": "VIX_change_points",
    "DXY": "DXY_log_return_pct",
    "US2Y": "US2Y_change_pp",
    "BTC": "BTC_log_return_pct",
    "ETH": "ETH_log_return_pct",
}

SHOCKS = ["VIX", "DXY", "US2Y"]
ASSETS = ["BTC", "ETH"]
ALL_VARIABLES = list(VARIABLES.keys())

# =====================================================
# 2. READ FULL DAILY CRYPTO DATA
# =====================================================
df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
    encoding="utf-8-sig"
)

df = df.sort_values("date")
df = df[df["date"].between(START, END)].copy()

if df["date"].duplicated().any():
    raise ValueError("Duplicate dates detected.")

required = ["date"] + list(VARIABLES.values())
required += [
    "VIX_observed",
    "DXY_observed",
    "US2Y_observed",
]

missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Chỉ giữ các biến thực sự cần cho mô hình LP
# trước khi đổi tên để tránh trùng với cột giá BTC/ETH

model_columns = (
    ["date"]
    + list(VARIABLES.values())
    + [
        "VIX_observed",
        "DXY_observed",
        "US2Y_observed",
    ]
)

df = df.loc[:, model_columns].copy()

df = df.rename(
    columns={
        original: name
        for name, original in VARIABLES.items()
    }
)

# Đảm bảo tên cột không bị trùng
assert df.columns.is_unique, (
    "Duplicate column names detected!"
)

df = df.set_index("date").sort_index()
df.index = df.index.normalize()

for col in ALL_VARIABLES:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Require actual observations on the shock date.
valid_macro = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
)

valid_macro &= df[SHOCKS].notna().all(axis=1)

# Macro event dates, while crypto returns remain
# available on the original calendar-day series.
events = df.loc[valid_macro, ALL_VARIABLES].copy()

print("Full calendar observations:", len(df))
print("Valid macro-event dates:", len(events))
print("First macro date:", events.index.min())
print("Last macro date:", events.index.max())

if len(events) < 300:
    raise ValueError("Insufficient observations.")

# =====================================================
# 3. LAGGED CONTROLS
# =====================================================
# Lags refer to previous observed macro sessions.
# Crypto controls also use returns at those sessions.
# No future data and no backward filling.

lag_columns = []

for variable in ALL_VARIABLES:
    for lag in range(1, LAGS + 1):
        name = f"{variable}_lag{lag}"
        events[name] = events[variable].shift(lag)
        lag_columns.append(name)

# Same-date macro variables are jointly controlled
# for, but NOT interpreted as identified causal shocks.
X_COLUMNS = SHOCKS + lag_columns

# =====================================================
# 4. LOCAL PROJECTION ESTIMATION
# =====================================================
results = []

for asset in ASSETS:

    # Daily crypto series must remain on calendar time.
    crypto_daily = df[asset]

    for h in HORIZONS:

        work = events[X_COLUMNS].copy()

        # Exact h calendar days after the macro event.
        future_dates = events.index + pd.Timedelta(days=h)

        work["target"] = crypto_daily.reindex(
            future_dates
        ).to_numpy()

        work = work.replace(
            [np.inf, -np.inf], np.nan
        ).dropna()

        if len(work) < 100:
            print(f"Skipping {asset}, h={h}: small sample")
            continue

        X = sm.add_constant(
            work[X_COLUMNS], has_constant="add"
        )
        y = work["target"]

        # HAC for serial correlation and overlapping
        # future horizons; bandwidth in event observations.
        hac_lags = max(5, h + 1)

        fit = sm.OLS(y, X).fit(
            cov_type="HAC",
            cov_kwds={
                "maxlags": hac_lags,
                "use_correction": True,
            }
        )

        for shock in SHOCKS:
            beta = float(fit.params[shock])
            se = float(fit.bse[shock])
            pval = float(fit.pvalues[shock])

            results.append({
                "response": asset,
                "shock": shock,
                "horizon": h,
                "estimate": beta,
                "std_error": se,
                "ci_lower": beta - CI_Z * se,
                "ci_upper": beta + CI_Z * se,
                "p_value": pval,
                "nobs": int(fit.nobs),
                "r_squared": float(fit.rsquared),
                "model": "LP",
                "specification": "ols_hac_5lags",
                "hac_lags": hac_lags,
                "horizon_unit": "calendar_days",
                "response_type": "daily_log_return",
                "shock_unit": (
                    "percentage_points"
                    if shock == "US2Y"
                    else "index_points"
                    if shock == "VIX"
                    else "log_return_pct"
                ),
            })

    print(f"Completed Local Projections: {asset}")

# =====================================================
# 5. EXPORT MODEL RESULTS
# =====================================================
lp_df = pd.DataFrame(results)

if lp_df.empty:
    raise RuntimeError("No LP estimates were produced.")

lp_df = lp_df.sort_values(
    ["response", "shock", "horizon"]
).reset_index(drop=True)

expected_rows = len(ASSETS) * len(SHOCKS) * len(HORIZONS)

if len(lp_df) != expected_rows:
    raise RuntimeError(
        f"Incomplete LP: got {len(lp_df)}, "
        f"expected {expected_rows}"
    )

if not np.isfinite(
    lp_df[["estimate", "ci_lower", "ci_upper"]].to_numpy()
).all():
    raise RuntimeError("Nonfinite LP estimates or CIs.")

output_file = RESULTS_DIR / "lp_results.csv"

lp_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("Saved:", output_file)
print("Total LP result rows:", len(lp_df))

# =====================================================
# 6. CREATE LP RESPONSE FIGURE
# =====================================================
fig, axes = plt.subplots(
    2, 3,
    figsize=(16, 9),
    sharex=True
)

for i, asset in enumerate(ASSETS):
    for j, shock in enumerate(SHOCKS):

        ax = axes[i, j]

        subset = lp_df[
            (lp_df["response"] == asset)
            & (lp_df["shock"] == shock)
        ].sort_values("horizon")

        h = subset["horizon"].to_numpy()
        beta = subset["estimate"].to_numpy()
        lower = subset["ci_lower"].to_numpy()
        upper = subset["ci_upper"].to_numpy()

        ax.plot(
            h, beta,
            linewidth=2,
            label="LP estimate"
        )

        ax.fill_between(
            h, lower, upper,
            alpha=0.2,
            label="95% HAC CI"
        )

        ax.axhline(
            0,
            color="black",
            linewidth=0.8,
            linestyle="--"
        )

        ax.set_title(f"{shock} -> {asset}")
        ax.set_xlabel("Horizon (calendar days)")
        ax.set_ylabel("Crypto return response (pp)")
        ax.grid(alpha=0.2)

        if i == 0 and j == 0:
            ax.legend()

fig.suptitle(
    "Local Projections: BTC and ETH responses\n"
    "Contemporaneous macro changes + 5 lag controls",
    fontsize=14
)

fig.tight_layout()

figure_file = FIGURES_DIR / "lp_responses.png"

fig.savefig(
    figure_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

print("Saved:", figure_file)

# =====================================================
# 7. SUMMARY FOR RESEARCH PAPER
# =====================================================
print("\nLOCAL PROJECTION SUMMARY")
print("Observations by asset/shock/horizon:")
print(
    lp_df.groupby(["response", "shock"])["nobs"]
    .agg(["min", "max"])
    .to_string()
)

print("\nSELECTED HORIZONS (0, 1, 5, 10, 20, 30)")

selected = lp_df[
    lp_df["horizon"].isin([0, 1, 5, 10, 20, 30])
][[
    "response", "shock", "horizon",
    "estimate", "ci_lower", "ci_upper", "p_value"
]]

print(
    selected.round(5).to_string(index=False)
)

print("\nLP FINISHED SUCCESSFULLY")

