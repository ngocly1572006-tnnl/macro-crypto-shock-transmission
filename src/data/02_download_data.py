
# ============================================================
# 02_download_data.py
# Đề tài: Điều kiện tài chính toàn cầu và thị trường tiền mã hóa
# Giai đoạn: 2018-01-01 đến 2025-12-31
# Tần suất: Hằng ngày
# Quy ước ngày crypto: UTC
#
# OUTPUT:
# 1. crypto_macro_raw.csv  : dữ liệu thô ban đầu
# 2. crypto_macro_full.csv : dữ liệu đã xử lý, ngày chung
# 3. crypto_macro_miss.csv : BTC và ETH đủ 7 ngày/tuần
# ============================================================

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


# ------------------------------------------------------------
# 1. CẤU HÌNH
# ------------------------------------------------------------

START_DATE = "2018-01-01"
END_DATE = "2026-01-01"  # Ngày kết thúc không bao gồm trong yfinance

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = RAW_DIR / "crypto_macro_raw.csv"
FULL_PATH = RAW_DIR / "crypto_macro_full.csv"
MISS_PATH = RAW_DIR / "crypto_macro_miss.csv"

DOWNLOAD_TIME = datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------
# 2. HÀM TẢI GIÁ ĐÓNG CỬA TỪ YAHOO FINANCE
# ------------------------------------------------------------

def download_close(ticker, variable):
    print(f"Đang tải {variable} ({ticker})...")

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
            f"Không tải được {ticker}. "
            "Kiểm tra kết nối mạng hoặc mã tài sản."
        )

    # Hỗ trợ cả tên cột thông thường và MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        close_cols = [
            col for col in df.columns
            if str(col[0]).lower() == "close"
        ]
        if not close_cols:
            raise ValueError(f"Không tìm thấy giá đóng cửa của {ticker}.")
        close = df[close_cols[0]]
    else:
        if "Close" not in df.columns:
            raise ValueError(f"Không tìm thấy giá đóng cửa của {ticker}.")
        close = df["Close"]

    close = pd.to_numeric(close, errors="coerce")

    # Ngày của giá crypto được quy ước theo UTC.
    # Với các chỉ số Mỹ, đây là ngày giao dịch của nguồn;
    # không được diễn giải nó thành thời điểm công bố chính xác.
    idx = pd.to_datetime(df.index, utc=True)
    close.index = idx.tz_convert(None).normalize()
    close.index.name = "date"
    close.name = variable

    close = close[~close.index.duplicated(keep="last")].sort_index()
    close = close.loc[
        (close.index >= pd.Timestamp(START_DATE))
        & (close.index < pd.Timestamp(END_DATE))
    ]

    return close


# ------------------------------------------------------------
# 3. TẢI BTC, ETH, VIX VÀ DXY
# ------------------------------------------------------------

btc = download_close("BTC-USD", "BTC")
eth = download_close("ETH-USD", "ETH")
vix = download_close("^VIX", "VIX")
dxy = download_close("DX-Y.NYB", "DXY")


# ------------------------------------------------------------
# 4. TẢI LỢI SUẤT TPCP MỸ 2 NĂM TỪ FRED
# DGS2: đơn vị phần trăm (%)
# ------------------------------------------------------------

print("Đang tải US2Y (FRED DGS2)...")

fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"
us2y_df = pd.read_csv(fred_url)

required_fred_cols = {"observation_date", "DGS2"}
if not required_fred_cols.issubset(us2y_df.columns):
    raise ValueError(
        "Dữ liệu FRED không có cột observation_date và DGS2."
    )

us2y_df["date"] = pd.to_datetime(
    us2y_df["observation_date"], errors="coerce"
).dt.normalize()

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


# ------------------------------------------------------------
# 5. TẠO DỮ LIỆU THÔ BAN ĐẦU
# Outer join để không loại ngày chỉ vì một biến bị thiếu.
# Không forward-fill, backfill hoặc nội suy.
# ------------------------------------------------------------

raw = pd.concat([btc, eth, vix, dxy, us2y], axis=1, join="outer")
raw.index.name = "date"
raw = raw.sort_index()

raw = raw.loc[
    (raw.index >= pd.Timestamp(START_DATE))
    & (raw.index < pd.Timestamp(END_DATE))
]

raw = raw.reset_index()
raw["date"] = raw["date"].dt.strftime("%Y-%m-%d")

raw = raw[["date", "BTC", "ETH", "VIX", "DXY", "US2Y"]]

raw.to_csv(RAW_PATH, index=False, encoding="utf-8-sig")
print(f"Đã lưu dữ liệu thô: {RAW_PATH}")


# ------------------------------------------------------------
# 6. TẠO crypto_macro_full.csv
# Bộ truyền dẫn: ngày thứ Hai đến thứ Sáu, đủ 5 biến.
#
# Không tự điền dữ liệu vĩ mô còn thiếu.
# Chỉ giữ ngày có quan sát hợp lệ cho tất cả biến.
# ------------------------------------------------------------

processed = raw.copy()
processed["date"] = pd.to_datetime(processed["date"])

# Chỉ giữ ngày thứ Hai đến thứ Sáu.
# Sau đó yêu cầu đủ dữ liệu cho cả 5 biến.
processed = processed[
    processed["date"].dt.dayofweek < 5
].copy()

variables = ["BTC", "ETH", "VIX", "DXY", "US2Y"]

missing_before_filter = processed[variables].isna().sum()
print("\nSố giá trị thiếu trước khi lọc bộ truyền dẫn:")
print(missing_before_filter.to_string())

transmission = processed.dropna(subset=variables).copy()
transmission = transmission.sort_values("date")

# Không tính lợi suất tại bước tải dữ liệu.
# Việc tạo sai phân/lợi suất cần kiểm tra khoảng cách ngày
# trong chuỗi sau khi đã chọn mẫu phân tích.
transmission["date"] = transmission["date"].dt.strftime("%Y-%m-%d")

transmission.to_csv(FULL_PATH, index=False, encoding="utf-8-sig")
print(f"\nĐã lưu dữ liệu đã xử lý: {FULL_PATH}")


# ------------------------------------------------------------
# 7. TẠO crypto_macro_miss.csv
# Chỉ có date, BTC, ETH; giữ toàn bộ ngày UTC.
# Không loại thứ Bảy, Chủ nhật và ngày lễ.
# ------------------------------------------------------------

crypto = pd.concat([btc, eth], axis=1, join="outer")
crypto.index.name = "date"
crypto = crypto.sort_index()

# Tạo lịch ngày UTC liên tục trong toàn bộ giai đoạn.
calendar = pd.date_range(
    start=START_DATE,
    end="2025-12-31",
    freq="D",
    name="date",
)

crypto = crypto.reindex(calendar)
crypto = crypto.reset_index()
crypto["date"] = crypto["date"].dt.strftime("%Y-%m-%d")
crypto = crypto[["date", "BTC", "ETH"]]

crypto.to_csv(MISS_PATH, index=False, encoding="utf-8-sig")
print(f"Đã lưu dữ liệu BTC/ETH đủ ngày: {MISS_PATH}")


# ------------------------------------------------------------
# 8. NHẬT KÝ CHẤT LƯỢNG VÀ THỐNG KÊ TỔNG QUAN
# ------------------------------------------------------------

print("\n" + "=" * 55)
print("KIỂM TRA BA FILE ĐẦU RA")
print("=" * 55)

print("\n1. crypto_macro_raw.csv")
print(f"Số dòng: {len(raw):,}")
print(f"Số giá trị thiếu:\n{raw[variables].isna().sum().to_string()}")

print("\n2. crypto_macro_full.csv")
print(f"Số dòng: {len(transmission):,}")
if not transmission.empty:
    print(
        f"Khoảng ngày: {transmission['date'].min()} "
        f"đến {transmission['date'].max()}"
    )
print(f"Số giá trị thiếu: {transmission[variables].isna().sum().sum()}")

print("\n3. crypto_macro_miss.csv")
print(f"Số dòng: {len(crypto):,}")
print(f"Số ngày BTC thiếu: {crypto['BTC'].isna().sum()}")
print(f"Số ngày ETH thiếu: {crypto['ETH'].isna().sum()}")

print("\nĐã hoàn thành tải và xuất dữ liệu.")
print(f"Thời điểm chạy UTC: {DOWNLOAD_TIME}")
