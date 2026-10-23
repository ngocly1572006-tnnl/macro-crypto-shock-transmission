
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
from docx.shared import Pt, RGBColor


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


def add_table(doc, headers, rows, font_size=13):
    from docx.shared import RGBColor

    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Header
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = str(header)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    # Nội dung
    for row in rows:
        cells = table.add_row().cells

        for i, value in enumerate(row):
            cells[i].text = (
                "" if pd.isna(value) else str(value)
            )
            cells[i].vertical_alignment = (
                WD_CELL_VERTICAL_ALIGNMENT.CENTER
            )

    # Áp dụng định dạng cho toàn bộ ô, bao gồm header
    for row_idx, row in enumerate(table.rows):
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.line_spacing = 1.5
                paragraph.paragraph_format.space_before = Pt(0)
                paragraph.paragraph_format.space_after = Pt(0)

                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(13)
                    run.font.color.rgb = RGBColor(0, 0, 0)

                    if row_idx == 0:
                        run.bold = True

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


def _fmt_num(value, digits=3):
    """Format numeric cells consistently with Chapters 3 and 4."""
    if pd.isna(value):
        return "—"
    if isinstance(value, (int, np.integer)) or (isinstance(value, float) and float(value).is_integer()):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        return f"{value:,.{digits}f}"
    return str(value)


def generate_report(df, stats, corr):
    """Generate Chapter 2 using the same definitions and regime rules as Chapters 3–4."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()

    # =========================
    # THIẾT LẬP TRANG
    # =========================
    sec = doc.sections[0]
    sec.top_margin = Inches(1)
    sec.bottom_margin = Inches(1)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1)

    from docx.shared import RGBColor

    # =========================
    # ĐỊNH DẠNG TOÀN BỘ VĂN BẢN
    # =========================
    styles = doc.styles

    for style_name in ["Normal", "Body Text"]:
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(13)
        style.font.color.rgb = RGBColor(0, 0, 0)

        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_before = Pt(0)
        style.paragraph_format.space_after = Pt(6)

    # Định dạng tiêu đề: vẫn phân cấp nhưng chữ đen
    for style_name in ["Title", "Subtitle",
                       "Heading 1", "Heading 2", "Heading 3"]:
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.line_spacing = 1.5

    styles["Heading 1"].font.size = Pt(13)
    styles["Heading 1"].font.bold = True

    styles["Heading 2"].font.size = Pt(13)
    styles["Heading 2"].font.bold = True

    styles["Heading 3"].font.size = Pt(13)
    styles["Heading 3"].font.bold = True

    title = doc.add_heading("2. DỮ LIỆU VÀ PHƯƠNG PHÁP XỬ LÝ", 0)
    for run in title.runs:
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(0, 0, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT

    p = doc.add_paragraph(
    "Global Financial Conditions and Cryptocurrency Markets: "
    "Nonlinear Transmission of Monetary, Dollar and Risk Shocks "
    "to Bitcoin and Ethereum"
    )
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.runs[0].italic = True

    subtitle = doc.add_paragraph(
    "Phạm vi mẫu: 2018–2025 | Bộ dữ liệu chuẩn dùng chung cho phân tích kinh tế lượng và học máy"
    )
    subtitle.alignment = WD_ALIGN_PARAGRAPH.LEFT

    dates = pd.to_datetime(df["date"], errors="coerce") if "date" in df else pd.Series(dtype="datetime64[ns]")
    start_date = dates.min().strftime("%d/%m/%Y") if dates.notna().any() else "chưa xác định"
    end_date = dates.max().strftime("%d/%m/%Y") if dates.notna().any() else "chưa xác định"
    nrows, ncols = df.shape

    doc.add_heading("2.1. Thiết kế và phạm vi dữ liệu", level=1)
    doc.add_paragraph(
        f"Nghiên cứu sử dụng dữ liệu chuỗi thời gian theo ngày trong giai đoạn {start_date}–{end_date}. "
        f"Bộ dữ liệu chuẩn có {nrows:,} ngày lịch và {ncols} cột, bao gồm giá BTC, ETH; ba chỉ báo tài chính toàn cầu US2Y, DXY và VIX; "
        "các biến lợi suất/thay đổi cùng cờ quan sát và khoảng cách giữa các lần quan sát vĩ mô. Phạm vi này thống nhất với Chương 3 "
        "(mô hình VAR, phản ứng xung và Local Projections) và Chương 4 (dự báo ngoài mẫu độ lớn lợi suất BTC/ETH)."
    )
    doc.add_paragraph(
        "Đơn vị thời gian của dataset là ngày lịch liên tục, không phải chỉ các ngày thị trường tài chính truyền thống mở cửa. "
        "Vì vậy, số quan sát thực tế dùng trong từng mô hình có thể khác nhau tùy biến và quy tắc lọc mẫu; không được hiểu số ngày lịch là cỡ mẫu của mọi ước lượng."
    )

    doc.add_heading("2.2. Nguồn dữ liệu", level=1)
    add_table(doc, ["Biến", "Nguồn/mã", "Định nghĩa và lưu ý"], [
        ["BTC", "Yahoo Finance: BTC-USD", "Giá đóng cửa Bitcoin; thị trường giao dịch liên tục."],
        ["ETH", "Yahoo Finance: ETH-USD", "Giá đóng cửa Ethereum; thị trường giao dịch liên tục."],
        ["US2Y", "FRED: DGS2", "Lợi suất Kho bạc Mỹ kỳ hạn 2 năm, đơn vị %/năm; không có quan sát cho mọi ngày lịch."],
        ["DXY", "Yahoo Finance: DX-Y.NYB", "Proxy chỉ số USD theo mã được tải trong pipeline; không gọi là chuỗi chuẩn chính thức nếu chưa xác minh tương đương."],
        ["VIX", "Yahoo Finance: ^VIX", "Chỉ số biến động kỳ vọng thị trường chứng khoán Mỹ, đơn vị điểm chỉ số."],
    ], 8)
    doc.add_paragraph(
        "Nhật ký nguồn và thông tin truy xuất được lưu trong docs/data_source_log.xlsx. Để tái lập, cần giữ mã chuỗi, nguồn, khoảng thời gian tải, "
        "thời điểm tải và số quan sát hợp lệ; mọi thay đổi nguồn hoặc mã proxy phải được phản ánh đồng thời trong nhật ký và bản thảo."
    )

    doc.add_heading("2.3. Đồng bộ và làm sạch dữ liệu", level=1)
    doc.add_paragraph(
        "Dữ liệu thô được chuẩn hóa về ngày UTC, sắp xếp theo thời gian, kiểm tra ngày trùng và chuyển các cột số về dạng số. Dataset được reindex trên lịch ngày liên tục "
        "từ đầu năm 2018 đến hết năm 2025. Không forward-fill, backfill hoặc nội suy các mức vĩ mô trong dataset chuẩn; giá trị thiếu được giữ là NA và không được diễn giải là 0."
    )
    doc.add_paragraph(
        "Lợi suất BTC/ETH được tính trên chuỗi giá crypto theo ngày lịch trước khi lọc mẫu. Ngược lại, thay đổi US2Y, DXY và VIX chỉ được tính giữa hai lần quan sát hợp lệ liên tiếp của nguồn. "
        "Nếu hai lần quan sát cách nhau hơn một ngày, biến đổi tương ứng không phải biến động một ngày. Các biến *_observation_gap_days và *_observed được lưu để nhận diện khoảng trống quan sát."
    )

    doc.add_heading("2.4. Xây dựng biến và quy ước đo lường", level=1)
    add_table(doc, ["Biến", "Công thức/định nghĩa", "Đơn vị"], [
        ["BTC_log_return_pct", "100 × ln(BTC_t / BTC_(t−1))", "%/ngày"],
        ["ETH_log_return_pct", "100 × ln(ETH_t / ETH_(t−1))", "%/ngày"],
        ["US2Y_change_pp", "US2Y_t − US2Y_previous_observed", "Điểm phần trăm giữa hai lần quan sát"],
        ["DXY_log_return_pct", "100 × ln(DXY_t / DXY_previous_observed)", "% giữa hai lần quan sát"],
        ["VIX_change_points", "VIX_t − VIX_previous_observed", "Điểm VIX giữa hai lần quan sát"],
        ["*_observed", "1 nếu có mức dữ liệu nguồn tại ngày đó; ngược lại 0", "Nhị phân 0/1"],
        ["*_observation_gap_days", "Số ngày giữa lần quan sát hiện tại và lần quan sát hợp lệ trước đó", "Ngày"],
    ], 8)
    doc.add_paragraph(
        "Ký hiệu previous_observed là lần quan sát hợp lệ trước đó, không nhất thiết là ngày lịch liền kề. Trong Chương 3, các biến thay đổi vĩ mô được dùng để mô tả liên hệ có điều kiện "
        "trong VAR/LP; US2Y, DXY và VIX không được xem mặc nhiên là cú sốc ngoại sinh đã nhận diện. Trong Chương 4, biến mục tiêu là độ lớn lợi suất ngày kế tiếp, "
        "y_(t+1) = |r_(t+1)|, đơn vị điểm phần trăm; đây là proxy cho độ lớn biến động ngày, không phải phương sai thực hiện, VaR hay ES."
    )

    doc.add_heading("2.5. Kiểm tra chất lượng dữ liệu", level=1)
    quality_rows = []
    for col in df.columns:
        valid = int(df[col].notna().sum())
        missing = int(df[col].isna().sum())
        rate = missing / nrows * 100 if nrows else 0
        quality_rows.append([col, f"{valid:,}", f"{missing:,}", f"{rate:.2f}%"])
    add_table(doc, ["Biến", "Hợp lệ", "Thiếu", "Tỷ lệ thiếu"], quality_rows, 7)
    doc.add_paragraph(
        "Bảng được tính trực tiếp từ dataset chuẩn trong cùng lần chạy pipeline. Cờ observed bằng 0 chỉ ra ngày không có mức dữ liệu nguồn; giá trị thay đổi bị thiếu ở lần quan sát đầu tiên "
        "còn có thể xuất phát từ việc chưa có quan sát trước đó để tính sai phân. Hai trường hợp này cần được phân biệt khi chọn mẫu cho mô hình."
    )

    doc.add_heading("2.6. Thống kê mô tả và tương quan", level=1)
    core_stats = ["BTC", "ETH", "US2Y", "DXY", "VIX", "BTC_log_return_pct", "ETH_log_return_pct", "US2Y_change_pp", "DXY_log_return_pct", "VIX_change_points"]
    if stats is not None and not stats.empty:
        stats_view = stats.copy()
        first_col = stats_view.columns[0]
        stats_view[first_col] = stats_view[first_col].astype(str)

        if first_col == "Unnamed: 0":
            stats_view = stats_view.rename(
                columns={first_col: "Biến"}
            )
            first_col = "Biến"
        stats_view = stats_view[stats_view[first_col].isin(core_stats)]
        preferred = [c for c in [first_col, "count", "mean", "std", "min", "50%", "max", "missing_rate_pct"] if c in stats_view.columns]
        stats_view = stats_view[preferred]
        rows = [[str(v) if j == 0 else _fmt_num(v, 3) for j, v in enumerate(row)] for row in stats_view.itertuples(index=False, name=None)]
        doc.add_paragraph("Bảng thống kê mô tả được lấy từ outputs/tables/descriptive_stats.csv và trình bày với tối đa ba chữ số thập phân để dễ đọc. Số quan sát hợp lệ thay đổi theo biến do lịch công bố và giao dịch khác nhau.")
    if rows:
        add_table(doc, [str(c) for c in stats_view.columns], rows, 8)

        doc.add_paragraph(
                "Xét các biến giá, BTC và ETH có quy mô giá trung bình khác nhau "
                "và mức độ phân tán đáng kể trong giai đoạn nghiên cứu. Do giá "
                "tài sản có xu hướng biến động theo thời gian, các thống kê về "
                "mức giá được sử dụng chủ yếu để mô tả dữ liệu, không thay thế "
                "việc phân tích lợi suất."
            )

        doc.add_paragraph(
                "Đối với lợi suất log theo ngày, độ lệch chuẩn của ETH cao hơn "
                "BTC trong mẫu mô tả, cho thấy lợi suất ETH có mức phân tán lớn "
                "hơn trong giai đoạn được khảo sát. Các biến vĩ mô có số quan sát "
                "hợp lệ thấp hơn chuỗi giá crypto do lịch giao dịch và công bố "
                "không bao phủ toàn bộ ngày lịch. Vì vậy, việc so sánh các biến "
                "cần dựa trên mẫu thực tế được sử dụng trong từng phân tích."
            )
    else:
        doc.add_paragraph("Chưa có outputs/tables/descriptive_stats.csv. Chạy src/data/04_descriptive_stats.py trước khi phát hành bản thảo cuối.")

    if corr is not None and not corr.empty:
        corr_view = corr.copy()
        first_col = corr_view.columns[0]
        corr_view[first_col] = corr_view[first_col].astype(str)

        if first_col == "Unnamed: 0":
            corr_view = corr_view.rename(
                columns={first_col: "Biến"}
            )
            first_col = "Biến"
        corr_view = corr_view[corr_view[first_col].isin(["BTC_log_return_pct", "ETH_log_return_pct", "US2Y_change_pp", "DXY_log_return_pct", "VIX_change_points"])]
        corr_cols = [c for c in ["BTC_log_return_pct", "ETH_log_return_pct", "US2Y_change_pp", "DXY_log_return_pct", "VIX_change_points"] if c in corr_view.columns]
        corr_view = corr_view[[first_col] + corr_cols]
        rows = [[str(v) if j == 0 else _fmt_num(v, 3) for j, v in enumerate(row)] for row in corr_view.itertuples(index=False, name=None)]
        doc.add_paragraph("Ma trận tương quan dùng cùng nhóm biến lợi suất/thay đổi được phân tích ở Chương 3. Hệ số tương quan mô tả quan hệ tuyến tính không điều kiện; tương quan không xác lập quan hệ nhân quả, và cỡ mẫu có thể khác nhau giữa các cặp biến nếu dùng loại bỏ thiếu theo cặp.")
        if rows:
            add_table(doc, [str(c) for c in corr_view.columns], rows, 8)

            doc.add_paragraph(
                "Ma trận cho thấy lợi suất BTC và ETH có tương quan dương tương "
                "đối cao (0,825), phản ánh mức độ đồng biến trong mẫu. Thay đổi "
                "VIX có tương quan âm với lợi suất BTC (-0,326) và ETH (-0,344), "
                "trong khi lợi suất DXY có tương quan âm với lợi suất của hai "
                "tài sản ở mức thấp hơn. Thay đổi US2Y có tương quan tuyến tính "
                "gần bằng không với lợi suất BTC và ETH trong ma trận này."
            )

            doc.add_paragraph(
                "Đây là các tương quan tuyến tính không điều kiện, không phản "
                "ánh đầy đủ quan hệ động, độ trễ hoặc sự khác biệt giữa các "
                "trạng thái thị trường. Các kết quả này không đủ để kết luận "
                "về quan hệ nhân quả; những vấn đề đó được xem xét riêng trong "
                "các mô hình kinh tế lượng ở Chương 3."
            )
    else:
        doc.add_paragraph("Chưa có outputs/tables/correlation_matrix.csv; chạy src/data/04_descriptive_stats.py để tạo bảng.")

    doc.add_heading("2.7. Phân kỳ mẫu và trạng thái thị trường", level=1)
    doc.add_paragraph(
        "Để thống nhất với Chương 3, phân tích trước/sau năm 2020 chia mẫu thành giai đoạn 2018–2019 và 2020–2025. Khi diễn giải, cần kiểm định trực tiếp chênh lệch hệ số; "
        "việc một hệ số có ý nghĩa trong một giai đoạn nhưng không có ý nghĩa ở giai đoạn còn lại không tự nó chứng minh hai hệ số khác nhau. Các p-value từ nhiều phép thử được xem xét cùng điều chỉnh Benjamini–Hochberg (FDR 5%) như báo cáo ở Chương 3."
    )
    doc.add_paragraph(
        "Trạng thái thị trường cơ sở được xác định bằng VIX ở phiên quan sát vĩ mô trước đó: Calm nếu VIX trễ < 30 và Stress nếu VIX trễ ≥ 30. Dùng giá trị trễ giúp tránh phân loại trạng thái bằng chính giá trị VIX đương kỳ. "
        "Các ngưỡng 25 và 35 được sử dụng như kiểm tra độ nhạy, không thay thế tùy ý quy tắc cơ sở. Mẫu Stress nhỏ hơn đáng kể nên các ước lượng ở trạng thái này có thể kém chính xác."
    )
    doc.add_paragraph(
        "Đối với Chương 4, năm 2025 là tập kiểm tra ngoài mẫu gồm 365 ngày dự báo cho mỗi tài sản; giai đoạn đến hết năm 2024 được dùng để huấn luyện và lựa chọn tham số qua xác thực theo thời gian. "
        "Thông tin chuẩn hóa, điền khuyết và các lựa chọn mô hình không được ước lượng từ tập kiểm tra 2025."
    )
    doc.add_paragraph(
        "Trong bài toán học máy ở Chương 4, biến mục tiêu là độ lớn lợi suất "
        "log của ngày kế tiếp, được xác định bằng y_(t+1) = |r_(t+1)|. "
        "Biến mục tiêu được đo bằng điểm phần trăm mỗi ngày và không phải "
        "thước đo phương sai thực hiện trên một cửa sổ nhiều ngày, VaR hay ES."
    )

    doc.add_paragraph(
        "Nghiên cứu so sánh hai bộ đặc trưng. Bộ Crypto-only gồm 40 đặc trưng "
        "được xây dựng từ thông tin giá và lợi suất crypto, bao gồm các độ trễ "
        "của lợi suất, độ lớn lợi suất, thống kê cuộn với cửa sổ 3, 7, 14 và "
        "30 ngày, cùng các đặc trưng chu kỳ thứ trong tuần. Bộ Crypto+Macro "
        "bổ sung 12 đặc trưng vĩ mô, gồm mức quan sát gần nhất, thay đổi mới "
        "được ghi nhận, cờ quan sát mới và số ngày kể từ lần quan sát trước "
        "cho từng chuỗi US2Y, DXY và VIX."
    )

    doc.add_paragraph(
        "Các mô hình dự báo gồm chuẩn đối chiếu là trung bình độ lớn lợi suất "
        "trong 30 ngày gần nhất, Elastic Net và XGBoost. Hai bộ đặc trưng được "
        "đánh giá riêng cho BTC và ETH. Dữ liệu được chia theo thời gian: "
        "các năm 2022–2024 được sử dụng cho quy trình xác thực và lựa chọn "
        "mô hình, sau đó mô hình được huấn luyện bằng dữ liệu đến hết năm "
        "2024 và đánh giá trên 365 ngày của năm 2025. Dữ liệu nhãn năm 2025 "
        "không được sử dụng để huấn luyện hoặc lựa chọn mô hình."
    )

    doc.add_paragraph(
        "Các bước điền khuyết và chuẩn hóa được ước lượng từ dữ liệu huấn "
        "luyện rồi áp dụng cho dữ liệu đánh giá. Đối với đặc trưng vĩ mô, "
        "thông tin tại ngày t chỉ được sử dụng để dự báo từ ngày t+1 trở đi; "
        "cờ quan sát mới và biến thay đổi không được lặp lại giả tạo vào "
        "những ngày không có quan sát mới. Hiệu quả dự báo được đánh giá "
        "bằng MAE và RMSE. Chênh lệch MAE giữa hai bộ đặc trưng được phân "
        "tích thêm bằng bootstrap khối thời gian, với độ dài khối 7 ngày "
        "và 2.000 lần lặp."
    )

    doc.add_paragraph(
        "Đối với Elastic Net, mức độ quan trọng của đặc trưng được xem xét "
        "thông qua trị tuyệt đối của hệ số chuẩn hóa; đối với XGBoost, sử "
        "dụng thước đo gain. Hai thước đo này khác nhau về bản chất nên "
        "không được so sánh trực tiếp về độ lớn."
    )

    doc.add_heading("2.8. Khả năng tái lập và liên kết với các chương kết quả", level=1)
    doc.add_paragraph(
        "Bản thảo Chương 2 và data dictionary được tạo từ src/data/03_preprocess_data.py. Bảng thống kê mô tả và tương quan được tạo bởi src/data/04_descriptive_stats.py. "
        "Sau khi thay đổi dữ liệu hoặc quy tắc xử lý, cần chạy lại pipeline tiền xử lý, chạy thống kê mô tả, rồi kiểm tra các bảng và số liệu trong Chương 3–4 để bảo đảm mọi chương dùng cùng phiên bản dataset."
    )
    doc.add_paragraph(
        "Các bước tái lập từ thư mục gốc repository: python src/data/03_preprocess_data.py; sau đó python src/data/04_descriptive_stats.py. "
        "Bản thảo này mô tả định nghĩa và quy tắc dữ liệu; kết quả ước lượng, chẩn đoán mô hình và đánh giá dự báo được trình bày riêng trong paper/drafts/03_econometric_results.docx và paper/drafts/04_ml_results.docx."
    )

    doc.add_heading("2.9. Hạn chế dữ liệu", level=1)
    doc.add_paragraph(
        "Thứ nhất, ngày quan sát không đồng nghĩa với thời điểm thông tin thực sự sẵn có cho nhà đầu tư; timestamp công bố/khả dụng của dữ liệu vĩ mô chưa được xác minh đầy đủ. "
        "Thứ hai, DX-Y.NYB là proxy theo mã tải xuống và cần được gọi đúng như vậy. Thứ ba, các biến thay đổi vĩ mô có thể bao phủ nhiều ngày do lịch nghỉ và lịch giao dịch; cần kiểm soát observation gap khi diễn giải. "
        "Thứ tư, US2Y phản ánh lợi suất thị trường chứ không phải chuỗi bất ngờ chính sách Fed được nhận diện độc lập. Cuối cùng, các liên hệ thống kê và kết quả dự báo không tự thân chứng minh cơ chế nhân quả; đánh giá ngoài mẫu ML hiện chỉ bao phủ năm 2025."
    )

    # Chuẩn hóa định dạng lần cuối cho mọi đoạn và bảng
    from docx.shared import RGBColor

    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = 1.5

        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0, 0, 0)
    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith("Heading"):
            for run in paragraph.runs:
                run.bold = True
                run.font.name = "Times New Roman"
                run.font.color.rgb = RGBColor(0, 0, 0)

            if paragraph is title:
                run.font.size = Pt(15)
            else:
                run.font.size = Pt(13)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = 1.5

                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(13)
                        run.font.color.rgb = RGBColor(0, 0, 0)

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