
# ============================================================
# 02_download_data.py
# Du an: Dieu kien tai chinh toan cau va thi truong crypto
# Nhiem vu: Tai va luu DU LIEU THO, khong xu ly mau nghien cuu
#
# Output: data/raw/crypto_macro_raw.csv
#
# Khong tao model_dataset.csv tai file nay.
# Khong loc ngay giao dich chung khoan.
# Khong xoa dong co bien vi mo bi thieu.
# Khong forward-fill, backfill hoac noi suy.
# ============================================================

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


# ------------------------------------------------------------
# 1. CAU HINH
# ------------------------------------------------------------

START_DATE = "2018-01-01"
END_DATE = "2026-01-01"  # yfinance khong bao gom ngay end

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = RAW_DIR / "crypto_macro_raw.csv"

DOWNLOAD_TIME_UTC = datetime.now(timezone.utc).isoformat()

TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",
}


# ------------------------------------------------------------
# 2. TAI GIA DONG CUA TU YAHOO FINANCE
# ------------------------------------------------------------

def download_close(ticker: str, variable: str) -> pd.Series:
    """Tai gia dong cua; giu ngay cua nguon, khong dien gia tri thieu."""
    print(f"Dang tai {variable} ({ticker})...")

    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if df.empty:
        raise RuntimeError(
            f"Khong tai duoc {ticker}. "
            "Hay kiem tra ket noi mang va ma tai san."
        )

    # Tuong thich voi ca cot thuong va MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        close_cols = [
            col for col in df.columns
            if any(str(part).lower() == "close" for part in col)
        ]
        if not close_cols:
            raise ValueError(f"Khong tim thay cot Close cua {ticker}.")
        close = df[close_cols[0]]
    else:
        if "Close" not in df.columns:
            raise ValueError(f"Khong tim thay cot Close cua {ticker}.")
        close = df["Close"]

    close = pd.to_numeric(close, errors="coerce")

    # Luu ngay theo nhan ngay cua nguon.
    # Day KHONG phai thoi diem cong bo chinh xac cua chi so vi mo.
    idx = pd.to_datetime(df.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)

    close.index = idx.normalize()
    close.index.name = "date"
    close.name = variable

    close = close[~close.index.duplicated(keep="last")].sort_index()
    close = close.loc[
        (close.index >= pd.Timestamp(START_DATE))
        & (close.index < pd.Timestamp(END_DATE))
    ]

    return close


# ------------------------------------------------------------
# 3. TAI BTC, ETH, VIX, DXY
# ------------------------------------------------------------

series_list = []

for variable, ticker in TICKERS.items():
    series_list.append(download_close(ticker, variable))


# ------------------------------------------------------------
# 4. TAI US2Y TU FRED
# DGS2 co don vi phan tram (%)
# ------------------------------------------------------------

print("Dang tai US2Y (FRED DGS2)...")

fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"
us2y_df = pd.read_csv(fred_url)

required_columns = {"observation_date", "DGS2"}
if not required_columns.issubset(us2y_df.columns):
    raise ValueError(
        "Du lieu FRED khong co cac cot observation_date va DGS2."
    )

us2y_df["date"] = pd.to_datetime(
    us2y_df["observation_date"], errors="coerce"
).dt.normalize()

# FRED co the ma hoa gia tri thieu bang dau cham.
us2y_df["US2Y"] = pd.to_numeric(
    us2y_df["DGS2"], errors="coerce"
)

us2y = (
    us2y_df.dropna(subset=["date"])
    .set_index("date")["US2Y"]
    .sort_index()
)

us2y = us2y.loc[
    (us2y.index >= pd.Timestamp(START_DATE))
    & (us2y.index < pd.Timestamp(END_DATE))
]

us2y.index.name = "date"
us2y = us2y[~us2y.index.duplicated(keep="last")]
series_list.append(us2y.rename("US2Y"))


# ------------------------------------------------------------
# 5. GHEP DU LIEU THO
# Outer join: khong loai ngay vi mot bien bi thieu.
# Chua tao lich crypto lien tuc; viec nay thuoc file 03.
# ------------------------------------------------------------

raw = pd.concat(series_list, axis=1, join="outer").sort_index()
raw.index.name = "date"

raw = raw.loc[
    (raw.index >= pd.Timestamp(START_DATE))
    & (raw.index < pd.Timestamp(END_DATE))
]

raw = raw.reset_index()
raw["date"] = pd.to_datetime(raw["date"]).dt.strftime("%Y-%m-%d")

raw = raw[["date", "BTC", "ETH", "US2Y", "DXY", "VIX"]]
raw.to_csv(RAW_PATH, index=False, encoding="utf-8-sig")

# Xuat them file Excel
EXCEL_PATH = RAW_DIR / "crypto_macro_raw.xlsx"
raw.to_excel(EXCEL_PATH, index=False)

print(f"Da luu file CSV: {RAW_PATH}")
print(f"Da luu file Excel: {EXCEL_PATH}")

# ------------------------------------------------------------
# XUẤT NHẬT KÝ NGUỒN DỮ LIỆU: docs/data_source_log.xlsx
# ------------------------------------------------------------

DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_LOG_PATH = DOCS_DIR / "data_source_log.xlsx"

SOURCE_INFO = {
    "BTC": {
        "source": "Yahoo Finance",
        "ticker": "BTC-USD",
        "unit": "USD/BTC",
        "frequency": "Daily",
    },
    "ETH": {
        "source": "Yahoo Finance",
        "ticker": "ETH-USD",
        "unit": "USD/ETH",
        "frequency": "Daily",
    },
    "VIX": {
        "source": "Yahoo Finance",
        "ticker": "^VIX",
        "unit": "Index points",
        "frequency": "Trading days",
    },
    "DXY": {
        "source": "Yahoo Finance",
        "ticker": "DX-Y.NYB",
        "unit": "Index points",
        "frequency": "Trading days",
    },
    "US2Y": {
        "source": "Federal Reserve Bank of St. Louis (FRED)",
        "ticker": "DGS2",
        "unit": "Percent (%)",
        "frequency": "Business days",
    },
}

source_records = []

for variable, info in SOURCE_INFO.items():
    values = pd.to_numeric(raw[variable], errors="coerce")
    valid_dates = pd.to_datetime(
        raw.loc[values.notna(), "date"], errors="coerce"
    )

    source_records.append({
        "variable": variable,
        "source": info["source"],
        "ticker_or_series": info["ticker"],
        "unit": info["unit"],
        "frequency": info["frequency"],
        "requested_start_date": START_DATE,
        "requested_end_date_exclusive": END_DATE,
        "first_valid_date": (
            valid_dates.min().strftime("%Y-%m-%d")
            if valid_dates.notna().any() else None
        ),
        "last_valid_date": (
            valid_dates.max().strftime("%Y-%m-%d")
            if valid_dates.notna().any() else None
        ),
        "total_rows": len(raw),
        "valid_observations": int(values.notna().sum()),
        "missing_observations": int(values.isna().sum()),
        "missing_rate_percent": round(
            values.isna().mean() * 100, 2
        ),
        "download_time_utc": DOWNLOAD_TIME_UTC,
    })

source_log = pd.DataFrame(source_records)

run_summary = pd.DataFrame([
    {"item": "project", "value": "Macro-crypto shock transmission"},
    {"item": "requested_start_date", "value": START_DATE},
    {"item": "requested_end_date_exclusive", "value": END_DATE},
    {"item": "raw_file", "value": str(RAW_PATH)},
    {"item": "excel_file", "value": str(EXCEL_PATH)},
    {"item": "number_of_rows", "value": len(raw)},
    {"item": "number_of_columns", "value": len(raw.columns)},
    {"item": "download_time_utc", "value": DOWNLOAD_TIME_UTC},
])

with pd.ExcelWriter(SOURCE_LOG_PATH, engine="openpyxl") as writer:
    source_log.to_excel(
        writer, sheet_name="data_sources", index=False
    )
    run_summary.to_excel(
        writer, sheet_name="run_summary", index=False
    )

print(f"Da luu nhat ky nguon du lieu: {SOURCE_LOG_PATH}")

# ------------------------------------------------------------
# 6. KIEM TRA VA GHI NHAN
# ------------------------------------------------------------

variables = ["BTC", "ETH", "US2Y", "DXY", "VIX"]

print("\n" + "=" * 60)
print("KET QUA TAI DU LIEU THO")
print("=" * 60)
print(f"File: {RAW_PATH}")
print(f"So dong: {len(raw):,}")
print(f"Khoang ngay: {raw['date'].min()} -> {raw['date'].max()}")
print("\nSo gia tri thieu:")
print(raw[variables].isna().sum().to_string())
print(f"\nThoi diem tai UTC: {DOWNLOAD_TIME_UTC}")
print("\nHoan tat. File 02 chi tai va luu du lieu tho.")
