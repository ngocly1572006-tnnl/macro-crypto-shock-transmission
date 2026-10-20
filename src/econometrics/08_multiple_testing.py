from pathlib import Path
import pandas as pd
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/model_results"

summary = []


def apply_fdr(df, p_col, family, output_name=None, alpha=0.05):
    """Benjamini-Hochberg FDR within one family of tests."""
    df = df.copy()
    reject, p_adj, _, _ = multipletests(
        df[p_col].to_numpy(), alpha=alpha, method="fdr_bh"
    )
    df["p_value_fdr"] = p_adj
    df["significant_raw_5pct"] = df[p_col] < alpha
    df["significant_fdr_5pct"] = reject

    if output_name:
        df.to_csv(OUT / output_name, index=False, encoding="utf-8-sig")

    summary.append({
        "family": family,
        "n_tests": len(df),
        "raw_significant_5pct": int(df["significant_raw_5pct"].sum()),
        "fdr_significant_5pct": int(reject.sum()),
        "min_p_raw": float(df[p_col].min()),
        "min_p_fdr": float(p_adj.min()),
    })
    return df


# 1. Pre/Post 2020 coefficient differences (RQ3)
sub = pd.read_csv(
    OUT / "subperiod_difference_tests.csv", encoding="utf-8-sig"
)
sub = apply_fdr(
    sub, "difference_p_value", "subperiod_difference_RQ3",
    "subperiod_difference_fdr.csv"
)

# 2. Calm/Stress interaction differences, baseline threshold (RQ4)
reg = pd.read_csv(OUT / "regime_results.csv", encoding="utf-8-sig")
reg = reg[reg["regime"] == "Stress"]
apply_fdr(
    reg, "difference_p_value", "regime_difference_RQ4",
    "regime_difference_fdr.csv"
)

# 3. Alternative Stress thresholds (robustness)
rob = pd.read_csv(OUT / "robustness_results.csv", encoding="utf-8-sig")
thr = rob[rob["test"] == "stress_threshold"]
thr = apply_fdr(
    thr, "difference_p_value", "stress_threshold_robustness",
    "threshold_difference_fdr.csv"
)

# 4. LP coefficients across 31 horizons x 3 shocks x 2 assets
lp = pd.read_csv(OUT / "lp_results.csv", encoding="utf-8-sig")
lp = apply_fdr(lp, "p_value", "lp_baseline_coefficients", "lp_fdr.csv")

summary_df = pd.DataFrame(summary)
summary_df.to_csv(
    OUT / "multiple_testing_summary.csv",
    index=False, encoding="utf-8-sig"
)

print("MULTIPLE TESTING SUMMARY (Benjamini-Hochberg, 5%)")
print(summary_df.round(4).to_string(index=False))

print("\nLP coefficients significant after FDR:")
print(
    lp[lp["significant_fdr_5pct"]][[
        "response", "shock", "horizon",
        "estimate", "p_value", "p_value_fdr"
    ]].round(4).to_string(index=False)
)

print("\nMULTIPLE TESTING FINISHED")