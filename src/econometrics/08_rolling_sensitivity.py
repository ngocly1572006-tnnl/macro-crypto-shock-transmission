
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/model_dataset.csv"
CONFIG = ROOT / "config/research_config.json"
OUT = ROOT / "outputs/model_results"
FIG = ROOT / "outputs/figures"

OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

with open(CONFIG, encoding="utf-8") as f:
    cfg = json.load(f)

start = cfg["de_tai"]["ngay_bat_dau"]
end = cfg["de_tai"]["ngay_ket_thuc"]

WINDOW = 252
LAGS = 5

mapping = {
    "VIX_change_points": "VIX",
    "DXY_log_return_pct": "DXY",
    "US2Y_change_pp": "US2Y",
    "BTC_log_return_pct": "BTC",
    "ETH_log_return_pct": "ETH",
}

shocks = ["VIX", "DXY", "US2Y"]
assets = ["BTC", "ETH"]
variables = shocks + assets

df = pd.read_csv(DATA, parse_dates=["date"])
df = df.loc[df["date"].between(start, end)].copy()
df = df.sort_values("date")

required = (
    ["date"] + list(mapping)
    + ["VIX_observed", "DXY_observed", "US2Y_observed"]
)

missing = sorted(set(required) - set(df.columns))
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df.loc[:, required].rename(columns=mapping)

if not df.columns.is_unique:
    raise ValueError("Duplicate columns")

if df["date"].duplicated().any():
    raise ValueError("Duplicate dates")

valid = (
    df["VIX_observed"].eq(1)
    & df["DXY_observed"].eq(1)
    & df["US2Y_observed"].eq(1)
)

df = df.loc[valid].copy().reset_index(drop=True)

for variable in variables:
    df[variable] = pd.to_numeric(
        df[variable], errors="coerce"
    )

df = df.replace([np.inf, -np.inf], np.nan)

# Five lags of the full observed-variable system.
lag_cols = []

for variable in variables:
    for lag in range(1, LAGS + 1):
        col = f"{variable}_lag{lag}"
        df[col] = df[variable].shift(lag)
        lag_cols.append(col)

df = df.dropna(
    subset=variables + lag_cols
).reset_index(drop=True)

features = shocks + lag_cols

X = np.column_stack([
    np.ones(len(df)),
    df[features].to_numpy(dtype=float)
])

results = []

print("Rolling regression sample:", len(df))
print("Rolling window:", WINDOW)
print("Model regressors:", X.shape[1])

if len(df) < WINDOW:
    raise ValueError("Insufficient observations")

for asset in assets:
    y = df[asset].to_numpy(dtype=float)

    for end_idx in range(WINDOW, len(df) + 1):
        start_idx = end_idx - WINDOW

        Xw = X[start_idx:end_idx]
        yw = y[start_idx:end_idx]

        beta, _, rank, _ = np.linalg.lstsq(
            Xw, yw, rcond=None
        )

        if rank < Xw.shape[1]:
            raise ValueError(
                f"Rank deficiency for {asset}, "
                f"ending {df.loc[end_idx - 1, 'date']}"
            )

        date = df.loc[end_idx - 1, "date"]

        for j, shock in enumerate(shocks):
            results.append({
                "date": date,
                "asset": asset,
                "shock": shock,
                "rolling_beta": float(beta[1 + j]),
                "window": WINDOW,
                "specification": (
                    "contemporaneous_macro_"
                    "five_lags_ols"
                ),
                "nobs": WINDOW,
            })

    print(f"Completed rolling regression: {asset}")

result = pd.DataFrame(results)

if result.empty:
    raise RuntimeError("No rolling estimates generated")

if result["rolling_beta"].isna().any():
    raise RuntimeError("Missing rolling coefficients")

result.to_csv(
    OUT / "rolling_sensitivity.csv",
    index=False,
    encoding="utf-8-sig"
)

fig, axes = plt.subplots(
    2, 3, figsize=(16, 9), sharex=True
)

for i, asset in enumerate(assets):
    for j, shock in enumerate(shocks):
        ax = axes[i, j]

        part = result[
            (result["asset"] == asset)
            & (result["shock"] == shock)
        ].sort_values("date")

        ax.plot(
            part["date"],
            part["rolling_beta"],
            linewidth=1.5
        )

        ax.axhline(
            0, color="black",
            linestyle="--", linewidth=0.8
        )

        ax.axvline(
            pd.Timestamp("2020-01-01"),
            color="gray",
            linestyle=":", linewidth=1
        )

        ax.set_title(f"{shock} -> {asset}")
        ax.set_ylabel("Rolling coefficient")
        ax.grid(alpha=0.2)
        ax.tick_params(axis="x", rotation=30)

fig.suptitle(
    "Rolling macro-crypto sensitivities\n"
    "252 observed macro sessions, OLS with 5 lags"
)

fig.tight_layout()
fig.savefig(
    FIG / "rolling_sensitivity.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close(fig)

print("\nROLLING SUMMARY")
print(
    result.groupby(["asset", "shock"])["rolling_beta"]
    .agg(["mean", "std", "min", "max"])
    .round(5)
    .to_string()
)

print("\nFirst rolling date:", result["date"].min())
print("Last rolling date:", result["date"].max())
print("Total output rows:", len(result))
print("ROLLING SENSITIVITY FINISHED")
