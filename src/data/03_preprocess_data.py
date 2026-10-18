
# ============================================================
# 03_preprocess_data.py
# Du an: Dieu kien tai chinh toan cau va thi truong tien ma hoa
# Nhiem vu: Tao bo du lieu chuan dung chung cho TV3 va TV4
#
# INPUT:
#   data/raw/crypto_macro_raw.csv
#   config/research_config.json
#
# OUTPUT:
#   data/processed/model_dataset.csv
#   outputs/tables/preprocessing_quality_report.csv
#
# Quy tac:
# - Lich ngay UTC lien tuc, 2018-01-01 den 2025-12-31.
# - Khong tu dong loai ngay cuoi tuan.
# - Khong forward-fill, backfill hoac noi suy bien vi mo.
# - Tinh loi suat BTC/ETH tren chuoi ngay lien tiep truoc khi loc mau.
# - Bien doi vi mo tai cac ngay co quan sat thuc te.
# ============================================================

from pathlib import Path
import json

import numpy as np
import pandas as pd

# Tao tai lieu TV2 (data dictionary va ban thao phuong phap)
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter



# ------------------------------------------------------------
# 1. CAU HINH DU AN
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "config" / "research_config.json"
RAW_PATH = ROOT / "data" / "raw" / "crypto_macro_raw.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "outputs" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "model_dataset.csv"
QUALITY_REPORT_PATH = REPORT_DIR / "preprocessing_quality_report.csv"

# Dau ra tai lieu TV2, duoc tao cung lan voi tien xu ly
SOURCE_LOG_PATH = ROOT / "docs" / "data_source_log.xlsx"
STATS_PATH = ROOT / "outputs" / "tables" / "descriptive_stats.csv"
CORR_PATH = ROOT / "outputs" / "tables" / "correlation_matrix.csv"
DICT_PATH = ROOT / "docs" / "data_dictionary.xlsx"
METHODOLOGY_PATH = ROOT / "paper" / "drafts" / "02_data_methodology.docx"
REPORT_PATH = METHODOLOGY_PATH

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"Khong tim thay config: {CONFIG_PATH}")

if not RAW_PATH.exists():
    raise FileNotFoundError(f"Khong tim thay du lieu tho: {RAW_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

START_DATE = pd.Timestamp(config["de_tai"]["ngay_bat_dau"])
END_DATE = pd.Timestamp(config["de_tai"]["ngay_ket_thuc"])

if END_DATE < START_DATE:
    raise ValueError("Ngay ket thuc phai sau ngay bat dau.")


# ------------------------------------------------------------
# 2. DOC VA KIEM TRA DU LIEU THO
# ------------------------------------------------------------

raw = pd.read_csv(RAW_PATH)

required_columns = ["date", "BTC", "ETH", "US2Y", "DXY", "VIX"]
missing_columns = [
    col for col in required_columns if col not in raw.columns
]

if missing_columns:
    raise ValueError(
        f"Du lieu tho thieu cac cot: {missing_columns}"
    )

raw = raw[required_columns].copy()
raw["date"] = pd.to_datetime(raw["date"], errors="coerce")

if raw["date"].isna().any():
    raise ValueError("Cot date co gia tri khong the chuyen thanh ngay.")

# Du lieu quy uoc theo ngay UTC; khong giu thanh phan gio.
raw["date"] = raw["date"].dt.normalize()

if raw["date"].duplicated().any():
    duplicate_dates = raw.loc[
        raw["date"].duplicated(keep=False), "date"
    ].dt.strftime("%Y-%m-%d").tolist()

    raise ValueError(
        f"Du lieu tho co ngay trung lap: {duplicate_dates[:10]}"
    )

raw = raw.sort_values("date")
raw = raw.loc[
    raw["date"].between(START_DATE, END_DATE)
].copy()

for col in ["BTC", "ETH", "US2Y", "DXY", "VIX"]:
    raw[col] = pd.to_numeric(raw[col], errors="coerce")

# Gia crypto phai duong khi co quan sat.
for col in ["BTC", "ETH"]:
    invalid = raw[col].notna() & (raw[col] <= 0)

    if invalid.any():
        raise ValueError(
            f"{col} co gia tri gia khong hop le (<= 0)."
        )

raw = raw.set_index("date").sort_index()


# ------------------------------------------------------------
# 3. TAO LICH NGAY UTC LIEN TUC
# ------------------------------------------------------------

calendar = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D",
    name="date",
)

# Reindex tao ngay con thieu, khong tu dien gia tri.
data = raw.reindex(calendar)

# Giu lai cac muc gia goc va gia tri vi mo tai ngay quan sat.
model = data[
    ["BTC", "ETH", "US2Y", "DXY", "VIX"]
].copy()


# ------------------------------------------------------------
# 4. TINH LOI SUAT LOG CRYPTO
# Cong thuc: 100 * ln(P_t / P_(t-1))
# Tinh tren lich ngay lien tiep truoc khi loc mau.
# ------------------------------------------------------------

for col in ["BTC", "ETH"]:
    return_col = f"{col}_log_return_pct"

    previous_price = model[col].shift(1)
    current_price = model[col]

    valid = (
        current_price.notna()
        & previous_price.notna()
        & (current_price > 0)
        & (previous_price > 0)
    )

    model[return_col] = np.nan
    model.loc[valid, return_col] = (
        100 * np.log(
            current_price.loc[valid] / previous_price.loc[valid]
        )
    )


# ------------------------------------------------------------
# 5. BIEN DOI CAC BIEN VI MO
# Chi tinh thay doi giua hai quan sat hop le lien tiep cua nguon.
# Khong xem ngay cuoi tuan la quan sat moi.
# Khong dien cac muc vi mo vao ngay bi thieu.
# ------------------------------------------------------------

macro_rules = {
    "US2Y": {
        "output": "US2Y_change_pp",
        "method": "difference",
    },
    "DXY": {
        "output": "DXY_log_return_pct",
        "method": "log_difference",
    },
    "VIX": {
        "output": "VIX_change_points",
        "method": "difference",
    },
}

for variable, rule in macro_rules.items():
    observed = raw[variable].dropna().sort_index()

    # Khoang cach ngay giua hai quan sat thuc te.
    observation_dates = pd.Series(
        observed.index, index=observed.index
    )
    gap_days = observation_dates.diff().dt.days

    if rule["method"] == "difference":
        transformed = observed.diff()
    else:
        # DXY phai duong de tinh log difference.
        invalid_dxy = observed <= 0

        if invalid_dxy.any():
            raise ValueError("DXY co gia tri khong duong.")

        transformed = 100 * np.log(
            observed / observed.shift(1)
        )

    # Chi gan gia tri bien doi vao ngay co quan sat moi.
    model[rule["output"]] = transformed.reindex(calendar)

    # Ghi lai khoang cach giua cac quan sat vi mo.
    gap_column = f"{variable}_observation_gap_days"
    model[gap_column] = gap_days.reindex(calendar)

    # Danh dau ngay co quan sat goc thuc te.
    flag_column = f"{variable}_observed"
    model[flag_column] = (
        model[variable].notna().astype("int8")
    )


# ------------------------------------------------------------
# 6. KIEM TRA BO DU LIEU CHUAN
# ------------------------------------------------------------

model.index.name = "date"
model = model.reset_index()
model["date"] = model["date"].dt.strftime("%Y-%m-%d")

# Dam bao ngay lien tuc va dung giai doan.
expected_dates = pd.date_range(
    START_DATE, END_DATE, freq="D"
)

actual_dates = pd.to_datetime(model["date"])

if len(model) != len(expected_dates):
    raise AssertionError("So ngay khong khop voi lich ngay ky vong.")

if not actual_dates.reset_index(drop=True).equals(
    pd.Series(expected_dates)
):
    raise AssertionError("Ngay bi thieu, trung hoac sai thu tu.")


# ------------------------------------------------------------
# 7. BAO CAO CHAT LUONG DU LIEU
# ------------------------------------------------------------

quality_records = []

for col in model.columns:
    if col == "date":
        continue

    series = model[col]

    quality_records.append({
        "variable": col,
        "total_rows": len(model),
        "non_missing": int(series.notna().sum()),
        "missing": int(series.isna().sum()),
        "missing_rate_percent": round(
            series.isna().mean() * 100, 2
        ),
    })

quality_report = pd.DataFrame(quality_records)

# Luu bo du lieu chuan duy nhat.
model.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

# Luu bao cao QA rieng, khong phai bo du lieu mo hinh thu hai.
quality_report.to_csv(
    QUALITY_REPORT_PATH, index=False, encoding="utf-8-sig"
)


# ------------------------------------------------------------
# 8. IN KET QUA
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("KET QUA TIEN XU LY DU LIEU")
print("=" * 60)

print(f"So dong: {len(model):,}")
print(f"So cot: {len(model.columns)}")
print(f"Ngay dau: {model['date'].min()}")
print(f"Ngay cuoi: {model['date'].max()}")

print("\nSo gia tri thieu theo bien:")
print(
    model.drop(columns=["date"])
    .isna()
    .sum()
    .to_string()
)

print("\nSo ngay co quan sat vi mo thuc te:")
for variable in ["US2Y", "DXY", "VIX"]:
    print(
        f"{variable}: "
        f"{int(model[f'{variable}_observed'].sum()):,}"
    )

print("\nDa luu bo du lieu chuan:")
print(OUTPUT_PATH)

print("\nDa luu bao cao chat luong:")
print(QUALITY_REPORT_PATH)

print("\nHoan tat muc 03.")


# ============================================================
# 9. TAO DATA DICTIONARY VA BAN THAO PHUONG PHAP (TV2)
# Duoc tich hop vao pipeline 03 de khong can script rieng.
# ============================================================

VARIABLES = {
    "date": ("Ngày quan sát", "Ngày lịch dùng để đồng bộ các chuỗi", "YYYY-MM-DD", "Chỉ mục thời gian", "Lịch ngày liên tục trong giai đoạn nghiên cứu"),
    "BTC": ("Giá Bitcoin đóng cửa", "Giá đóng cửa BTC-USD theo dữ liệu nguồn", "USD", "Giá tài sản", "Yahoo Finance: BTC-USD"),
    "ETH": ("Giá Ethereum đóng cửa", "Giá đóng cửa ETH-USD theo dữ liệu nguồn", "USD", "Giá tài sản", "Yahoo Finance: ETH-USD"),
    "US2Y": ("Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm", "Lợi suất DGS2 quan sát được; không tự điền ngày thiếu", "%/năm", "Biến vĩ mô", "FRED: DGS2"),
    "DXY": ("Chỉ số USD (proxy)", "Giá đóng cửa của mã DX-Y.NYB được dùng làm đại diện chỉ số USD", "Điểm chỉ số", "Biến vĩ mô", "Yahoo Finance: DX-Y.NYB"),
    "VIX": ("Chỉ số biến động kỳ vọng VIX", "Giá đóng cửa chỉ số VIX", "Điểm chỉ số", "Biến rủi ro thị trường", "Yahoo Finance: ^VIX"),
    "BTC_log_return_pct": ("Lợi suất log Bitcoin", "100 × ln(BTC_t / BTC_{t-1}); tính trên lịch ngày liên tục", "%/ngày", "Biến dẫn xuất", "Tính từ BTC"),
    "ETH_log_return_pct": ("Lợi suất log Ethereum", "100 × ln(ETH_t / ETH_{t-1}); tính trên lịch ngày liên tục", "%/ngày", "Biến dẫn xuất", "Tính từ ETH"),
    "US2Y_change_pp": ("Mức thay đổi US2Y", "US2Y_t − US2Y ở lần quan sát hợp lệ trước đó; có thể cách nhau nhiều ngày", "Điểm phần trăm", "Biến dẫn xuất", "Tính từ US2Y; xem observation gap"),
    "US2Y_observation_gap_days": ("Khoảng cách ngày giữa quan sát US2Y", "Số ngày giữa ngày quan sát US2Y hiện tại và ngày quan sát hợp lệ trước đó", "Ngày", "Kiểm soát chất lượng", "Tính từ ngày quan sát US2Y"),
    "US2Y_observed": ("Cờ quan sát US2Y", "1 nếu có quan sát US2Y ở ngày đó; 0 nếu không", "Nhị phân 0/1", "Cờ dữ liệu", "Tính từ US2Y"),
    "DXY_log_return_pct": ("Thay đổi log DXY", "100 × ln(DXY_t / DXY ở lần quan sát hợp lệ trước đó)", "% giữa hai lần quan sát", "Biến dẫn xuất", "Tính từ DXY; xem observation gap"),
    "DXY_observation_gap_days": ("Khoảng cách ngày giữa quan sát DXY", "Số ngày giữa ngày quan sát DXY hiện tại và ngày quan sát hợp lệ trước đó", "Ngày", "Kiểm soát chất lượng", "Tính từ ngày quan sát DXY"),
    "DXY_observed": ("Cờ quan sát DXY", "1 nếu có quan sát DXY ở ngày đó; 0 nếu không", "Nhị phân 0/1", "Cờ dữ liệu", "Tính từ DXY"),
    "VIX_change_points": ("Mức thay đổi VIX", "VIX_t − VIX ở lần quan sát hợp lệ trước đó", "Điểm VIX", "Biến dẫn xuất", "Tính từ VIX; xem observation gap"),
    "VIX_observation_gap_days": ("Khoảng cách ngày giữa quan sát VIX", "Số ngày giữa ngày quan sát VIX hiện tại và ngày quan sát hợp lệ trước đó", "Ngày", "Kiểm soát chất lượng", "Tính từ ngày quan sát VIX"),
    "VIX_observed": ("Cờ quan sát VIX", "1 nếu có quan sát VIX ở ngày đó; 0 nếu không", "Nhị phân 0/1", "Cờ dữ liệu", "Tính từ VIX"),
}


def safe_read_csv(path):
    return pd.read_csv(path) if path.exists() else None


def add_table(doc, headers, rows, font_size=8):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = str(h)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(font_size)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = "" if pd.isna(val) else str(val)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cells[i].paragraphs:
                for run in p.runs:
                    run.font.size = Pt(font_size)
    return table


def format_workbook(path):
    from openpyxl import load_workbook
    wb = load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="156082")
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        for col in ws.columns:
            letter = get_column_letter(col[0].column)
            max_len = max((len(str(c.value)) if c.value is not None else 0) for c in col[:100])
            ws.column_dimensions[letter].width = min(max(max_len + 2, 12), 48)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(path)


def generate_dictionary(df):
    DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    quality = []
    for col in df.columns:
        spec = VARIABLES.get(col, (col, "Chưa có mô tả được khai báo trong script; cần cập nhật từ thiết kế nghiên cứu.", "Chưa xác định", "Chưa phân loại", "Cần bổ sung nguồn/công thức"))
        valid = int(df[col].notna().sum())
        missing = int(df[col].isna().sum())
        rows.append([col, *spec, str(df[col].dtype), valid, missing, round(missing / len(df) * 100, 2) if len(df) else None])
        quality.append([col, len(df), valid, missing, round(missing / len(df) * 100, 2) if len(df) else None, "Không có giá trị thiếu" if missing == 0 else "Giữ NA; không tự động nội suy/điền bù"])
    dictionary_cols = ["Tên biến", "Tên/ý nghĩa", "Định nghĩa", "Đơn vị", "Nhóm biến", "Nguồn/cách tính", "Kiểu dữ liệu", "Số quan sát hợp lệ", "Số thiếu", "Tỷ lệ thiếu (%)"]
    methods = [
        ["Phạm vi", "2018-01-01 đến 2025-12-31; lịch ngày liên tục."],
        ["Tài sản số", "BTC-USD và ETH-USD; giá đóng cửa từ Yahoo Finance."],
        ["VIX", "Mã ^VIX từ Yahoo Finance; chỉ báo biến động kỳ vọng thị trường."],
        ["DXY proxy", "Mã DX-Y.NYB từ Yahoo Finance; cần gọi là proxy/đại diện theo mã tải xuống, không khẳng định là chuỗi DXY chính thức nếu chưa xác minh."],
        ["US2Y", "DGS2 từ FRED; quan sát ngày giao dịch, không có dữ liệu cho mọi ngày lịch."],
        ["Lợi suất crypto", "100 × ln(P_t/P_{t-1}); tính trên chuỗi giá theo lịch ngày liên tục trước khi xử lý các biến vĩ mô."],
        ["Thay đổi US2Y", "Sai phân giữa hai lần quan sát hợp lệ liên tiếp, đơn vị điểm phần trăm; khoảng cách có thể lớn hơn một ngày."],
        ["Thay đổi DXY", "100 × log sai phân giữa hai lần quan sát hợp lệ liên tiếp; kiểm tra gap trước khi diễn giải như lợi suất ngày."],
        ["Thay đổi VIX", "Sai phân giữa hai lần quan sát hợp lệ liên tiếp; khoảng cách có thể lớn hơn một ngày."],
        ["Dữ liệu thiếu", "Không forward-fill, backfill hoặc nội suy trong dataset chuẩn. Biến đổi macro có thể thiếu tại ngày không quan sát được."],
        ["Cờ observed", "1 = có quan sát nguồn tại ngày; 0 = không có quan sát nguồn tại ngày."],
        ["Giới hạn diễn giải", "Các chỉ báo US2Y, DXY và VIX không tự động là cú sốc nhân quả hoặc một chỉ số tổng hợp."],
    ]
    with pd.ExcelWriter(DICT_PATH, engine="openpyxl") as writer:
        pd.DataFrame(rows, columns=dictionary_cols).to_excel(writer, sheet_name="data_dictionary", index=False)
        pd.DataFrame(quality, columns=["Biến", "Tổng số dòng", "Hợp lệ", "Thiếu", "Tỷ lệ thiếu (%)", "Ghi chú xử lý"]).to_excel(writer, sheet_name="data_quality", index=False)
        pd.DataFrame(methods, columns=["Hạng mục", "Mô tả"]).to_excel(writer, sheet_name="sources_and_methods", index=False)
    format_workbook(DICT_PATH)


def generate_report(df, stats, corr):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.7); sec.bottom_margin = Inches(0.7)
    sec.left_margin = Inches(0.8); sec.right_margin = Inches(0.8)
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(11)
    for s in ["Heading 1", "Heading 2", "Heading 3"]:
        styles[s].font.name = "Times New Roman"
    title = doc.add_heading("CHƯƠNG 2. DỮ LIỆU VÀ PHƯƠNG PHÁP XỬ LÝ", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Global Financial Conditions and Cryptocurrency Markets: Nonlinear Transmission of Monetary, Dollar and Risk Shocks to Bitcoin and Ethereum")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True

    dates = pd.to_datetime(df["date"], errors="coerce") if "date" in df else pd.Series(dtype="datetime64[ns]")
    start = dates.min().strftime("%Y-%m-%d") if dates.notna().any() else "chưa xác định"
    end = dates.max().strftime("%Y-%m-%d") if dates.notna().any() else "chưa xác định"
    nrows, ncols = df.shape
    doc.add_heading("2.1. Thiết kế và phạm vi dữ liệu", level=1)
    doc.add_paragraph(f"Nghiên cứu sử dụng dữ liệu chuỗi thời gian với lịch ngày liên tục trong giai đoạn {start} đến {end}. Tập dữ liệu đã xử lý hiện có {nrows:,} dòng và {ncols} cột. Hai tài sản số được phân tích là Bitcoin (BTC) và Ethereum (ETH); các điều kiện tài chính toàn cầu được đại diện bởi lợi suất Kho bạc Mỹ kỳ hạn 2 năm (US2Y), chỉ số USD proxy (DXY) và chỉ số biến động VIX.")
    doc.add_paragraph("Phạm vi dữ liệu và biến được mô tả theo đúng cấu trúc dataset hiện có. Các biến bổ sung hoặc quy tắc phân nhóm thị trường cần được xác định thống nhất trong cấu hình nghiên cứu trước khi dùng cho mô hình suy luận.")

    doc.add_heading("2.2. Nguồn dữ liệu", level=1)
    add_table(doc, ["Biến", "Mã/nguồn", "Ghi chú"], [
        ["Bitcoin", "Yahoo Finance – BTC-USD", "Giá đóng cửa; tần suất ngày."],
        ["Ethereum", "Yahoo Finance – ETH-USD", "Giá đóng cửa; tần suất ngày."],
        ["VIX", "Yahoo Finance – ^VIX", "Chỉ báo biến động kỳ vọng thị trường."],
        ["USD index proxy", "Yahoo Finance – DX-Y.NYB", "Cần ghi rõ là mã proxy được dùng trong pipeline."],
        ["US2Y", "FRED – DGS2", "Lợi suất Kho bạc Mỹ kỳ hạn 2 năm; ngày nghỉ/không giao dịch có thể không có quan sát."],
    ], 8)
    doc.add_paragraph("Nhật ký nguồn dữ liệu nằm tại docs/data_source_log.xlsx nếu có trong repository. Nên lưu thời điểm tải, mã chuỗi, khoảng thời gian và số quan sát hợp lệ để tăng khả năng tái lập.")

    doc.add_heading("2.3. Đồng bộ và làm sạch dữ liệu", level=1)
    doc.add_paragraph("Các chuỗi được đưa về chỉ mục ngày liên tục để thống nhất mốc thời gian. Dữ liệu vĩ mô không được tự động điền tiến, điền lùi hoặc nội suy trong dataset chuẩn. Do đó, giá trị thiếu phản ánh việc nguồn không có quan sát ở ngày tương ứng; không nên diễn giải chúng như giá trị bằng không.")
    doc.add_paragraph("Lợi suất log của BTC và ETH được tính trên lịch giá crypto liên tục trước khi phân tích các biến vĩ mô. Với US2Y, DXY và VIX, các biến thay đổi được tính giữa hai lần quan sát hợp lệ liên tiếp; nếu khoảng cách quan sát dài hơn một ngày, biến đổi đó không tương đương với thay đổi một ngày. Các cột observation_gap_days được giữ lại để nhận diện trường hợp này.")

    doc.add_heading("2.4. Xây dựng biến", level=1)
    add_table(doc, ["Biến", "Công thức/định nghĩa", "Đơn vị"], [
        ["BTC_log_return_pct", "100 × ln(BTC_t / BTC_(t−1))", "%/ngày"],
        ["ETH_log_return_pct", "100 × ln(ETH_t / ETH_(t−1))", "%/ngày"],
        ["US2Y_change_pp", "US2Y_t − US2Y_previous_observed", "Điểm phần trăm"],
        ["DXY_log_return_pct", "100 × ln(DXY_t / DXY_previous_observed)", "% giữa hai lần quan sát"],
        ["VIX_change_points", "VIX_t − VIX_previous_observed", "Điểm VIX"],
        ["*_observed", "1 nếu nguồn có quan sát ở ngày đó; ngược lại 0", "Nhị phân"],
    ], 8)
    doc.add_paragraph("Ký hiệu previous_observed chỉ lần quan sát hợp lệ trước đó, không nhất thiết là ngày lịch liền kề. Vì vậy cần dùng cùng các cột gap để lọc hoặc kiểm tra độ nhạy khi phân tích biến đổi vĩ mô.")

    doc.add_heading("2.5. Kiểm tra chất lượng dữ liệu", level=1)
    quality_rows = []
    for c in df.columns:
        miss = int(df[c].isna().sum())
        quality_rows.append([c, int(df[c].notna().sum()), miss, f"{miss/nrows*100:.2f}%" if nrows else "-"])
    add_table(doc, ["Biến", "Hợp lệ", "Thiếu", "Tỷ lệ thiếu"], quality_rows, 7)
    doc.add_paragraph("Bảng chất lượng được tính lại trực tiếp từ model_dataset.csv khi chạy script. Các giá trị thiếu được giữ nguyên để tránh tạo ra quan sát giả. Cờ observed giúp phân biệt ngày không có dữ liệu nguồn với giá trị biến đổi bị thiếu do chưa có quan sát trước đó.")

    doc.add_heading("2.6. Thống kê mô tả và tương quan", level=1)
    if stats is not None and not stats.empty:
        doc.add_paragraph("Bảng thống kê mô tả dưới đây được đọc từ outputs/tables/descriptive_stats.csv nếu file tồn tại. Cần bảo đảm bảng này được tạo lại từ cùng phiên bản dataset trước khi phát hành báo cáo.")
        add_table(doc, list(stats.columns), stats.head(15).fillna("").astype(str).values.tolist(), 7)
    else:
        doc.add_paragraph("Chưa tìm thấy outputs/tables/descriptive_stats.csv. Hãy chạy script thống kê mô tả của dự án trước để bổ sung bảng kết quả vào báo cáo.")
    if corr is not None and not corr.empty:
        doc.add_paragraph("Ma trận tương quan hiện có được chèn từ outputs/tables/correlation_matrix.csv. Do dữ liệu vĩ mô có thiếu, cỡ mẫu có thể khác nhau giữa từng cặp biến; cần kiểm tra cách tính tương quan (pairwise deletion/listwise deletion) trước khi diễn giải.")
        add_table(doc, list(corr.columns), corr.head(12).fillna("").astype(str).values.tolist(), 7)
    else:
        doc.add_paragraph("Chưa tìm thấy outputs/tables/correlation_matrix.csv; chạy script thống kê mô tả để tạo ma trận tương quan.")
    doc.add_paragraph("Tương quan là thống kê mô tả, không xác lập quan hệ nhân quả. Đặc biệt, tương quan giữa lợi suất crypto và thay đổi US2Y/VIX/DXY không đủ để kết luận rằng biến vĩ mô là cú sốc chính sách ngoại sinh.")

    doc.add_heading("2.7. Phân kỳ mẫu và trạng thái thị trường", level=1)
    doc.add_paragraph("Kế hoạch nghiên cứu có đề cập so sánh giai đoạn trước và sau năm 2020, đồng thời có đề cập ngưỡng VIX hoặc phân vị để xác định trạng thái căng thẳng. Cần chốt một quy tắc nhất quán trong config và báo cáo (ví dụ: VIX ≥ 30 hoặc ngưỡng phân vị được ước lượng trên mẫu huấn luyện). Không nên dùng hai quy tắc thay thế cho nhau mà không giải thích.")
    doc.add_paragraph("Nếu phân tích dự báo sử dụng năm 2025 làm tập kiểm tra ngoài mẫu, các ngưỡng chuẩn hóa hoặc phân vị phải được xác định chỉ từ dữ liệu huấn luyện để tránh rò rỉ thông tin tương lai.")

    doc.add_heading("2.8. Khả năng tái lập", level=1)
    doc.add_paragraph("Các đầu ra tài liệu được sinh bằng src/data/generate_tv2_documentation.py. Script đọc dataset đã xử lý và, nếu có, bảng thống kê mô tả, ma trận tương quan và nhật ký nguồn. Sau khi cập nhật dữ liệu, chạy lại script để đồng bộ data dictionary và bản thảo phương pháp.")
    doc.add_paragraph("Lệnh chạy từ thư mục gốc repository: python src/data/generate_tv2_documentation.py. Các thư viện cần thiết gồm pandas, openpyxl và python-docx.")

    doc.add_heading("2.9. Hạn chế dữ liệu", level=1)
    doc.add_paragraph("(1) Các nguồn có lịch giao dịch và lịch công bố khác nhau; ngày lịch không đồng nghĩa với thời điểm thông tin đã sẵn có cho nhà đầu tư. (2) Dataset hiện lưu ngày quan sát nhưng không thể hiện đầy đủ timestamp công bố/khả dụng của từng giá trị vĩ mô, nên cần thận trọng khi diễn giải theo thời gian thực. (3) DXY dùng mã DX-Y.NYB trong pipeline nên cần mô tả là proxy nếu chưa xác nhận tính tương đương với chỉ số chuẩn. (4) US2Y, DXY và VIX là các chỉ báo riêng biệt; không tự động gọi chúng là một chỉ số tổng hợp hay cú sốc nhân quả. (5) Những biến được tính giữa các lần quan sát hợp lệ có thể bao phủ nhiều ngày, cần xử lý observation gap trong các phân tích tiếp theo.")

    doc.save(REPORT_PATH)



# Tao tai lieu tu bo du lieu vua tien xu ly va cac bang TV2 neu da co.
# Neu chua chay 04_descriptive_stats.py, bao cao se ghi ro bang nao chua co.
_stats = safe_read_csv(STATS_PATH)
_corr = safe_read_csv(CORR_PATH)
generate_dictionary(model)
generate_report(model, _stats, _corr)

print("\nDa tao tai lieu TV2:")
print(f"- {DICT_PATH.relative_to(ROOT)}")
print(f"- {METHODOLOGY_PATH.relative_to(ROOT)}")