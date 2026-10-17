
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

# ==================================================
# 1. CAU HINH
# ==================================================
ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT / "data" / "raw"
DOCS_DIR = ROOT / "docs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2018-01-01"
END_DATE = "2026-01-01"  # Yahoo: ngay ket thuc khong bao gom

# ==================================================
# 2. CAC NGUON DU LIEU
# ==================================================
YAHOO_TICKERS = {
    "BTC_close": "BTC-USD",
    "ETH_close": "ETH-USD",
    "VIX": "^VIX",
    "USD_INDEX": "DX-Y.NYB",
}

FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv"
    f"?id=DGS2&cosd={START_DATE}&coed=2025-12-31"
)

source_log = []
series_list = []

retrieved_at = datetime.now(timezone.utc).isoformat()


def record_source(variable, source, url, unit, status, data=None):
    """Ghi nhat ky nguon va tinh trang thu thap."""

    if data is not None and not data.empty:
        dates = pd.to_datetime(data["date"])
        min_date = dates.min().date().isoformat()
        max_date = dates.max().date().isoformat()
        n_obs = len(data)
        n_missing = int(data["value"].isna().sum())
    else:
        min_date = None
        max_date = None
        n_obs = 0
        n_missing = None

    source_log.append({
        "variable": variable,
        "source": source,
        "url": url,
        "frequency": "Daily",
        "unit": unit,
        "sample_start": START_DATE,
        "sample_end": "2025-12-31",
        "retrieved_at_utc": retrieved_at,
        "actual_start": min_date,
        "actual_end": max_date,
        "n_observations": n_obs,
        "n_missing": n_missing,
        "status": status,
    })


# ==================================================
# 3. TAI BTC, ETH, VIX, USD INDEX
# ==================================================
for variable, ticker in YAHOO_TICKERS.items():
    url = f"https://finance.yahoo.com/quote/{ticker}/history/"

    try:
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
            record_source(
                variable, "Yahoo Finance", url, "See source",
                "FAILED: empty response"
            )
            print(f"[ERROR] {variable}: khong co du lieu.")
            continue

        # Ho tro ca ten cot don va MultiIndex
        close = df["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        result = pd.DataFrame({
            "date": pd.to_datetime(df.index).tz_localize(None).date,
            "value": pd.to_numeric(close, errors="coerce").to_numpy(),
        })

        result["date"] = pd.to_datetime(result["date"])
        result = result.dropna(subset=["date", "value"])
        result = result.drop_duplicates("date").sort_values("date")
        result = result.rename(columns={"value": variable})

        if result.empty:
            record_source(
                variable, "Yahoo Finance", url, "See source",
                "FAILED: no valid observations"
            )
            continue

        series_list.append(result)
        log_data = result.rename(columns={variable: "value"})
        record_source(
            variable, "Yahoo Finance", url, "See source",
            "OK", log_data
        )

        print(
            f"[OK] {variable}: {len(result)} observations, "
            f"{result['date'].min().date()} -> "
            f"{result['date'].max().date()}"
        )

    except Exception as exc:
        record_source(
            variable, "Yahoo Finance", url, "See source",
            f"FAILED: {exc}"
        )
        print(f"[ERROR] {variable}: {exc}")


# ==================================================
# 4. TAI US2Y TU FRED
# ==================================================
try:
    fred = pd.read_csv(FRED_URL)

    # FRED CSV thuong co cot observation_date va DGS2
    date_col = "observation_date" if "observation_date" in fred.columns else "DATE"

    if date_col not in fred.columns or "DGS2" not in fred.columns:
        raise ValueError(
            f"Cau truc CSV FRED khong dung nhu mong doi: {list(fred.columns)}"
        )

    us2y = pd.DataFrame({
        "date": pd.to_datetime(fred[date_col], errors="coerce"),
        "US2Y": pd.to_numeric(fred["DGS2"], errors="coerce"),
    })

    # FRED dung dau cham de bieu thi quan sat thieu.
    # Chua dien gia tri thieu o buoc tai du lieu tho.
    us2y = us2y.dropna(subset=["date"])
    us2y = us2y.drop_duplicates("date").sort_values("date")

    series_list.append(us2y)

    log_data = us2y.rename(columns={"US2Y": "value"})
    record_source(
        "US2Y",
        "FRED - Federal Reserve Bank of St. Louis",
        FRED_URL,
        "% per annum",
        "OK",
        log_data,
    )

    print(f"[OK] US2Y: {len(us2y)} daily calendar observations")

except Exception as exc:
    record_source(
        "US2Y", "FRED", FRED_URL, "% per annum",
        f"FAILED: {exc}"
    )
    print(f"[ERROR] US2Y: {exc}")


# ==================================================
# 5. KIEM TRA VA GHEP DU LIEU
# ==================================================
if len(series_list) != len(YAHOO_TICKERS) + 1:
    print(
        "\nCANH BAO: Chua tai duoc tat ca 5 chuoi. "
        "Kiem tra log va khong tu dien du lieu gia."
    )

if not series_list:
    raise RuntimeError("Khong tai duoc chuoi du lieu nao.")

raw = series_list[0]

for series in series_list[1:]:
    raw = raw.merge(series, on="date", how="outer")

raw["date"] = pd.to_datetime(raw["date"])
raw = raw.sort_values("date").drop_duplicates("date")

raw = raw[
    (raw["date"] >= pd.Timestamp(START_DATE))
    & (raw["date"] <= pd.Timestamp("2025-12-31"))
]

expected_cols = [
    "date", "BTC_close", "ETH_close", "VIX",
    "USD_INDEX", "US2Y"
]

for col in expected_cols:
    if col not in raw.columns:
        raw[col] = pd.NA

raw = raw[expected_cols]

# ==================================================
# 6. XUAT FILE
# ==================================================
raw_path = RAW_DIR / "crypto_macro_raw.csv"
log_path = DOCS_DIR / "data_source_log.xlsx"

raw.to_csv(raw_path, index=False, date_format="%Y-%m-%d")
pd.DataFrame(source_log).to_excel(log_path, index=False)

print("\n===== KET QUA THU THAP =====")
print("Raw data:", raw_path)
print("Source log:", log_path)
print("Date range:", raw["date"].min(), "->", raw["date"].max())
print("\nMissing values:")
print(raw.isna().sum())
print("\nFile da duoc tao. Hay kiem tra log truoc khi su dung.")
