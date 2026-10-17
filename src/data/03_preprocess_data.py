
"""
03_preprocess_data.py
Project: macro-crypto-shock-transmission

Mục đích:
- Đọc dữ liệu thô và giữ nguyên file gốc.
- Chuẩn hóa dữ liệu và tính các biến nghiên cứu.
- Đồng bộ theo ngày có đủ dữ liệu thị trường Mỹ.
- Xuất model_dataset.csv và data_dictionary.xlsx.
"""

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# 1. ĐƯỜNG DẪN VÀ CẤU HÌNH
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = ROOT / "data" / "raw" / "crypto_macro_raw.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
DICTIONARY_DIR = ROOT / "docs"

OUTPUT_FILE = OUTPUT_DIR / "model_dataset.csv"
DICTIONARY_FILE = DICTIONARY_DIR / "data_dictionary.xlsx"

START_DATE = "2018-01-01"
END_DATE = "2025-12-31"

REQUIRED_COLUMNS = [
    "date",
    "BTC_close",
    "ETH_close",
    "VIX",
    "USD_INDEX",
    "US2Y",
]


# ============================================================
# 2. ĐỌC VÀ KIỂM TRA DỮ LIỆU THÔ
# ============================================================

def load_raw_data():
    """Đọc dữ liệu thô, không chỉnh sửa file nguồn."""

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file dữ liệu thô: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Thiếu các cột bắt buộc: {missing_columns}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    # Chuẩn hóa ngày
    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    ).dt.normalize()

    if df["date"].isna().any():
        raise ValueError(
            "Cột date có giá trị không thể chuyển thành ngày."
        )

    # Chuyển các cột dữ liệu thành dạng số.
    # Giá trị không hợp lệ được chuyển thành NaN, không thành 0.
    numeric_columns = [
        "BTC_close",
        "ETH_close",
        "VIX",
        "USD_INDEX",
        "US2Y",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    # Kiểm tra ngày trùng trước khi tính toán
    if df["date"].duplicated().any():
        duplicated_dates = (
            df.loc[df["date"].duplicated(False), "date"]
            .dt.strftime("%Y-%m-%d")
            .tolist()
        )
        raise ValueError(
            "Dữ liệu có ngày trùng. Cần kiểm tra nguồn trước khi "
            f"tiếp tục. Ví dụ: {duplicated_dates[:10]}"
        )

    # Giới hạn mẫu nghiên cứu
    df = df.loc[
        df["date"].between(START_DATE, END_DATE)
    ].copy()

    df = df.sort_values("date").reset_index(drop=True)

    if df.empty:
        raise ValueError(
            "Không có dữ liệu trong giai đoạn nghiên cứu."
        )

    # Giá tài sản và các chỉ số dùng trong log phải dương.
    # US2Y có thể âm trong một số thị trường, vì vậy không
    # áp dụng điều kiện dương cho US2Y.
    for col in ["BTC_close", "ETH_close", "USD_INDEX"]:
        df.loc[df[col] <= 0, col] = np.nan

    df.loc[df["VIX"] < 0, "VIX"] = np.nan

    return df


# ============================================================
# 3. TÍNH CÁC BIẾN NGHIÊN CỨU
# ============================================================

def create_variables(df):
    """
    Tính biến thay đổi trên chuỗi quan sát gốc đã sắp xếp.
    Không điền giá trị thiếu và không dùng dữ liệu tương lai
    để thay thế dữ liệu quá khứ.
    """

    df = df.copy()

    # Lợi suất log hằng ngày của tiền mã hóa
    df["BTC_log_return"] = np.log(
        df["BTC_close"] / df["BTC_close"].shift(1)
    )

    df["ETH_log_return"] = np.log(
        df["ETH_close"] / df["ETH_close"].shift(1)
    )

    # Thay đổi tuyệt đối của VIX
    df["VIX_change"] = df["VIX"].diff()

    # Thay đổi log của USD Index
    df["USD_log_change"] = np.log(
        df["USD_INDEX"] / df["USD_INDEX"].shift(1)
    )

    # US2Y được ghi theo đơn vị phần trăm (%/năm).
    # Chênh lệch 4.25 - 4.10 = 0.15 điểm phần trăm.
    df["US2Y_change"] = df["US2Y"].diff()

    # Biến phụ thuộc tham khảo cho mô hình biến động:
    # trị tuyệt đối lợi suất log của chính ngày đó.
    df["BTC_abs_log_return"] = df["BTC_log_return"].abs()
    df["ETH_abs_log_return"] = df["ETH_log_return"].abs()

    return df


# ============================================================
# 4. ĐỒNG BỘ THEO NGÀY GIAO DỊCH THỊ TRƯỜNG MỸ
# ============================================================

def align_trading_days(df):
    """
    Chỉ giữ các ngày có đủ:
    - Giá BTC và ETH
    - VIX, USD Index và US2Y
    - Các biến thay đổi tương ứng

    Không forward-fill, backward-fill hoặc nội suy.
    """

    df = df.copy()

    required_for_model = [
        "BTC_close",
        "ETH_close",
        "VIX",
        "USD_INDEX",
        "US2Y",
        "BTC_log_return",
        "ETH_log_return",
        "VIX_change",
        "USD_log_change",
        "US2Y_change",
    ]

    # Giữ lại những ngày có đủ dữ liệu thực tế.
    # Các ngày thiếu không được tự động điền.
    model_df = df.dropna(
        subset=required_for_model
    ).copy()

    model_df = model_df.sort_values(
        "date"
    ).reset_index(drop=True)

    # Tạo ngày giao dịch trước đó để kiểm tra khoảng cách.
    # Không giả định mọi quan sát liên tiếp đều cách nhau 1 ngày.
    model_df["previous_observation_date"] = (
        model_df["date"].shift(1)
    )

    
    model_df["days_since_previous_observation"] = (
        model_df["date"] -
        model_df["previous_observation_date"]
    ).dt.days

    # Đánh dấu khoảng cách giữa các quan sát
    model_df["is_consecutive_calendar_day"] = (
        model_df["days_since_previous_observation"] == 1
    )

    # Biến mục tiêu ML: trị tuyệt đối lợi suất log của
    # quan sát kế tiếp trong chuỗi ngày giao dịch đã đồng bộ.
    # Tại ngày t, target là biến động tại ngày t+1.
    model_df["BTC_target_next_abs_return"] = (
        model_df["BTC_abs_log_return"].shift(-1)
    )

    model_df["ETH_target_next_abs_return"] = (
        model_df["ETH_abs_log_return"].shift(-1)
    )

    return model_df



# ============================================================
# 5. TỪ ĐIỂN DỮ LIỆU
# ============================================================

def create_data_dictionary():
    """Tạo từ điển mô tả các biến trong bộ dữ liệu."""

    rows = [
        {
            "variable": "date",
            "description": "Ngày quan sát",
            "unit": "YYYY-MM-DD",
            "formula": "Ngày lấy từ dữ liệu nguồn",
        },
        {
            "variable": "BTC_close",
            "description": "Giá đóng cửa Bitcoin",
            "unit": "USD",
            "formula": "Giá đóng cửa từ nguồn dữ liệu",
        },
        {
            "variable": "ETH_close",
            "description": "Giá đóng cửa Ethereum",
            "unit": "USD",
            "formula": "Giá đóng cửa từ nguồn dữ liệu",
        },
        {
            "variable": "VIX",
            "description": "Chỉ số biến động kỳ vọng thị trường chứng khoán Mỹ",
            "unit": "Điểm chỉ số",
            "formula": "Giá trị VIX từ nguồn dữ liệu",
        },
        {
            "variable": "USD_INDEX",
            "description": "Chỉ số USD được sử dụng trong nghiên cứu",
            "unit": "Điểm chỉ số",
            "formula": "Giá trị USD Index từ nguồn dữ liệu",
        },
        {
            "variable": "US2Y",
            "description": "Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm",
            "unit": "%/năm",
            "formula": "Giá trị US2Y từ nguồn dữ liệu",
        },
        {
            "variable": "BTC_log_return",
            "description": "Lợi suất log Bitcoin",
            "unit": "Log return",
            "formula": "ln(BTC_close_t / BTC_close_t-1)",
        },
        {
            "variable": "ETH_log_return",
            "description": "Lợi suất log Ethereum",
            "unit": "Log return",
            "formula": "ln(ETH_close_t / ETH_close_t-1)",
        },
        {
            "variable": "VIX_change",
            "description": "Mức thay đổi VIX",
            "unit": "Điểm chỉ số",
            "formula": "VIX_t - VIX_t-1",
        },
        {
            "variable": "USD_log_change",
            "description": "Mức thay đổi log của USD Index",
            "unit": "Log change",
            "formula": "ln(USD_INDEX_t / USD_INDEX_t-1)",
        },
        {
            "variable": "US2Y_change",
            "description": "Mức thay đổi lợi suất US2Y",
            "unit": "Điểm phần trăm",
            "formula": "US2Y_t - US2Y_t-1",
        },
        {
            "variable": "BTC_abs_log_return",
            "description": "Trị tuyệt đối lợi suất log Bitcoin trong ngày",
            "unit": "Giá trị tuyệt đối log return",
            "formula": "abs(BTC_log_return)",
        },
        {
            "variable": "ETH_abs_log_return",
            "description": "Trị tuyệt đối lợi suất log Ethereum trong ngày",
            "unit": "Giá trị tuyệt đối log return",
            "formula": "abs(ETH_log_return)",
        },
        {
            "variable": "previous_observation_date",
            "description": "Ngày của quan sát hợp lệ trước đó trong mẫu đã đồng bộ",
            "unit": "YYYY-MM-DD",
            "formula": "date.shift(1)",
        },
        {
            "variable": "days_since_previous_observation",
            "description": "Số ngày lịch từ quan sát hợp lệ trước đó",
            "unit": "Ngày",
            "formula": "date - previous_observation_date",
        },

        {
            "variable": "is_consecutive_calendar_day",
            "description": "Đánh dấu ngày hiện tại cách quan sát trước đúng 1 ngày lịch",
            "unit": "Boolean",
            "formula": "days_since_previous_observation == 1",
        },
        {
            "variable": "BTC_target_next_abs_return",
            "description": "Trị tuyệt đối lợi suất log BTC tại quan sát kế tiếp trong mẫu đồng bộ",
            "unit": "Giá trị tuyệt đối log return",
            "formula": "BTC_abs_log_return.shift(-1)",
        },
        {
            "variable": "ETH_target_next_abs_return",
            "description": "Trị tuyệt đối lợi suất log ETH tại quan sát kế tiếp trong mẫu đồng bộ",
            "unit": "Giá trị tuyệt đối log return",
            "formula": "ETH_abs_log_return.shift(-1)",
        },

    ]

    return pd.DataFrame(rows)


# ============================================================
# 6. CHẠY PIPELINE VÀ XUẤT KẾT QUẢ
# ============================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DICTIONARY_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("BƯỚC 03 - TIỀN XỬ LÝ DỮ LIỆU")
    print("=" * 60)

    raw_df = load_raw_data()

    print(f"Số dòng dữ liệu thô: {len(raw_df):,}")
    print(
        "Giai đoạn: "
        f"{raw_df['date'].min().date()} -> "
        f"{raw_df['date'].max().date()}"
    )

    print("\nSố giá trị thiếu trong dữ liệu thô:")
    print(raw_df.isna().sum().to_string())

    transformed_df = create_variables(raw_df)

    # Chỉ chọn mẫu đầy đủ cho bộ dữ liệu mô hình.
    model_df = align_trading_days(transformed_df)

    # Không xuất index pandas thành một cột không cần thiết.
    model_df.to_csv(
        OUTPUT_FILE,
        index=False,
        date_format="%Y-%m-%d",
    )

    dictionary_df = create_data_dictionary()
    dictionary_df.to_excel(
        DICTIONARY_FILE,
        index=False,
        sheet_name="Data Dictionary",
    )

    print("\n" + "=" * 60)
    print("KẾT QUẢ TIỀN XỬ LÝ")
    print("=" * 60)

    print(f"Số dòng sau đồng bộ: {len(model_df):,}")

    if not model_df.empty:
        print(
            "Ngày đầu/cuối: "
            f"{model_df['date'].min().date()} -> "
            f"{model_df['date'].max().date()}"
        )

    print("\nSố dòng bị loại khỏi mẫu đầy đủ:")
    print(f"{len(transformed_df) - len(model_df):,}")

    print("\nSố giá trị thiếu trong bộ dữ liệu mô hình:")
    print(model_df.isna().sum().to_string())

    print("\nCác khoảng cách giữa những quan sát đã đồng bộ:")
    print(
        model_df["days_since_previous_observation"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    print("\nFile đầu ra:")
    print(f"Model dataset: {OUTPUT_FILE}")
    print(f"Data dictionary: {DICTIONARY_FILE}")

    print(
        "\nLƯU Ý: BTC_abs_log_return và ETH_abs_log_return "
        "là biến trị tuyệt đối lợi suất cùng ngày, chưa phải "
        "biến mục tiêu lợi suất tuyệt đối ngày kế tiếp."
    )


if __name__ == "__main__":
    main()
