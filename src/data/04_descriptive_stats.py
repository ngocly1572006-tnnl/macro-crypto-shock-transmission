
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "processed" / "model_dataset.csv"
TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay du lieu: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 1. Thong ke mo ta
    numeric_cols = df.select_dtypes(include="number").columns
    descriptive = df[numeric_cols].describe().T
    descriptive["missing_count"] = df[numeric_cols].isna().sum()
    descriptive["missing_rate_pct"] = (
        df[numeric_cols].isna().mean() * 100
    )
    descriptive["valid_count"] = df[numeric_cols].count()

    descriptive.to_csv(
        TABLE_DIR / "descriptive_stats.csv",
        encoding="utf-8-sig"
    )

    # 2. Tuong quan giua cac bien bien dong
    correlation_cols = [
        "BTC_log_return_pct",
        "ETH_log_return_pct",
        "US2Y_change_pp",
        "DXY_log_return_pct",
        "VIX_change_points",
    ]

    missing_cols = [
        col for col in correlation_cols if col not in df.columns
    ]
    if missing_cols:
        raise ValueError(f"Thieu cot: {missing_cols}")

    corr = df[correlation_cols].corr(method="pearson")
    corr.to_csv(
        TABLE_DIR / "correlation_matrix.csv",
        encoding="utf-8-sig"
    )

    # 3. Bieu do xu huong gia crypto, chuan hoa ve moc 100
    fig, ax = plt.subplots(figsize=(12, 6))

    for col, label in [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
    ]:
        valid = df[["date", col]].dropna()
        if valid.empty:
            continue

        base = valid[col].iloc[0]
        if pd.notna(base) and base != 0:
            indexed = valid[col] / base * 100
            ax.plot(valid["date"], indexed, label=label)

    ax.set_title("Crypto Price Trends (Indexed to 100)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Index (first observation = 100)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        FIGURE_DIR / "crypto_price_trends.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close(fig)

    # 4. Heatmap tuong quan
    values = corr.to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(
        values,
        vmin=-1,
        vmax=1,
        aspect="auto"
    )

    ax.set_xticks(range(len(correlation_cols)))
    ax.set_yticks(range(len(correlation_cols)))
    ax.set_xticklabels(
        correlation_cols, rotation=45, ha="right"
    )
    ax.set_yticklabels(correlation_cols)

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            label = "NA" if np.isnan(value) else f"{value:.2f}"
            ax.text(j, i, label, ha="center", va="center")

    ax.set_title("Correlation Matrix of Crypto and Macro Changes")
    fig.colorbar(image, ax=ax, label="Pearson correlation")
    fig.tight_layout()
    fig.savefig(
        FIGURE_DIR / "correlation_heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close(fig)

    print("=" * 60)
    print("HOAN TAT MUC 04 - THONG KE MO TA")
    print("=" * 60)
    print(f"So dong du lieu: {len(df):,}")
    print(f"So bien dinh luong: {len(numeric_cols)}")
    print("\nDa tao:")
    print(TABLE_DIR / "descriptive_stats.csv")
    print(TABLE_DIR / "correlation_matrix.csv")
    print(FIGURE_DIR / "crypto_price_trends.png")
    print(FIGURE_DIR / "correlation_heatmap.png")

    print("\nTuong quan Pearson:")
    print(corr.round(3).to_string())


if __name__ == "__main__":
    main()
