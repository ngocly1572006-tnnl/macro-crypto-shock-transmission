
# ============================================================
# MACRO × CRYPTO INTELLIGENCE
# RESEARCH DASHBOARD — READER-FRIENDLY VERSION 5
#
# 8 trang | 5 câu hỏi nghiên cứu
# Không chạy lại VAR / LP / ML
# Đọc trực tiếp các kết quả CSV hiện có
#
# Run:
# python -m streamlit run dashboard/12_dashboard_app.py
# ============================================================

from pathlib import Path
import html
import re
import unicodedata

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 01. CẤU HÌNH
# ============================================================

st.set_page_config(
    page_title="Macro × Crypto Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "model_results"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

C = {
    "plum": "#553C5C",
    "deep": "#402D48",
    "coral": "#D77676",
    "teal": "#25887E",
    "violet": "#9270B5",
    "gold": "#C7954E",
    "ink": "#3D3045",
    "muted": "#76677C",
    "bg": "#F5EFF3",
    "white": "#FFFFFF",
}

RQ = {
    "RQ1": (
        "Các biến động tài chính toàn cầu liên hệ như thế nào "
        "với lợi suất Bitcoin và Ethereum?"
    ),
    "RQ2": (
        "Phản ứng của Bitcoin và Ethereum trước các biến động "
        "tài chính toàn cầu diễn biến như thế nào theo thời gian?"
    ),
    "RQ3": (
        "Mối quan hệ giữa điều kiện tài chính toàn cầu và "
        "BTC/ETH có thay đổi trước và sau năm 2020 không?"
    ),
    "RQ4": (
        "Mối quan hệ này có khác nhau giữa thị trường "
        "bình ổn (Calm) và căng thẳng (Stress) không?"
    ),
    "RQ5": (
        "Bổ sung dữ liệu vĩ mô có cải thiện dự báo độ lớn "
        "lợi suất ngày tiếp theo của BTC/ETH không?"
    ),
}

PAGES = {
    "🏠 Tổng quan nghiên cứu": "overview",
    "📉 RQ1 · Truyền dẫn": "rq1",
    "📈 RQ2 · Phản ứng động": "rq2",
    "🔄 RQ3 · Trước/sau 2020": "rq3",
    "🛡️ RQ4 · Calm/Stress": "rq4",
    "🧠 RQ5 · Dự báo ML": "rq5",
    "📚 Dữ liệu & cách đọc": "methods",
    "🎯 Kết luận & ứng dụng": "final_conclusion",
}

SHOCKS = {
    "VIX": "VIX · Mức độ bất ổn tài chính",
    "DXY": "DXY · Sức mạnh đồng USD",
    "US2Y": "US2Y · Lợi suất TPCP Mỹ 2 năm",
}

SHOCK_MEANING = {
    "VIX": (
        "VIX phản ánh mức độ bất ổn kỳ vọng trên thị trường "
        "cổ phiếu Mỹ. VIX tăng thường gắn với tâm lý lo ngại rủi ro."
    ),
    "DXY": (
        "DXY phản ánh sức mạnh của USD so với một rổ tiền tệ. "
        "DXY tăng nghĩa là USD mạnh lên."
    ),
    "US2Y": (
        "US2Y là lợi suất trái phiếu Chính phủ Mỹ kỳ hạn 2 năm, "
        "thường nhạy cảm với kỳ vọng về lãi suất."
    ),
}

ASSETS = {"BTC": "Bitcoin", "ETH": "Ethereum"}

FILES = {
    "lp": ("lp_results.csv", RESULTS),
    "lp_fdr": ("lp_fdr.csv", RESULTS),
    "irf": ("irf_results.csv", RESULTS),
    "subperiod": ("subperiod_results.csv", RESULTS),
    "rolling": ("rolling_sensitivity.csv", RESULTS),
    "rq3": ("subperiod_difference_fdr.csv", RESULTS),
    "regime": ("regime_results.csv", RESULTS),
    "rq4": ("regime_difference_fdr.csv", RESULTS),
    "regime_diag": ("regime_diagnostics.csv", RESULTS),
    "comparison": ("model_comparison.csv", RESULTS),
    "forecast": ("forecast_results.csv", RESULTS),
    "significance": ("forecast_significance.csv", RESULTS),
    "importance": ("feature_importance.csv", RESULTS),
    "correlation": ("correlation_matrix.csv", TABLES),
    "quality": ("preprocessing_quality_report.csv", TABLES),
    "descriptive": ("descriptive_stats.csv", TABLES),
}


# ============================================================
# 02. GIAO DIỆN
# ============================================================

CSS = """
<style>
:root { color-scheme:light; }

.stApp {
    background:#F5EFF3!important;
    color:#3D3045!important;
}

[data-testid="stHeader"] {
    background:#F5EFF3!important;
}

.block-container {
    max-width:1450px!important;
    padding-top:3.5rem!important;
    padding-bottom:4rem!important;
}

.stApp h1,.stApp h2,.stApp h3 {
    color:#3D3045!important;
    font-weight:900!important;
}

.stApp p,.stApp li {
    line-height:1.75;
}

[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#553C5C,#3E2D47)!important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color:#FFF5FB!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius:12px;
    padding:10px!important;
    margin:3px 0;
}

[data-testid="stSidebar"]
[role="radiogroup"] label:has(input:checked) {
    background:#C87582!important;
}

.brand {
    background:linear-gradient(135deg,#775681,#A76D87);
    border-radius:19px;
    padding:25px 20px;
    margin-bottom:24px;
    color:white;
}

.brand-title {
    color:#FFFFFF;
    font-size:26px;
    font-weight:950;
    line-height:1.35;
}

.brand-sub {
    color:#FFE3DC;
    font-size:12px;
    font-weight:800;
    letter-spacing:1px;
    margin-top:10px;
}

.side-card {
    background:#614B69;
    border:1px solid #856E8D;
    border-radius:14px;
    padding:19px;
    color:#FFF1F8;
    font-size:14px;
    line-height:2;
}

.side-card strong { color:#FFD4B8; }

.hero {
    background:linear-gradient(110deg,#503A57,#765477,#A76F86);
    border-radius:24px;
    padding:40px 43px;
    margin:16px 0 27px;
    box-shadow:0 12px 29px rgba(70,40,75,.13);
}

.hero-kicker {
    color:#FFD3B9;
    font-size:13px;
    font-weight:950;
    letter-spacing:1.7px;
}

.hero-title {
    color:#FFFFFF;
    font-size:clamp(35px,3.5vw,51px);
    font-weight:950;
    line-height:1.27;
    margin:12px 0;
}

.hero-title em {
    color:#FFD1AE;
    font-style:normal;
}

.hero-description {
    color:#FFF0F8;
    font-size:18px;
    font-weight:600;
    line-height:1.8;
    max-width:1050px;
}

.section {
    margin:36px 0 19px;
}

.section-kicker {
    color:#AD596E;
    font-size:12px;
    font-weight:950;
    letter-spacing:1.4px;
}

.section-title {
    color:#3D3045;
    font-size:29px;
    font-weight:950;
    margin:8px 0;
    line-height:1.4;
}

.section-desc {
    color:#76677C;
    font-size:16px;
    font-weight:600;
    line-height:1.8;
}

.question {
    background:#FFFFFF;
    border:1px solid #E7D8E5;
    border-left:6px solid #D77676;
    border-radius:17px;
    padding:24px 28px;
    margin:18px 0 25px;
}

.question-label {
    color:#B35C6B;
    font-size:13px;
    font-weight:950;
    letter-spacing:1px;
}

.question-text {
    color:#3D3045;
    font-size:21px;
    font-weight:900;
    line-height:1.65;
    margin-top:10px;
}

.kpi {
    background:#FFFFFF;
    border:1px solid #E6D8E4;
    border-top:6px solid #D77676;
    border-radius:17px;
    padding:23px;
    min-height:160px;
    margin-bottom:10px;
    box-shadow:0 5px 16px rgba(60,40,65,.04);
}

.kpi.teal { border-top-color:#25887E; }
.kpi.violet { border-top-color:#9270B5; }
.kpi.gold { border-top-color:#C7954E; }
.kpi.coral { border-top-color:#D77676; }

.kpi-label {
    color:#775E79;
    font-size:13px;
    font-weight:900;
    text-transform:uppercase;
}

.kpi-value {
    color:#503A57;
    font-size:clamp(27px,2.5vw,40px);
    font-weight:950;
    margin:13px 0 8px;
}

.kpi-detail {
    color:#776B7A;
    font-size:14px;
    font-weight:600;
}

.info-card {
    border-radius:17px;
    border-left:6px solid #9270B5;
    padding:23px 26px;
    margin:15px 0 22px;
    background:#EAE1F4;
}

.info-card.teal {
    background:#DFEFEA;
    border-left-color:#25887E;
}

.info-card.coral {
    background:#F9E4E2;
    border-left-color:#D77676;
}

.info-card.gold {
    background:#FAEEDB;
    border-left-color:#C7954E;
}

.info-card.white {
    background:#FFFFFF;
    border-left-color:#775681;
}

.info-label {
    color:#9B5470;
    font-size:12px;
    font-weight:950;
    letter-spacing:1px;
}

.info-title {
    color:#3D3045;
    font-size:21px;
    font-weight:950;
    margin:9px 0;
    line-height:1.5;
}

.info-body {
    color:#4D4253;
    font-size:16px;
    font-weight:600;
    line-height:1.85;
}

.guide {
    background:#FFFFFF;
    border:1px solid #E5D8E4;
    border-left:6px solid #9270B5;
    border-radius:17px;
    padding:23px 27px;
    margin:17px 0 23px;
}

.guide-label {
    color:#9561A4;
    font-size:13px;
    font-weight:950;
    letter-spacing:1px;
}

.guide-question {
    color:#3D3045;
    font-size:21px;
    font-weight:950;
    margin:10px 0 15px;
}

.guide-line {
    color:#514556;
    font-size:16px;
    line-height:1.85;
    margin-top:9px;
}

.guide-line b { color:#9860A4; }

.result {
    background:#FFFFFF;
    border:1px solid #E8DCE6;
    border-radius:20px;
    overflow:hidden;
    margin:19px 0 34px;
    box-shadow:0 7px 22px rgba(70,40,75,.06);
}

.result-header {
    background:linear-gradient(110deg,#553C5C,#805B7C);
    color:#FFFFFF;
    font-size:15px;
    font-weight:950;
    letter-spacing:1px;
    padding:19px 25px;
}

.result-inner { padding:25px 28px; }

.result-step {
    color:#A65D70;
    font-size:13px;
    font-weight:950;
    margin-bottom:9px;
}

.result-main {
    color:#3D3045;
    font-size:23px;
    font-weight:950;
    line-height:1.55;
    margin-bottom:24px;
}

.result-meaning {
    background:#E2F1EC;
    border-left:5px solid #25887E;
    border-radius:13px;
    padding:19px 22px;
    margin-bottom:15px;
}

.result-caution {
    background:#FFF0DD;
    border-left:5px solid #C7954E;
    border-radius:13px;
    padding:19px 22px;
}

.result-subtitle {
    font-size:13px;
    font-weight:950;
    margin-bottom:9px;
}

.result-meaning .result-subtitle { color:#176E65; }
.result-caution .result-subtitle { color:#966B31; }

.result-text {
    color:#443C49;
    font-size:16px;
    font-weight:600;
    line-height:1.85;
}

.answer {
    background:linear-gradient(110deg,#DDEEE8,#EEE5F4);
    border-left:7px solid #25887E;
    border-radius:18px;
    padding:26px 29px;
    margin:30px 0;
}

.answer-label {
    color:#227A70;
    font-size:13px;
    font-weight:950;
    letter-spacing:1px;
}

.answer-title {
    color:#3D3045;
    font-size:24px;
    font-weight:950;
    margin:12px 0;
    line-height:1.5;
}

.answer-body {
    color:#4A4251;
    font-size:17px;
    font-weight:600;
    line-height:1.85;
}

/* Input controls: luôn sáng, không phụ thuộc dark theme */

[data-testid="stSelectbox"] label p,
[data-testid="stMultiSelect"] label p {
    color:#503A57!important;
    font-size:16px!important;
    font-weight:900!important;
}

[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background:#FFFFFF!important;
    color:#503A57!important;
    border-radius:12px!important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    border:2px solid #C8AFCB!important;
    min-height:49px!important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * {
    color:#503A57!important;
    -webkit-text-fill-color:#503A57!important;
}

[data-baseweb="popover"],
[data-baseweb="popover"] *,
[data-baseweb="menu"],
[data-baseweb="menu"] *,
ul[role="listbox"],
li[role="option"] {
    background-color:#FFFFFF!important;
    color:#503A57!important;
    -webkit-text-fill-color:#503A57!important;
}

li[role="option"]:hover,
li[aria-selected="true"] {
    background-color:#F2E4EF!important;
}

[data-testid="stExpander"] {
    background:#FFFFFF!important;
    border:1px solid #E5D6E2!important;
    border-radius:14px!important;
}

[data-testid="stExpander"] summary {
    background:#F4EAF2!important;
}

[data-testid="stExpander"] summary p {
    color:#503A57!important;
    font-size:15px!important;
    font-weight:900!important;
}

/* V5 FIX: thống nhất TẤT CẢ điều khiển nhập/chọn ở chế độ sáng. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stTimeInput"] input {
    background-color:#FFFFFF!important;
    color:#503A57!important;
    -webkit-text-fill-color:#503A57!important;
    color-scheme:light!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stTimeInput"] input {
    border:2px solid #C8AFCB!important;
    border-radius:12px!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {
    fill:#553C5C!important;
    color:#553C5C!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder,
[data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder,
[data-testid="stTextInput"] input::placeholder {
    color:#88738B!important;
    -webkit-text-fill-color:#88738B!important;
}
/* Menu xổ xuống: hỗ trợ cả portal của BaseWeb và Streamlit phiên bản mới. */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] > div,
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] > div,
[role="listbox"] {
    background-color:#FFFFFF!important;
    color:#503A57!important;
    color-scheme:light!important;
}
[data-baseweb="menu"] [role="option"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"],
[role="listbox"] [role="option"] {
    background-color:#FFFFFF!important;
    color:#503A57!important;
    -webkit-text-fill-color:#503A57!important;
}
[data-baseweb="menu"] [role="option"]:hover,
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
[role="listbox"] [role="option"][aria-selected="true"] {
    background-color:#F2E4EF!important;
}
/* Sidebar: vòng tròn radio không còn bị đen. */
[data-testid="stSidebar"] [role="radiogroup"] [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] [role="radiogroup"] [data-baseweb="radio"] > div:first-child > div,
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stMarkdownContainer"] {
    color:#FFF5FB!important;
}
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] + div {
    background:#FFFFFF!important;
    border-color:#F1D6E5!important;
}
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"]:checked + div {
    background:#D77676!important;
    border-color:#FFFFFF!important;
}
/* Mọi nhãn bộ lọc trong vùng nội dung giữ màu tím gốc. */
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stSelectbox"] label p,
[data-testid="stMain"] [data-testid="stMultiSelect"] label p {
    color:#503A57!important;
}

/* Bảng màu */

.table-wrap {
    overflow:auto;
    max-height:460px;
    border:1px solid #E6D9E4;
    border-radius:14px;
}

.color-table {
    border-collapse:collapse;
    width:100%;
    min-width:700px;
    font-size:14px;
}

.color-table th {
    background:#5D4564;
    color:#FFFFFF;
    padding:14px;
    text-align:left;
    position:sticky;
    top:0;
    white-space:nowrap;
}

.color-table th:nth-child(3n+2) { background:#795A82; }
.color-table th:nth-child(3n+3) { background:#31877D; }

.color-table td {
    padding:12px 14px;
    background:#FFFFFF;
    color:#493D50;
    border-bottom:1px solid #EEE4EC;
    white-space:nowrap;
}

.color-table tr:nth-child(even) td {
    background:#F9F3F8;
}

.color-table tr:hover td {
    background:#FCECE8;
}

.cell-tag {
    display:inline-block;
    background:#EADCF1;
    color:#684C7A;
    border-radius:8px;
    padding:4px 9px;
    font-weight:850;
}

.cell-positive { color:#207F73; font-weight:850; }
.cell-negative { color:#C75F70; font-weight:850; }

.stButton > button {
    background:#553C5C!important;
    border:none!important;
    border-radius:12px!important;
    color:#FFFFFF!important;
    font-weight:850!important;
}

.stButton > button * { color:#FFFFFF!important; }

[data-testid="stCaptionContainer"] p {
    color:#756779!important;
    font-size:14px!important;
}

@media(max-width:900px) {
    .hero { padding:27px 24px; }
    .hero-title { font-size:35px; }
    .section-title { font-size:25px; }
    .block-container { padding-top:3rem!important; }
}
</style>
"""

st.html(CSS)


# ============================================================
# 03. ĐỌC VÀ CHUẨN HÓA DỮ LIỆU
# ============================================================

@st.cache_data(show_spinner=False)
def read_csv(path):
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


ALIASES = {
    "response": [
        "response", "asset", "coin", "target",
        "response_variable", "asset_name",
    ],
    "shock": [
        "shock", "impulse", "shock_variable",
        "impulse_variable",
    ],
    "horizon": ["horizon", "h", "step"],
    "estimate": [
        "estimate", "beta", "coefficient",
        "coef", "irf", "response_value",
    ],
    "ci_lower": [
        "ci_lower", "lower_ci", "ci_low",
        "lower", "ci95_lower", "ci_lower_95",
        "lower_95", "ci_low_95", "ci_lower_95pct",
    ],
    "ci_upper": [
        "ci_upper", "upper_ci", "ci_high",
        "upper", "ci95_upper", "ci_upper_95",
        "upper_95", "ci_high_95", "ci_upper_95pct",
    ],
    "p_value": ["p_value", "pvalue", "p"],
    "p_value_fdr": [
        "p_value_fdr", "q_value", "p_fdr",
        "bh_q_value", "fdr_p_value",
    ],
    "period": ["period", "subperiod", "sample_period"],
    "regime": ["regime", "market_regime", "state"],
    "model": ["model", "model_name"],
    "feature_set": [
        "feature_set", "features", "feature_group",
    ],
    "metric": ["metric", "metric_name"],
    "value": ["value", "score", "metric_value"],
    "date": ["date", "ds", "timestamp"],
    "actual": [
        "actual", "y_true", "realized", "y_actual",
    ],
    "predicted": [
        "predicted", "prediction", "y_pred", "forecast",
    ],
    "feature": ["feature", "feature_name"],
    "importance": [
        "importance", "gain", "importance_value",
    ],
}


def clean_col(value):
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(
        c for c in value if not unicodedata.combining(c)
    )
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower())
    return value.strip("_")


def normalize_columns(df):
    if df.empty:
        return df.copy()

    result = df.copy()
    result.columns = [clean_col(c) for c in result.columns]

    rename = {}
    used = set()

    for canonical, options in ALIASES.items():
        if canonical in result.columns:
            used.add(canonical)
            continue

        for option in options:
            candidate = clean_col(option)

            if candidate in result.columns and candidate not in used:
                rename[candidate] = canonical
                used.add(candidate)
                break

    return result.rename(columns=rename)


@st.cache_data(show_spinner=False)
def load_data():
    return {
        key: normalize_columns(read_csv(folder / filename))
        for key, (filename, folder) in FILES.items()
    }


DATA = load_data()


def num(value):
    try:
        value = float(value)
        return value if np.isfinite(value) else np.nan
    except (TypeError, ValueError):
        return np.nan


def fmt(value, digits=4):
    value = num(value)
    return "N/A" if np.isnan(value) else f"{value:,.{digits}f}"


def esc(value):
    return html.escape(str(value), quote=True)


def col(df, *names):
    for name in names:
        if name in df.columns:
            return name
    return None


def field(row, *names):
    if row is None:
        return np.nan

    for name in names:
        if name in row.index:
            return row[name]

    return np.nan


def filter_df(df, **conditions):
    if df.empty:
        return df.copy()

    result = df.copy()

    for column, value in conditions.items():
        if column not in result.columns or value is None:
            continue

        series = result[column].astype(str).str.strip().str.lower()
        target = str(value).strip().lower()

        if column == "horizon":
            numeric = pd.to_numeric(
                result[column], errors="coerce"
            )
            result = result[numeric == num(value)]
        else:
            result = result[series == target]

    return result.copy()


def first(df):
    return None if df.empty else df.iloc[0]


def numeric_frame(df, *columns):
    result = df.copy()

    for column in columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column], errors="coerce"
            )

    return result


def unique_values(df, column):
    if df.empty or column not in df.columns:
        return []

    return [
        x for x in df[column].dropna().unique().tolist()
        if str(x).strip()
    ]


def fdr_message(row):
    q = num(field(row, "p_value_fdr"))
    p = num(field(row, "p_value"))

    if np.isfinite(q):
        if q < 0.05:
            return (
                "Có ý nghĩa sau điều chỉnh FDR",
                f"q = {fmt(q)} < 0,05",
                True,
            )

        return (
            "Chưa đủ bằng chứng sau điều chỉnh FDR",
            f"q = {fmt(q)} ≥ 0,05",
            False,
        )

    if np.isfinite(p):
        return (
            "Có ý nghĩa theo kiểm định gốc"
            if p < 0.05
            else "Chưa có ý nghĩa theo kiểm định gốc",
            f"p = {fmt(p)}; chưa xác nhận FDR",
            None,
        )

    return (
        "Chưa có thông tin kiểm định",
        "Không tìm thấy p-value hoặc q-value",
        None,
    )


# ============================================================
# 04. CÁC THÀNH PHẦN GIAO DIỆN
# ============================================================

def hero(kicker, title, description):
    st.html(
        f"""
        <div class="hero">
            <div class="hero-kicker">{esc(kicker)}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-description">{esc(description)}</div>
        </div>
        """
    )


def section(title, description="", kicker="RESEARCH ANALYTICS"):
    st.html(
        f"""
        <div class="section">
            <div class="section-kicker">{esc(kicker)}</div>
            <div class="section-title">{esc(title)}</div>
            <div class="section-desc">{esc(description)}</div>
        </div>
        """
    )


def question(rq):
    st.html(
        f"""
        <div class="question">
            <div class="question-label">
                {esc(rq)} · CÂU HỎI NGHIÊN CỨU
            </div>
            <div class="question-text">{esc(RQ[rq])}</div>
        </div>
        """
    )


def kpi(label, value, detail="", tone="coral"):
    st.html(
        f"""
        <div class="kpi {esc(tone)}">
            <div class="kpi-label">{esc(label)}</div>
            <div class="kpi-value">{esc(value)}</div>
            <div class="kpi-detail">{esc(detail)}</div>
        </div>
        """
    )


def insight(label, title, body, tone="violet"):
    st.html(
        f"""
        <div class="info-card {esc(tone)}">
            <div class="info-label">{esc(label)}</div>
            <div class="info-title">{esc(title)}</div>
            <div class="info-body">{esc(body)}</div>
        </div>
        """
    )


def guide(question_text, how_to_read, focus):
    st.html(
        f"""
        <div class="guide">
            <div class="guide-label">TRƯỚC KHI XEM BIỂU ĐỒ</div>
            <div class="guide-question">{esc(question_text)}</div>
            <div class="guide-line">
                <b>Cách đọc:</b> {esc(how_to_read)}
            </div>
            <div class="guide-line">
                <b>Cần chú ý:</b> {esc(focus)}
            </div>
        </div>
        """
    )


def conclusion(finding, meaning, caution, heading="KẾT LUẬN TỪ BIỂU ĐỒ"):
    st.html(
        f"""
        <div class="result">
            <div class="result-header">
                {esc(heading)}
            </div>
            <div class="result-inner">
                <div class="result-step">
                    01 · PHÁT HIỆN CHÍNH
                </div>
                <div class="result-main">{esc(finding)}</div>

                <div class="result-meaning">
                    <div class="result-subtitle">
                        02 · ĐIỀU NÀY CÓ NGHĨA GÌ?
                    </div>
                    <div class="result-text">{esc(meaning)}</div>
                </div>

                <div class="result-caution">
                    <div class="result-subtitle">
                        03 · GIỚI HẠN CỦA KẾT LUẬN
                    </div>
                    <div class="result-text">{esc(caution)}</div>
                </div>
            </div>
        </div>
        """
    )


def answer(rq, title, body):
    st.html(
        f"""
        <div class="answer">
            <div class="answer-label">
                TRẢ LỜI CÂU HỎI {esc(rq)}
            </div>
            <div class="answer-title">{esc(title)}</div>
            <div class="answer-body">{esc(body)}</div>
        </div>
        """
    )


def show_table(df, title="Xem bảng số liệu chi tiết"):
    with st.expander("📋 " + title):
        if df.empty:
            st.info("Không tìm thấy dữ liệu.")
            return

        display = df.head(100).copy()

        headers = "".join(
            f"<th>{esc(name)}</th>" for name in display.columns
        )

        rows = []

        for _, record in display.iterrows():
            cells = []

            for name, value in record.items():
                if pd.isna(value):
                    content = "—"

                elif name in {
                    "response", "shock", "regime", "period",
                    "model", "feature_set", "metric",
                }:
                    content = (
                        f'<span class="cell-tag">{esc(value)}</span>'
                    )

                elif isinstance(value, (int, float, np.number)):
                    css = (
                        "cell-positive" if value > 0
                        else "cell-negative" if value < 0
                        else ""
                    )

                    content = (
                        f'<span class="{css}">{fmt(value)}</span>'
                    )

                else:
                    content = esc(value)

                cells.append(f"<td>{content}</td>")

            rows.append("<tr>" + "".join(cells) + "</tr>")

        st.html(
            '<div class="table-wrap">'
            '<table class="color-table">'
            f"<thead><tr>{headers}</tr></thead>"
            f'<tbody>{"".join(rows)}</tbody>'
            "</table></div>"
        )

        if len(df) > 100:
            st.caption(
                f"Đang hiển thị 100/{len(df):,} dòng đầu."
            )


def method_note(title, body):
    insight("PHƯƠNG PHÁP ĐANG SỬ DỤNG", title, body, "violet")


def selectors(prefix):
    c1, c2 = st.columns(2)

    with c1:
        asset = st.selectbox(
            "🪙 Chọn tài sản",
            ["BTC", "ETH"],
            format_func=lambda x: ASSETS[x],
            key=f"{prefix}_asset",
        )

    with c2:
        shock = st.selectbox(
            "🌐 Chọn biến tài chính",
            ["VIX", "DXY", "US2Y"],
            format_func=lambda x: SHOCKS[x],
            key=f"{prefix}_shock",
        )

    return asset, shock


# ============================================================
# 05. BIỂU ĐỒ
# ============================================================

def style_plot(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            color=C["ink"],
            size=16,
        ),
        margin=dict(l=65, r=50, t=75, b=80),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font=dict(color=C["ink"], size=14),
        ),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
            font=dict(color=C["ink"], size=15),
        ),
    )

    fig.update_xaxes(
        tickfont=dict(color=C["ink"], size=14),
        title_font=dict(color=C["ink"], size=16),
        showgrid=False,
        linecolor="#D4C5D2",
    )

    fig.update_yaxes(
        tickfont=dict(color=C["ink"], size=14),
        title_font=dict(color=C["ink"], size=16),
        gridcolor="#EEE5EC",
        zerolinecolor="#D4C5D2",
        nticks=6,
        tickformat="~g",
        separatethousands=True,
    )

    return fig


def plot(fig, key, height=430):
    fig = style_plot(fig, height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        theme=None,
        config={"displaylogo": False},
    )


def response_chart(
    df,
    key,
    color,
    x_title="Số ngày sau biến động",
):
    if df.empty or not {"horizon", "estimate"}.issubset(df.columns):
        st.info("Chưa có dữ liệu phù hợp để dựng biểu đồ.")
        return False

    part = numeric_frame(
        df, "horizon", "estimate", "ci_lower", "ci_upper"
    )

    part = part.dropna(
        subset=["horizon", "estimate"]
    ).sort_values("horizon")

    if part.empty:
        st.info("Dữ liệu phản ứng không hợp lệ.")
        return False

    fig = go.Figure()

    if {"ci_lower", "ci_upper"}.issubset(part.columns):
        ci = part.dropna(
            subset=["ci_lower", "ci_upper"]
        ).sort_values("horizon")

        if not ci.empty:
            xx = ci["horizon"].tolist()

            fig.add_trace(
                go.Scatter(
                    x=xx + xx[::-1],
                    y=(
                        ci["ci_upper"].tolist()
                        + ci["ci_lower"].tolist()[::-1]
                    ),
                    fill="toself",
                    fillcolor="rgba(146,112,181,.20)",
                    line=dict(color="rgba(0,0,0,0)"),
                    hoverinfo="skip",
                    name="Khoảng tin cậy",
                )
            )

    fig.add_trace(
        go.Scatter(
            x=part["horizon"],
            y=part["estimate"],
            mode="lines+markers",
            line=dict(color=color, width=3.5),
            marker=dict(size=7),
            name="Hệ số ước lượng",
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#A995A8",
    )

    fig.update_xaxes(title=x_title, tickmode="array", tickvals=part["horizon"].iloc[::max(1, len(part)//7)].tolist(), ticktext=[f"Ngày {int(v)}" for v in part["horizon"].iloc[::max(1, len(part)//7)]])
    fig.update_yaxes(title="Hệ số phản ứng")

    plot(fig, key)
    return True


def two_lines(
    datasets,
    key,
    x_title="Số ngày sau biến động",
    y_title="Hệ số ước lượng",
):
    fig = go.Figure()
    found = False

    for label, df, color in datasets:
        if df.empty or not {"horizon", "estimate"}.issubset(df.columns):
            continue

        part = numeric_frame(df, "horizon", "estimate")
        part = part.dropna(
            subset=["horizon", "estimate"]
        ).sort_values("horizon")

        if part.empty:
            continue

        found = True

        fig.add_trace(
            go.Scatter(
                x=part["horizon"],
                y=part["estimate"],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3.5),
                marker=dict(size=6),
            )
        )

    if not found:
        st.info("Không tìm thấy chuỗi phản ứng phù hợp.")
        return False

    fig.add_hline(
        y=0, line_dash="dash", line_color="#A995A8"
    )

    fig.update_xaxes(title=x_title, tickmode="array", tickvals=[0, 5, 10, 15, 20, 25, 30], ticktext=[f"Ngày {v}" for v in [0, 5, 10, 15, 20, 25, 30]])
    fig.update_yaxes(title=y_title)

    plot(fig, key)
    return True


# ============================================================
# 06. DIỄN GIẢI KẾT QUẢ
# ============================================================

def lp_interpret(asset, shock, row):
    beta = num(field(row, "estimate"))

    if not np.isfinite(beta):
        return (
            "Chưa có hệ số để kết luận.",
            "Không tìm thấy ước lượng cho lựa chọn hiện tại.",
            "Cần kiểm tra dữ liệu nguồn.",
        )

    if beta < 0:
        direction = "ngược chiều"
        explanation = (
            f"Khi {shock} tăng, lợi suất {asset} có xu hướng "
            "thấp hơn trong cùng ngày, sau khi xét các yếu tố "
            "kiểm soát của mô hình."
        )
    elif beta > 0:
        direction = "cùng chiều"
        explanation = (
            f"Khi {shock} tăng, lợi suất {asset} có xu hướng "
            "cao hơn trong cùng ngày, sau khi xét các yếu tố "
            "kiểm soát của mô hình."
        )
    else:
        direction = "không thể hiện chiều rõ ràng"
        explanation = (
            "Hệ số ước lượng bằng 0 nên không thể hiện "
            "chiều hướng liên hệ rõ ràng."
        )

    status, detail, strong = fdr_message(row)

    if strong is True:
        evidence = (
            "Kết quả vẫn đạt ngưỡng ý nghĩa thống kê "
            "sau điều chỉnh nhiều kiểm định."
        )
    elif strong is False:
        evidence = (
            "Dù hệ số có chiều hướng như trên, chưa đủ "
            "bằng chứng để khẳng định mối liên hệ "
            "sau điều chỉnh nhiều kiểm định."
        )
    else:
        evidence = (
            "Cần thận trọng vì chưa xác nhận được "
            "ý nghĩa thống kê sau điều chỉnh FDR."
        )

    return (
        f"{shock} và lợi suất {ASSETS[asset]} "
        f"có hệ số {direction} tại h = 0.",
        (
            f"Hệ số LP = {fmt(beta)}. {explanation} "
            f"{status} ({detail}). {evidence}"
        ),
        (
            "Đây là liên hệ thống kê có điều kiện, "
            "không phải bằng chứng nhân quả. "
            "Đơn vị của VIX, DXY và US2Y khác nhau "
            "nên không so sánh trực tiếp độ lớn hệ số."
        ),
    )


def dynamic_interpret(asset, shock, df, method="LP"):
    if df.empty or not {"horizon", "estimate"}.issubset(df.columns):
        return (
            "Chưa có dữ liệu phản ứng động.",
            "Không thể đánh giá diễn biến hệ số.",
            "Kiểm tra dữ liệu CSV.",
        )

    part = numeric_frame(
        df, "horizon", "estimate", "ci_lower", "ci_upper"
    )

    part = part.dropna(
        subset=["horizon", "estimate"]
    ).sort_values("horizon")

    if part.empty:
        return (
            "Không có dữ liệu hợp lệ.",
            "Chưa thể diễn giải biểu đồ.",
            "Kiểm tra các cột hệ số và chân trời.",
        )

    start = part.iloc[0]
    peak = part.loc[part["estimate"].abs().idxmax()]

    first_h = int(start["horizon"])
    peak_h = int(peak["horizon"])
    peak_beta = float(peak["estimate"])

    unit = "ngày lịch" if method == "LP" else "phiên vĩ mô"

    finding = (
        f"Phản ứng ước lượng của {asset} trước {shock} "
        "thay đổi theo chân trời thời gian."
    )

    meaning = (
        f"Ở h = {first_h}, hệ số là "
        f"{fmt(start['estimate'])}. "
        f"Hệ số có độ lớn tuyệt đối cao nhất tại "
        f"h = {peak_h} ({fmt(peak_beta)}), "
        f"tương ứng {peak_h} {unit} kể từ thời điểm gốc."
    )

    if {"ci_lower", "ci_upper"}.issubset(part.columns):
        ci = part.dropna(
            subset=["ci_lower", "ci_upper"]
        ).copy()

        if not ci.empty:
            excludes_zero = (
                (ci["ci_lower"] > 0)
                | (ci["ci_upper"] < 0)
            )

            count = int(excludes_zero.sum())

            meaning += (
                f" Trong {len(ci)} chân trời có khoảng tin cậy, "
                f"{count} chân trời có khoảng tin cậy "
                "không chứa giá trị 0."
            )

            caution = (
                "Khoảng tin cậy không chứa 0 gợi ý "
                "ý nghĩa theo kiểm định từng chân trời, "
                "nhưng không đồng nghĩa kết quả vẫn "
                "có ý nghĩa sau điều chỉnh FDR. "
                "Không chọn đỉnh của đường phản ứng "
                "làm bằng chứng thống kê."
            )
        else:
            caution = (
                "Chưa có khoảng tin cậy hợp lệ để "
                "đánh giá ý nghĩa thống kê của phản ứng."
            )
    else:
        caution = (
            "Biểu đồ chưa có khoảng tin cậy; "
            "không thể kết luận phản ứng khác 0 "
            "một cách đáng tin chỉ từ hình dạng đường."
        )

    if method == "LP":
        caution += (
            " LP ở đây mô tả lợi suất tại từng chân trời, "
            "không phải lợi suất cộng dồn."
        )
    else:
        caution += (
            " IRF VAR phụ thuộc vào thứ tự Cholesky "
            "và không có cùng đơn vị cú sốc với LP."
        )

    return finding, meaning, caution


def difference_interpret(
    row,
    label,
    names,
    description,
):
    if row is None:
        return (
            f"Chưa có kiểm định chênh lệch {label}.",
            "Không tìm thấy dòng kết quả phù hợp.",
            "Chưa thể đánh giá sự khác biệt.",
        )

    diff = num(field(row, *names))
    q = num(field(row, "p_value_fdr", "q_value"))
    p = num(field(row, "difference_p_value", "p_value"))

    finding = (
        f"Chênh lệch hệ số {label} = {fmt(diff)}."
        if np.isfinite(diff)
        else f"Chưa xác định được chênh lệch {label}."
    )

    if np.isfinite(q):
        if q < 0.05:
            meaning = (
                f"{description} q-value FDR = {fmt(q)}. "
                "Có bằng chứng về khác biệt hệ số "
                "sau điều chỉnh FDR 5%."
            )
        else:
            meaning = (
                f"{description} q-value FDR = {fmt(q)}. "
                "Chưa đủ bằng chứng thống kê để "
                "khẳng định hai nhóm khác nhau."
            )
    elif np.isfinite(p):
        meaning = (
            f"{description} p-value = {fmt(p)}. "
            "Đây là kiểm định chưa điều chỉnh FDR; "
            "không nên xem là kết luận cuối cùng."
        )
    else:
        meaning = (
            f"{description} Chưa tìm thấy kết quả "
            "kiểm định chênh lệch."
        )

    caution = (
        "Hai đường trên biểu đồ nhìn khác nhau "
        "không đồng nghĩa khác biệt có ý nghĩa thống kê. "
        "Không tìm thấy bằng chứng khác biệt cũng "
        "không chứng minh hai nhóm hoàn toàn giống nhau."
    )

    return finding, meaning, caution




# ============================================================
# 06B. PHÂN TÍCH CHUYÊN SÂU — BỔ SUNG CHO BẢN V5
# ============================================================

def deep_analysis(title, finding, mechanism, evidence, limitation):
    """Bốn tầng diễn giải: quan sát → cơ chế → thống kê → giới hạn."""
    parts = [
        ("01 · KẾT QUẢ QUAN SÁT", finding, "#F4EDF5", "#9270B5"),
        ("02 · CƠ CHẾ KINH TẾ", mechanism, "#E2F2EC", "#25887E"),
        ("03 · BẰNG CHỨNG THỐNG KÊ", evidence, "#EEE8F7", "#9270B5"),
        ("04 · GIỚI HẠN & HÀM Ý", limitation, "#FFF0DD", "#C7954E"),
    ]
    content = "".join(
        '<div style="background:'+bg+';border-left:5px solid '+edge+';'
        'border-radius:12px;padding:18px 22px;margin:12px 0">'
        '<div style="font-weight:900;color:#4D3956;font-size:14px">'+esc(label)+'</div>'
        '<div style="color:#443A4B;font-size:16px;line-height:1.9;white-space:pre-line">'
        +esc(body)+'</div></div>'
        for label, body, bg, edge in parts
    )
    st.html('<div style="background:white;border:1px solid #E6D8E4;'
            'border-radius:19px;padding:24px;margin:18px 0 30px">'
            '<div style="font-size:20px;font-weight:900;color:#503A57">'
            +esc(title)+'</div>'+content+'</div>')


def fdr_overview(df, key, asset=None):
    if df.empty or not {'shock', 'horizon', 'p_value_fdr'}.issubset(df.columns):
        return
    part = filter_df(df, response=asset) if asset else df.copy()
    part = numeric_frame(part, 'horizon', 'p_value_fdr')
    part = part.dropna(subset=['horizon', 'p_value_fdr'])
    if part.empty:
        return
    part['significant'] = (part['p_value_fdr'] < 0.05).astype(int)
    piv = part.pivot_table(index='shock', columns='horizon', values='significant', aggfunc='max')
    if piv.empty:
        return
    fig = go.Figure(go.Heatmap(
        x=piv.columns, y=piv.index, z=piv.values,
        zmin=0, zmax=1, colorscale=[[0,'#F0E5EF'],[0.49,'#F0E5EF'],[0.5,'#25887E'],[1,'#25887E']],
        text=np.where(piv.values==1,'✓','—'), texttemplate='%{text}',
        showscale=False,
    ))
    fig.update_xaxes(title='Số ngày sau biến động')
    plot(fig, key, 310)


def rq3_year_comparison(sub, difference, key, days):
    """One selected horizon; plot separate estimates and their OWN 95% CIs."""
    test = first(filter_df(difference, horizon=days))
    fig = go.Figure()
    entries = [("2018–2019", "pre_2020", "pre_beta", C["violet"]),
               ("2020–2025", "post_2020", "post_beta", C["coral"])]
    if test is None:
        st.info("Không có kết quả kiểm định chênh lệch ở ngày đã chọn.")
        return
    for years, period, beta_field, color in entries:
        beta = num(field(test, beta_field))
        if not np.isfinite(beta):
            continue
        fig.add_trace(go.Scatter(x=[years], y=[beta], mode="markers",
            marker=dict(size=19, color=color, symbol="diamond"),
            name=years,
            hovertemplate=f"{years}<br>Hệ số từ mô hình tương tác: %{{y:.4f}}<extra></extra>"))
    if not fig.data:
        st.info("Không có hệ số cho lựa chọn này trong subperiod_results.csv.")
        return
    fig.add_hline(y=0, line_dash="dash", line_color="#A995A8")
    fig.update_xaxes(title="Giai đoạn nghiên cứu", type="category",
        categoryorder="array", categoryarray=["2018–2019", "2020–2025"])
    fig.update_yaxes(title="Hệ số trong mô hình tương tác Pre/Post")
    plot(fig, key, 410)
    st.caption("Hai điểm và ba KPI cùng lấy từ một dòng subperiod_difference_fdr.csv "
               "tại ngày đã chọn (mô hình tương tác). Không vẽ khoảng tin cậy "
               "riêng vì CSV này chỉ có sai số chuẩn của chênh lệch. "
               "Khoảng tin cậy của hồi quy riêng từng giai đoạn có trong bảng phía dưới.")


def rolling_year_chart(df, asset, shock, key):
    """Rolling 252-session estimates plotted on actual calendar dates."""
    part = filter_df(df, asset=asset, shock=shock).copy()
    if part.empty or "date" not in part or "rolling_beta" not in part:
        st.info("Chưa có dữ liệu rolling_sensitivity.csv cho lựa chọn này.")
        return
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part["rolling_beta"] = pd.to_numeric(part["rolling_beta"], errors="coerce")
    part = part.dropna(subset=["date", "rolling_beta"]).sort_values("date")
    if part.empty:
        st.info("Không có ngày hợp lệ để vẽ hệ số rolling.")
        return
    fig = go.Figure(go.Scatter(x=part["date"], y=part["rolling_beta"],
        mode="lines", name=f"{shock} → {asset}",
        line=dict(color=C["violet"], width=2.5),
        hovertemplate="Ngày %{x|%d/%m/%Y}<br>Hệ số rolling %{y:.4f}<extra></extra>"))
    fig.add_hline(y=0, line_dash="dash", line_color="#A995A8")
    fig.add_vline(x="2020-01-01", line_dash="dot", line_color=C["coral"])
    fig.update_xaxes(title="Năm quan sát", tickformat="%Y", dtick="M12")
    fig.update_yaxes(title="Hệ số hồi quy cửa sổ 252 phiên")
    plot(fig, key, 440)
    st.caption("Mỗi điểm là hệ số ước lượng từ cửa sổ 252 phiên gần nhất, "
               "không phải hệ số riêng của một năm. Đường dọc đánh dấu 2020; "
               "biểu đồ mô tả diễn biến, không thay thế kiểm định RQ3.")


def original_figure(filename, caption):
    """Use the original research output, not a reconstructed plot."""
    path = FIGURES / filename
    if path.is_file():
        st.image(str(path), use_container_width=True)
        st.caption(caption)
    else:
        st.info(f"Chưa tìm thấy outputs/figures/{filename}. "
                "Đặt nguyên thư mục figures từ ZIP vào outputs/figures của dự án.")

def paired_difference_chart(df, key, label):
    """Đường chênh lệch theo horizon; q-value được giữ nguyên từ CSV."""
    if df.empty or 'horizon' not in df.columns:
        st.info('Chưa có dữ liệu chênh lệch theo chân trời.')
        return
    part = df.copy()
    for candidate in ('difference_post_minus_pre', 'difference_stress_minus_calm'):
        if 'difference' not in part.columns and candidate in part.columns:
            part['difference'] = part[candidate]
    if 'difference' not in part.columns:
        st.info('CSV chưa có cột chênh lệch hệ số.')
        return
    part = numeric_frame(part, 'horizon', 'difference', 'p_value_fdr',
                         'difference_ci_lower', 'difference_ci_upper')
    part = part.dropna(subset=['horizon', 'difference']).sort_values('horizon')
    if part.empty:
        st.info('Không có hệ số chênh lệch hợp lệ.')
        return
    q = (pd.to_numeric(part['p_value_fdr'], errors='coerce')
         if 'p_value_fdr' in part else pd.Series(np.nan, index=part.index))
    significant = q.notna() & q.lt(.05)
    fig = go.Figure()
    if {'difference_ci_lower', 'difference_ci_upper'}.issubset(part.columns):
        ci = part.dropna(subset=['difference_ci_lower', 'difference_ci_upper'])
        if len(ci) >= 2:
            xx = ci['horizon'].tolist()
            fig.add_trace(go.Scatter(
                x=xx + xx[::-1],
                y=ci['difference_ci_upper'].tolist() + ci['difference_ci_lower'].tolist()[::-1],
                fill='toself', fillcolor='rgba(146,112,181,.16)',
                line=dict(color='rgba(0,0,0,0)'),
                name='Khoảng tin cậy', hoverinfo='skip'))
    fig.add_trace(go.Scatter(
        x=part['horizon'], y=part['difference'], mode='lines+markers',
        name='Chênh lệch hệ số', line=dict(color=C['violet'], width=3),
        marker=dict(size=7, color=[C['teal'] if x else C['coral'] for x in significant]),
        customdata=np.column_stack([q.to_numpy()]),
        hovertemplate='Sau %{x} ngày<br>Chênh lệch=%{y:+.6f}'
                      '<br>q-value FDR=%{customdata[0]:.4f}<extra></extra>',
    ))
    fig.add_hline(y=0, line_dash='dash', line_color='#A995A8')
    fig.update_xaxes(title='Số ngày sau biến động vĩ mô', dtick=5)
    fig.update_yaxes(title=label)
    plot(fig, key, 410)
    st.caption('Điểm xanh: q-value FDR < 0,05; điểm coral: chưa đạt FDR hoặc thiếu q-value. '
               'Đường thể hiện chênh lệch ước lượng; không thể kết luận chỉ từ khoảng cách với 0.')


def feature_increment_chart(df, asset, metric, key):
    if df.empty or not {'model','feature_set','value'}.issubset(df.columns): return
    part=filter_df(df,response=asset,metric=metric)
    if part.empty and 'asset' in df: part=filter_df(df,asset=asset,metric=metric)
    if part.empty:return
    part=numeric_frame(part,'value')
    piv=part.pivot_table(index='model',columns='feature_set',values='value',aggfunc='mean')
    if not {'crypto_only','crypto_macro'}.issubset(piv.columns): return
    delta=(piv['crypto_only']-piv['crypto_macro']).dropna().sort_values()
    if delta.empty:return
    fig=go.Figure(go.Bar(x=delta.values,y=delta.index,orientation='h',
        marker_color=[C['teal'] if x>0 else C['coral'] for x in delta.values],
        text=[f'{x:+.4f}' for x in delta.values],textposition='outside'))
    fig.add_vline(x=0,line_dash='dash',line_color='#A995A8')
    fig.update_xaxes(title=f'Giảm {metric} khi thêm Macro (dương = cải thiện)')
    plot(fig,key,390)


def deep_mechanism(shock):
    return {
        'VIX': 'VIX tăng thường phản ánh mức bất ổn kỳ vọng cao hơn. Khi các nhà đầu tư giảm đòn bẩy và ưu tiên thanh khoản, nhu cầu nắm giữ crypto có thể giảm. Nhưng VIX cũng phản ứng với cùng một tin tức mà crypto phản ứng, nên không thể mặc định một chiều nhân quả.',
        'DXY': 'DXY mạnh có thể đi cùng điều kiện USD thắt chặt và khẩu vị rủi ro suy yếu. Giá crypto định danh USD còn có thể phản ánh thay đổi sức mua và dòng vốn xuyên biên giới. Cơ chế này chỉ là giả thuyết giải thích, không được nhận diện độc lập.',
        'US2Y': 'US2Y phản ánh kỳ vọng chính sách tiền tệ và triển vọng kinh tế. Tăng lợi suất có thể làm chi phí cơ hội của tài sản không sinh lãi tăng, nhưng đồng thời có thể phản ánh tin tức tăng trưởng, nên dấu hệ số có thể biến đổi.',
    }.get(shock,'Mối liên hệ có thể chịu ảnh hưởng đồng thời từ tâm lý thị trường, thanh khoản và tin tức vĩ mô.')



# ============================================================
# 06C. BỐI CẢNH, HÀM Ý VÀ KIỂM ĐỊNH ĐỘ TIN CẬY
# Bổ sung trên V5; giữ nguyên CSS và các biểu đồ hiện có.
# ============================================================

def research_story(title, context, motivation, application, caution):
    deep_analysis(
        title,
        context,
        motivation,
        application,
        caution,
    )


def fdr_count_summary(df, title, asset=None):
    """Đếm từ CSV thực tế, không coi NA là không có ý nghĩa."""
    if df.empty or 'p_value_fdr' not in df.columns:
        st.info('Chưa có q-value FDR để tổng hợp bằng chứng.')
        return
    part = filter_df(df, response=asset) if asset else df.copy()
    q = pd.to_numeric(part['p_value_fdr'], errors='coerce').dropna()
    if q.empty:
        st.info('Không có q-value hợp lệ cho lựa chọn này.')
        return
    passed = int((q < .05).sum())
    a, b = st.columns(2)
    with a:
        kpi('Kiểm định đạt FDR 5%', f'{passed}/{len(q)}', title, 'teal')
    with b:
        kpi('Kiểm định chưa đạt FDR', str(len(q)-passed),
            'Không đồng nghĩa hệ số bằng 0', 'gold')


def forecast_bootstrap_chart(df, asset):
    """So sánh ứng viên và tham chiếu theo đúng từng dòng bootstrap CSV."""
    if df.empty:
        st.info('Chưa có dữ liệu bootstrap.')
        return
    part = filter_df(df, asset=asset) if 'asset' in df else filter_df(df, response=asset)
    required = {'mae_reduction', 'ci_lower', 'ci_upper'}
    if part.empty or not required.issubset(part.columns):
        st.info('Thiếu cột bootstrap cần thiết.')
        return
    part = numeric_frame(part, *required).dropna(subset=list(required)).copy()
    if part.empty:
        return
    labels = []
    for _, row in part.iterrows():
        reference = f"{row.get('reference_model', 'N/A')} · {row.get('reference_feature_set', 'N/A')}"
        candidate = f"{row.get('candidate_model', 'N/A')} · {row.get('candidate_feature_set', 'N/A')}"
        labels.append(f'{candidate}  so với  {reference}')
    x = part['mae_reduction'].to_numpy(dtype=float)
    lo = part['ci_lower'].to_numpy(dtype=float)
    hi = part['ci_upper'].to_numpy(dtype=float)
    valid = (lo <= x) & (x <= hi)
    if not valid.all():
        st.warning('Có khoảng tin cậy bootstrap không bao chứa ước lượng; kiểm tra CSV.')
    fig = go.Figure()
    for i, (estimate, lower, upper, label) in enumerate(zip(x, lo, hi, labels)):
        if not valid[i]:
            continue
        color = C['teal'] if lower > 0 else C['coral'] if upper < 0 else C['violet']
        fig.add_trace(go.Scatter(
            x=[estimate], y=[label], mode='markers', showlegend=False,
            marker=dict(size=13, color=color),
            error_x=dict(type='data', symmetric=False,
                         array=[upper-estimate], arrayminus=[estimate-lower],
                         thickness=2, width=7),
            hovertemplate=f'Mức giảm MAE: {estimate:.4f}<br>CI 95%: [{lower:.4f}; {upper:.4f}]<extra></extra>',
        ))
    fig.add_vline(x=0, line_dash='dash', line_color='#A995A8')
    fig.update_xaxes(title='Giảm MAE so với mô hình tham chiếu (dương = tốt hơn)')
    plot(fig, 'rq5_bootstrap_ci', max(360, 95*len(part)+170))
    st.caption('Mỗi dòng ghi rõ mô hình ứng viên so với mô hình tham chiếu. '
               'Khoảng tin cậy cắt 0: chưa xác nhận chênh lệch ở mức 95%.')


def regime_difference_safe(df, key):
    """RQ4 xuất difference_stress_minus_calm thay vì difference."""
    if df.empty:
        return
    part = df.copy()
    if 'difference' not in part and 'difference_stress_minus_calm' in part:
        part['difference'] = part['difference_stress_minus_calm']
    paired_difference_chart(part, key, 'Stress − Calm')


def significance_by_horizon(df, title):
    if df.empty or not {'horizon', 'p_value_fdr'}.issubset(df.columns):
        return
    part = numeric_frame(df, 'horizon', 'p_value_fdr')
    part = part.dropna(subset=['horizon', 'p_value_fdr'])
    if part.empty:
        return
    by_h = part.groupby('horizon', as_index=False).agg(
        tests=('p_value_fdr', 'size'),
        passes=('p_value_fdr', lambda x: int((x < .05).sum()))
    )
    fig = go.Figure(go.Bar(x=by_h['horizon'], y=by_h['passes'],
                           marker_color=C['teal'], name='Đạt FDR'))
    fig.update_xaxes(title='Số ngày sau biến động')
    fig.update_yaxes(title='Số kiểm định đạt FDR 5%', dtick=1)
    plot(fig, 'horizon_significance_' + title, 340)


# ============================================================
# 07. SIDEBAR
# ============================================================

with st.sidebar:
    st.html(
        """
        <div class="brand">
            <div class="brand-title">
                Crypto Insights
            </div>
            <div class="brand-sub">
                MACRO × CRYPTO RESEARCH DASHBOARD
            </div>
        </div>
        """
    )

    selected = st.radio(
        "Điều hướng",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    st.html(
        """
        <div class="side-card">
            <strong>THÔNG TIN NGHIÊN CỨU</strong><br>
            Giai đoạn: 2018–2025<br>
            Tài sản: BTC · ETH<br>
            Biến vĩ mô: VIX · DXY · US2Y<br>
            Kinh tế lượng: VAR · LP<br>
            Dự báo: Elastic Net · XGBoost<br>
            Kiểm tra ngoài mẫu: 2025
        </div>
        """
    )

    if st.button(
        "↻ Làm mới dữ liệu",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

PAGE = PAGES[selected]


# ============================================================
# 08. TỔNG QUAN
# ============================================================

if PAGE == "overview":

    hero(
        "GLOBAL FINANCIAL RESEARCH · 2018–2025",
        "Macro <em>× Crypto</em> Intelligence",
        "Nghiên cứu mối liên hệ giữa điều kiện tài chính "
        "toàn cầu với Bitcoin và Ethereum, đồng thời kiểm tra "
        "liệu dữ liệu vĩ mô có thực sự giúp dự báo tốt hơn.",
    )

    cols = st.columns(4)

    with cols[0]:
        kpi(
            "Ngày nghiên cứu", "2.922",
            "Ngày lịch · 2018–2025", "coral",
        )

    with cols[1]:
        kpi(
            "Câu hỏi nghiên cứu", "05",
            "RQ1 đến RQ5", "teal",
        )

    with cols[2]:
        kpi(
            "Biến vĩ mô", "03",
            "VIX · DXY · US2Y", "violet",
        )

    with cols[3]:
        kpi(
            "Dự báo ngoài mẫu", "2025",
            "365 ngày", "gold",
        )

    section("Diễn biến giá BTC và ETH theo năm", "Biểu đồ gốc từ pipeline nghiên cứu, chuẩn hóa giá tại thời điểm đầu = 100.")
    original_figure("crypto_price_trends.png", "Trục ngang là năm thực tế 2018–2025; chỉ số giá chuẩn hóa, không phải lợi suất ngày.")

    section('Bối cảnh thị trường 2018–2025',
            'Từ thị trường tài sản số tương đối tách biệt đến câu hỏi về mức độ gắn kết với tài chính toàn cầu.',
            'WHY THIS RESEARCH MATTERS')
    research_story(
        'Tại sao nghiên cứu mối liên hệ Macro × Crypto?',
        'Giai đoạn 2018–2025 bao trùm nhiều trạng thái thị trường: giai đoạn trước đại dịch, cú sốc COVID-19, môi trường thanh khoản và lãi suất thay đổi mạnh, rồi những năm crypto ngày càng được quan tâm như một lớp tài sản đầu tư. Đây là bối cảnh để kiểm tra xem lợi suất BTC/ETH có đồng biến hoặc nghịch biến với điều kiện tài chính toàn cầu hay không.',
        'VIX đại diện cho mức độ bất ổn và khẩu vị rủi ro; DXY đại diện cho sức mạnh đồng USD; US2Y phản ánh kỳ vọng lãi suất ngắn hạn của Mỹ. Ba biến tương ứng với ba kênh có thể ảnh hưởng đến quyết định phân bổ vốn: rủi ro, đồng tiền định giá và chi phí cơ hội. Các kênh là giả thuyết kinh tế, không mặc nhiên là cú sốc ngoại sinh.',
        'Năm RQ được sắp xếp theo logic: (1) có liên hệ cùng ngày không, (2) diễn biến động ra sao, (3) có khác trước/sau 2020 không, (4) có phụ thuộc Calm/Stress không, và (5) thông tin vĩ mô có tăng khả năng dự báo ngoài mẫu không. Điều này giúp tách giá trị giải thích khỏi giá trị dự báo.',
        'Các kết quả là bằng chứng thống kê từ dữ liệu quan sát; không được đọc như tác động nhân quả đã nhận diện hoặc quy tắc giao dịch chắc chắn.')

    section(
        "Nghiên cứu này đang trả lời điều gì?",
        "Năm câu hỏi đi từ mô tả mối liên hệ "
        "đến kiểm tra khả năng dự báo.",
        "RESEARCH ROADMAP",
    )

    for rq in RQ:
        question(rq)

    section(
        "Đọc nhanh kết quả nghiên cứu",
        "Năm phát hiện chính trước khi đi vào biểu đồ.",
        "EXECUTIVE FINDINGS",
    )

    left, right = st.columns(2)

    with left:
        insight(
            "RQ1 · TRUYỀN DẪN",
            "VIX và DXY có liên hệ âm cùng ngày.",
            "Ở chân trời h = 0, hệ số LP của VIX và DXY "
            "với lợi suất BTC/ETH mang dấu âm. "
            "Điều này gợi ý lợi suất crypto thường thấp hơn "
            "khi bất ổn tài chính hoặc sức mạnh USD gia tăng.",
            "teal",
        )

        insight(
            "RQ3 · TRƯỚC/SAU 2020",
            "Chưa xác nhận thay đổi có hệ thống.",
            "Không có kiểm định chênh lệch nào "
            "còn ý nghĩa sau BH-FDR 5%. "
            "Không thể kết luận chắc chắn cơ chế truyền dẫn "
            "đã thay đổi sau năm 2020.",
            "violet",
        )

        insight(
            "RQ5 · DỰ BÁO",
            "Dữ liệu vĩ mô chưa tạo lợi ích ổn định.",
            "Việc thêm VIX, DXY và US2Y không cải thiện "
            "sai số dự báo một cách nhất quán "
            "trên tập ngoài mẫu năm 2025.",
            "gold",
        )

    with right:
        insight(
            "RQ2 · PHẢN ỨNG ĐỘNG",
            "Phản ứng thay đổi theo thời gian.",
            "Đường LP và IRF cho thấy hệ số có thể "
            "thay đổi dấu và độ lớn ở từng chân trời. "
            "Cần đọc khoảng tin cậy và kiểm định "
            "trước khi kết luận phản ứng kéo dài.",
            "violet",
        )

        insight(
            "RQ4 · CALM/STRESS",
            "Chưa xác nhận khác biệt giữa hai trạng thái.",
            "Các kiểm định chênh lệch không còn "
            "ý nghĩa sau FDR. Mẫu Stress cũng nhỏ "
            "hơn nhiều so với Calm, làm giảm độ chính xác.",
            "coral",
        )

    section(
        "BTC, ETH và các biến vĩ mô liên hệ ra sao?",
        "Ma trận tương quan là bước khám phá ban đầu.",
        "DESCRIPTIVE ANALYSIS",
    )

    guide(
        "Các biến có thường tăng giảm cùng nhau không?",
        "Hệ số tương quan gần +1 nghĩa là cùng chiều mạnh; "
        "gần −1 nghĩa là ngược chiều mạnh; gần 0 nghĩa là "
        "liên hệ tuyến tính yếu.",
        "Nhìn vào cặp BTC–ETH và các cặp BTC/ETH với VIX.",
    )

    correlation = DATA["correlation"]

    if not correlation.empty:
        try:
            matrix = correlation.copy()

            if (
                len(matrix.columns) > 1
                and matrix.columns[0] not in matrix.columns[1:]
            ):
                matrix = matrix.set_index(matrix.columns[0])

            matrix = matrix.apply(
                pd.to_numeric, errors="coerce"
            )

            fig = go.Figure(
                go.Heatmap(
                    z=matrix.values,
                    x=matrix.columns.tolist(),
                    y=matrix.index.tolist(),
                    zmin=-1,
                    zmax=1,
                    colorscale=[
                        [0, C["coral"]],
                        [0.5, "#FFF8F5"],
                        [1, C["teal"]],
                    ],
                    text=np.round(matrix.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(
                        size=13, color=C["ink"]
                    ),
                    colorbar=dict(title="r"),
                )
            )

            plot(fig, "overview_correlation", 490)

            def corr(a, b):
                try:
                    return float(matrix.loc[a, b])
                except Exception:
                    return np.nan

            btc_eth = corr(
                "BTC_log_return_pct",
                "ETH_log_return_pct",
            )
            btc_vix = corr(
                "BTC_log_return_pct",
                "VIX_change_points",
            )
            eth_vix = corr(
                "ETH_log_return_pct",
                "VIX_change_points",
            )

            if all(
                np.isfinite(x)
                for x in [btc_eth, btc_vix, eth_vix]
            ):
                conclusion(
                    "BTC và ETH có tương quan dương mạnh; "
                    "VIX có tương quan âm với lợi suất crypto.",
                    (
                        f"Tương quan BTC–ETH = {fmt(btc_eth, 2)}. "
                        f"BTC–VIX = {fmt(btc_vix, 2)} và "
                        f"ETH–VIX = {fmt(eth_vix, 2)}. "
                        "Nói đơn giản, BTC và ETH thường "
                        "biến động cùng chiều, còn khi VIX "
                        "tăng thì lợi suất crypto có xu hướng thấp hơn."
                    ),
                    (
                        "Tương quan không chứng minh quan hệ nhân quả. "
                        "Các phần RQ1 và RQ2 sử dụng mô hình "
                        "để kiểm tra sâu hơn."
                    ),
                )
            else:
                conclusion(
                    "Ma trận cho thấy các mối liên hệ giữa biến.",
                    "Màu xanh ngọc biểu thị tương quan dương; "
                    "màu coral biểu thị tương quan âm.",
                    "Không đọc được đầy đủ các cặp tương quan "
                    "theo tên cột hiện tại. Hãy kiểm tra bảng gốc.",
                )

        except Exception as exc:
            st.warning(
                f"Không dựng được ma trận tương quan: {exc}"
            )
    else:
        st.info("Chưa có correlation_matrix.csv.")

    section("Ma trận tương quan từ kết quả nghiên cứu", "Mối liên hệ tuyến tính mô tả, không phải bằng chứng nhân quả.")
    original_figure("correlation_heatmap.png", "Hệ số Pearson từ dữ liệu biến đổi trong mẫu; đọc cùng RQ1.")

    show_table(correlation, "Dữ liệu tương quan")

    answer(
        "TỔNG QUAN",
        "Thị trường crypto có liên hệ với điều kiện tài chính, "
        "nhưng điều đó không có nghĩa dữ liệu vĩ mô "
        "luôn giúp dự báo tốt hơn.",
        "Đây là thông điệp xuyên suốt nghiên cứu. "
        "RQ1–RQ4 đánh giá mối liên hệ và sự khác biệt "
        "giữa các điều kiện thị trường; RQ5 kiểm tra "
        "giá trị dự báo thực tế trên dữ liệu chưa dùng để huấn luyện.",
    )


# ============================================================
# 09. RQ1 — TRUYỀN DẪN
# ============================================================

elif PAGE == "rq1":

    section("Bức tranh LP của BTC và ETH", "Đồ thị gốc: phản ứng tại ngày 0–30 và khoảng tin cậy HAC 95%.")
    original_figure("lp_responses.png", "Trục 0–30 là số ngày sau biến động vĩ mô, KHÔNG phải năm lịch.")

    hero(
        "RESEARCH QUESTION 01",
        "RQ1 · <em>Truyền dẫn tài chính</em>",
        "Khi VIX, DXY hoặc US2Y thay đổi, lợi suất "
        "Bitcoin và Ethereum có xu hướng phản ứng "
        "theo chiều nào trong cùng ngày?",
    )

    question("RQ1")

    method_note(
        "Local Projections · h = 0",
        "Hệ số LP tại h = 0 đo mối liên hệ cùng ngày "
        "giữa biến tài chính và lợi suất crypto. "
        "Kiểm định FDR giúp hạn chế việc kết luận nhầm "
        "khi thực hiện nhiều kiểm định.",
    )

    research_story(
        'Bối cảnh hình thành RQ1: kênh truyền dẫn cùng ngày',
        'Khi thị trường cổ phiếu Mỹ biến động mạnh, USD lên giá hoặc kỳ vọng lãi suất thay đổi, nhà đầu tư có thể điều chỉnh danh mục tài sản rủi ro, bao gồm BTC và ETH. RQ1 kiểm tra xem sự đồng thời này có xuất hiện trong dữ liệu hay không.',
        'VIX gắn với risk-off và nhu cầu thanh khoản; DXY gắn với điều kiện đồng USD; US2Y gắn với kỳ vọng chính sách tiền tệ. Vì ba biến đo những khía cạnh khác nhau, một hệ số lớn về trị tuyệt đối không có nghĩa biến đó quan trọng hơn nếu chưa chuẩn hóa đơn vị cú sốc.',
        'Kết quả có thể hỗ trợ nhà phân tích xây dựng bảng theo dõi rủi ro vĩ mô, đặt giả thuyết cho quản trị danh mục và thiết kế nghiên cứu tiếp theo. Khi theo dõi VIX/DXY, cần đọc cùng khoảng tin cậy và mức ý nghĩa sau BH-FDR.',
        'LP h=0 cho biết liên hệ có điều kiện trong cùng phiên, không xác định chắc chắn biến nào đi trước về mặt thông tin. Không thể dùng hệ số như hệ số nhân lợi nhuận hoặc dự báo giao dịch.')

    asset, shock = selectors("rq1")

    insight(
        "BIẾN ĐANG PHÂN TÍCH",
        SHOCKS[shock],
        SHOCK_MEANING[shock],
        "white",
    )

    lp = DATA["lp"]
    lp_fdr = DATA["lp_fdr"]

    current = filter_df(
        lp, response=asset, shock=shock, horizon=0
    )

    fdr_current = filter_df(
        lp_fdr, response=asset, shock=shock, horizon=0
    )

    row = first(current)

    if row is None:
        row = first(fdr_current)

    if row is not None and not fdr_current.empty:
        merged_row = row.copy()

        for name in ["p_value_fdr", "p_value"]:
            if name in fdr_current.columns:
                merged_row[name] = fdr_current.iloc[0][name]

        row = merged_row

    section(
        "Kết quả cho lựa chọn hiện tại",
        f"{ASSETS[asset]} · {SHOCKS[shock]}",
    )

    guide(
        f"Khi {shock} tăng, lợi suất {asset} thường tăng hay giảm?",
        "Hệ số âm biểu thị liên hệ ngược chiều; "
        "hệ số dương biểu thị liên hệ cùng chiều.",
        "Đọc hệ số trước, sau đó kiểm tra q-value FDR. "
        "q < 0,05 mới là bằng chứng có ý nghĩa "
        "sau điều chỉnh nhiều kiểm định.",
    )

    if row is not None:
        c1, c2, c3 = st.columns(3)

        with c1:
            kpi(
                "Hệ số LP", fmt(field(row, "estimate")),
                "Tại h = 0", "coral",
            )

        with c2:
            kpi(
                "p-value", fmt(field(row, "p_value")),
                "Kiểm định ban đầu", "violet",
            )

        with c3:
            kpi(
                "q-value FDR",
                fmt(field(row, "p_value_fdr")),
                "Sau điều chỉnh nhiều kiểm định",
                "teal",
            )

        # Một ước lượng đơn lẻ: biểu đồ điểm + CI, tránh trục cột bị phóng đại.
        section(
            'Biểu đồ · Hệ số LP cùng ngày cho lựa chọn hiện tại',
            f'{ASSETS[asset]} trước {SHOCKS[shock]} · mẫu 2018–2025 · h = 0',
            'LOCAL PROJECTIONS · SELECTED PAIR',
        )
        beta = num(field(row, 'estimate'))
        lower = num(field(row, 'ci_lower'))
        upper = num(field(row, 'ci_upper'))
        if np.isfinite(beta):
            err = None
            if np.isfinite(lower) and np.isfinite(upper) and lower <= beta <= upper:
                err = dict(type='data', symmetric=False,
                           array=[upper-beta], arrayminus=[beta-lower],
                           visible=True, color=C['plum'], thickness=2, width=8)
            fig = go.Figure(go.Scatter(
                x=[f'{asset} · {shock}'], y=[beta], mode='markers+text',
                marker=dict(size=17, color=C['coral'] if beta < 0 else C['teal']),
                text=[f'{beta:+.4f}'], textposition='top center',
                error_y=err, name='Hệ số LP tại h = 0',
                hovertemplate=f'{asset} · {shock}<br>Hệ số LP: %{{y:.6f}}<extra></extra>',
            ))
            fig.add_hline(y=0, line_dash='dash', line_color=C['muted'])
            fig.update_yaxes(title='Hệ số LP · h = 0', zeroline=True)
            fig.update_layout(showlegend=False)
            plot(fig, f'rq1_selected_{asset}_{shock}', 400)
            st.caption('Điểm là hệ số LP; thanh sai số (nếu có) là khoảng tin cậy từ CSV. '
                       'Ý nghĩa thống kê được đánh giá bằng p-value và q-value FDR.')
        conclusion(*lp_interpret(asset, shock, row))
    else:
        st.info(
            "Chưa tìm thấy kết quả LP h = 0 "
            "cho lựa chọn này."
        )

    section(
        "So sánh BTC và ETH theo ba biến tài chính",
        "Biểu đồ giúp nhìn nhanh dấu và độ lớn hệ số.",
    )

    guide(
        "Tài sản nào có hệ số cùng chiều hoặc ngược chiều?",
        "Cột phía dưới đường 0 biểu thị hệ số âm; "
        "cột phía trên biểu thị hệ số dương.",
        "Không so sánh trực tiếp độ lớn giữa VIX, "
        "DXY và US2Y vì đơn vị của các biến khác nhau.",
    )

    all_h0 = filter_df(lp, horizon=0)

    if (
        not all_h0.empty
        and {"response", "shock", "estimate"}.issubset(
            all_h0.columns
        )
    ):
        fig = go.Figure()

        for coin, color in [
            ("BTC", C["teal"]),
            ("ETH", C["coral"]),
        ]:
            part = filter_df(all_h0, response=coin)
            part = numeric_frame(part, "estimate")

            fig.add_trace(
                go.Bar(
                    x=part["shock"],
                    y=part["estimate"],
                    name=coin,
                    marker_color=color,
                    text=part["estimate"].round(3),
                    textposition="outside",
                    textfont=dict(color=C["ink"], size=14),
                )
            )

        fig.update_layout(barmode="group")
        fig.update_yaxes(title="Hệ số LP · h = 0")

        plot(fig, "rq1_comparison", 450)

        conclusion(
            "VIX và DXY có hệ số âm cùng ngày "
            "với BTC và ETH trong mô hình cơ sở.",
            "Điều này gợi ý bất ổn tài chính và "
            "sức mạnh USD cao hơn thường gắn với "
            "lợi suất crypto thấp hơn. "
            "Theo kết quả nghiên cứu, 8/186 hệ số LP "
            "còn ý nghĩa sau điều chỉnh BH-FDR 5%.",
            "Biểu đồ cột chỉ thể hiện hệ số, "
            "không thể hiện đầy đủ khoảng tin cậy. "
            "Cần dùng kiểm định để đánh giá độ tin cậy; "
            "không suy ra nhân quả.",
        )

    show_table(all_h0, "Hệ số LP cùng ngày")

    section('Phân tích bổ sung · Bản đồ ý nghĩa FDR', 'Ô xanh thể hiện kiểm định còn ý nghĩa sau điều chỉnh FDR 5%.')
    fdr_overview(lp_fdr, 'rq1_fdr_heatmap', asset)
    fdr_count_summary(lp_fdr, 'Tất cả chân trời LP của tài sản đã chọn', asset)
    deep_analysis('Đọc sâu kết quả truyền dẫn',
        f'Với {asset}, các hệ số theo {shock} có thể âm hoặc dương tùy chân trời. Không dùng dấu hệ số một mình để khẳng định tác động.',
        deep_mechanism(shock),
        'Mỗi hệ số được kiểm định riêng, nhưng có 186 kiểm định LP trong nghiên cứu. Chỉ 8 kiểm định còn ý nghĩa sau BH-FDR 5%. Bản đồ FDR giúp phân biệt tín hiệu được kiểm chứng và hệ số chỉ mang tính mô tả.',
        'Hệ số của ba cú sốc khác đơn vị. Không so sánh trực tiếp trị số VIX, DXY và US2Y; cũng không suy ra lợi nhuận giao dịch hoặc quan hệ nhân quả.')

    answer(
        "RQ1",
        "Có bằng chứng về liên hệ âm cùng ngày "
        "giữa VIX, DXY và lợi suất BTC/ETH.",
        "Đây là phát hiện nổi bật nhất trong phần "
        "truyền dẫn. Với US2Y, bằng chứng yếu hơn. "
        "Mối liên hệ thống kê không đồng nghĩa "
        "với việc các biến vĩ mô trực tiếp gây ra "
        "thay đổi giá tiền mã hóa.",
    )


# ============================================================
# 10. RQ2 — PHẢN ỨNG ĐỘNG
# ============================================================

elif PAGE == "rq2":

    section("Phản ứng động VAR(5) – BTC", "Kết quả IRF gốc và khoảng tin cậy 95%.")
    original_figure("irf_btc.png", "Trục ngang là phiên phản ứng 0–30, không phải năm.")
    section("Phản ứng động VAR(5) – ETH", "Cùng cách đọc với BTC.")
    original_figure("irf_eth.png", "IRF Cholesky phụ thuộc thứ tự biến, không phải cú sốc nhân quả đã nhận diện.")

    hero(
        "RESEARCH QUESTION 02",
        "RQ2 · <em>Phản ứng theo thời gian</em>",
        "Không chỉ quan tâm phản ứng cùng ngày, "
        "nghiên cứu còn xem hệ số của BTC/ETH "
        "thay đổi như thế nào ở các chân trời tiếp theo.",
    )

    question("RQ2")

    method_note(
        "Hai phương pháp bổ trợ: LP và VAR",
        "LP theo dõi hệ số tại từng chân trời ngày lịch. "
        "VAR(5) xây dựng phản ứng xung lực IRF "
        "theo phiên có dữ liệu vĩ mô. "
        "Hai phương pháp không hoàn toàn cùng đơn vị "
        "cú sốc hoặc đơn vị thời gian.",
    )

    research_story(
        'Bối cảnh RQ2: thị trường có thể hấp thụ thông tin theo nhiều nhịp',
        'Một biến động vĩ mô có thể được phản ánh ngay trong ngày, tiếp tục điều chỉnh ở những ngày sau hoặc nhanh chóng mất dấu. Vì vậy, kết luận chỉ dựa trên hệ số cùng ngày là chưa đủ để mô tả phản ứng động.',
        'LP ước lượng riêng lợi suất tại từng chân trời ngày lịch; VAR mô hình hóa tương tác động của cả hệ thống trên các phiên có dữ liệu vĩ mô. IRF trực giao hóa theo thứ tự Cholesky đã định. Hai đường trả lời các câu hỏi liên quan nhưng không hoàn toàn đồng nhất.',
        'Nếu phản ứng nhanh chóng quay về gần 0, đó là thông tin hữu ích về độ bền của mối liên hệ ước lượng. Nếu dải tin cậy rộng hoặc cắt 0, nhà phân tích không nên diễn giải các đỉnh của đường như một tác động bền vững.',
        'Không cộng các hệ số LP thành phản ứng tích lũy nếu chưa có đặc tả tích lũy. Không quy đổi trực tiếp một phiên macro thành một ngày lịch hoặc đồng nhất cú sốc VAR với một đơn vị thay đổi trong LP.')

    asset, shock = selectors("rq2")

    section(
        "Biểu đồ 1 · Local Projections",
        f"Phản ứng của {asset} trước {shock} theo ngày lịch.",
    )

    guide(
        "Phản ứng mạnh nhất ở thời điểm nào?",
        "Đường màu biểu thị hệ số ước lượng. "
        "Vùng tô mờ, nếu có, là khoảng tin cậy. "
        "Đường ngang tại 0 là mốc không có phản ứng ước lượng.",
        "Nếu khoảng tin cậy chứa 0, "
        "chưa thể kết luận hệ số khác 0 "
        "theo kiểm định tại chân trời đó.",
    )

    lp = filter_df(
        DATA["lp"], response=asset, shock=shock
    )

    if response_chart(
        lp, "rq2_lp", C["coral"],
        "Số ngày sau biến động (ngày lịch)",
    ):
        conclusion(
            *dynamic_interpret(asset, shock, lp, "LP")
        )

    section(
        "Biểu đồ 2 · VAR(5) và IRF",
        "Một cách tiếp cận khác để kiểm tra "
        "diễn biến phản ứng theo phiên vĩ mô.",
    )

    guide(
        "Kết quả VAR có cùng chiều với LP không?",
        "Đọc chiều của đường IRF và xem phản ứng "
        "có quay về gần 0 ở các chân trời sau không.",
        "VAR sử dụng thứ tự Cholesky "
        "VIX → DXY → US2Y → BTC → ETH. "
        "Không so sánh trực tiếp trị số hệ số với LP.",
    )

    irf = filter_df(
        DATA["irf"], response=asset, shock=shock
    )

    if response_chart(
        irf, "rq2_var", C["violet"],
        "Số phiên giao dịch vĩ mô sau biến động",
    ):
        conclusion(
            *dynamic_interpret(asset, shock, irf, "VAR")
        )

    show_table(lp, "Kết quả Local Projections")
    show_table(irf, "Kết quả VAR / IRF")

    rq2_fdr = filter_df(DATA['lp_fdr'], response=asset, shock=shock)
    if not rq2_fdr.empty and 'p_value_fdr' in rq2_fdr:
        section('Bằng chứng FDR theo chân trời',
                'Đối chiếu trực tiếp các chân trời LP với q-value sau điều chỉnh nhiều kiểm định.')
        fdr_overview(rq2_fdr, 'rq2_selected_fdr')
        show_table(rq2_fdr, 'q-value FDR của các chân trời đã chọn')

    section('Phân tích bổ sung · Cơ chế và mức độ bền vững', 'Phân biệt dấu, độ lớn và độ tin cậy thống kê.')
    deep_analysis('Vì sao đường phản ứng thay đổi theo chân trời?',
        f'Đường LP và VAR/IRF của {asset} trước {shock} cho thấy diễn biến hệ số theo thời gian; đỉnh tuyệt đối không nhất thiết là tác động có ý nghĩa.',
        deep_mechanism(shock) + ' Phản ứng có thể điều chỉnh theo quá trình định giá lại rủi ro và tái cân bằng danh mục.',
        'Đọc khoảng tin cậy tại từng h, đối chiếu bảng LP FDR. LP đo ngày lịch còn VAR đo phiên vĩ mô; VAR(5) còn phụ thuộc thứ tự Cholesky VIX → DXY → US2Y → BTC → ETH.',
        'Không xem h có hệ số lớn nhất là bằng chứng phản ứng kéo dài. Không so sánh trực tiếp hai phương pháp về trị số hoặc chân trời thời gian.')

    answer(
        "RQ2",
        "Phản ứng ước lượng không cố định theo thời gian.",
        "LP và VAR cho phép quan sát chiều hướng, "
        "độ lớn và diễn biến phản ứng tại các chân trời. "
        "Tuy nhiên, không thể dựa vào một đỉnh "
        "hoặc một đoạn đường phản ứng để khẳng định "
        "tác động kéo dài có ý nghĩa thống kê. "
        "Cần xét khoảng tin cậy và kiểm định FDR.",
    )


# ============================================================
# 11. RQ3 — TRƯỚC / SAU 2020
# ============================================================

elif PAGE == "rq3":

    hero(
        "RESEARCH QUESTION 03",
        "RQ3 · <em>Trước và sau 2020</em>",
        "Kiểm tra liệu mối liên hệ giữa điều kiện "
        "tài chính toàn cầu và crypto có thay đổi "
        "giữa hai giai đoạn hay không.",
    )

    question("RQ3")

    method_note(
        "So sánh hai giai đoạn",
        "Giai đoạn trước 2020 là 2018–2019; "
        "giai đoạn sau 2020 là 2020–2025. "
        "Nghiên cứu kiểm định trực tiếp chênh lệch "
        "hệ số và điều chỉnh BH-FDR.",
    )

    research_story(
        'Bối cảnh RQ3: giả thuyết thay đổi cấu trúc sau năm 2020',
        'Mốc năm 2020 gắn với một thay đổi lớn về điều kiện thị trường, chính sách tiền tệ và sự chú ý dành cho tài sản số. Nghiên cứu đặt giả thuyết rằng độ nhạy của BTC/ETH trước VIX, DXY và US2Y có thể khác giữa 2018–2019 và 2020–2025.',
        'Cần phân biệt hai nhận định: hệ số từng giai đoạn có khác 0 hay không và chênh lệch giữa hai hệ số có khác 0 hay không. Một hệ số có ý nghĩa ở giai đoạn sau nhưng không có ý nghĩa ở giai đoạn trước chưa đủ chứng minh hai giai đoạn khác nhau.',
        'Kết quả kiểm định chênh lệch hỗ trợ đánh giá giả thuyết về tính ổn định của quan hệ Macro–Crypto. Nếu chưa đạt FDR, cách diễn giải phù hợp là chưa xác nhận đứt gãy hệ số, chứ không phải đã chứng minh thị trường không thay đổi.',
        'Mẫu trước 2020 ngắn hơn đáng kể; việc chọn mốc 2020 là quyết định thiết kế nghiên cứu, không phải ngày đứt gãy được xác định nội sinh. Khác biệt cỡ mẫu ảnh hưởng độ chính xác của ước lượng.')

    asset, shock = selectors("rq3")

    section("Hệ số biến đổi qua từng năm (2019–2025)",
            "Dữ liệu rolling 252 phiên: nhìn được năm nào độ nhạy với VIX/DXY/US2Y tăng hoặc giảm.")
    guide("Quan hệ Macro–Crypto có ổn định qua thời gian?",
          "Trục ngang là năm thực tế; trục dọc là hệ số ước lượng trong cửa sổ 252 phiên.",
          "Hệ số thay đổi không tự chứng minh đứt gãy năm 2020; kiểm định RQ3 ở bên dưới mới trả lời điều đó.")
    rolling_year_chart(DATA["rolling"], asset, shock, "rq3_rolling_years")

    section(
        "Biểu đồ · So sánh 2018–2019 với 2020–2025",
        f"{asset} trước biến động {shock} · Pre: 2018–2019 | Post: 2020–2025.",
    )

    guide(
        "Hệ số phản ứng có thay đổi giữa 2018–2019 và 2020–2025 không?",
        "Trục ngang ghi rõ 2018–2019 và 2020–2025. Chọn số ngày sau biến động "
        "để so sánh hệ số tại cùng một thời điểm phản ứng.",
        "Hai cột khác nhau chưa đủ để kết luận khác biệt. "
        "Cần xem kiểm định chênh lệch sau FDR.",
    )

    sub = filter_df(DATA["subperiod"], response=asset, shock=shock)
    available_days = sorted(set(pd.to_numeric(sub.get("horizon", pd.Series(dtype=float)),
                                                   errors="coerce").dropna().astype(int)))
    selected_days = st.selectbox(
        "📅 So sánh tại bao nhiêu ngày sau biến động vĩ mô?",
        available_days if available_days else [0],
        format_func=lambda day: f"Sau {day} ngày" if day else "Cùng ngày (0 ngày)",
        key="rq3_response_day",
    )

    difference = filter_df(
        DATA["rq3"], response=asset, shock=shock
    )

    rq3_year_comparison(sub, difference, "rq3_period_lines", selected_days)

    h0 = first(filter_df(difference, horizon=selected_days))

    if h0 is not None:
        c1, c2, c3 = st.columns(3)

        with c1:
            kpi(
                "Hệ số trước 2020",
                fmt(field(h0, "pre_beta")),
                f"Giai đoạn 2018–2019 · sau {selected_days} ngày · mô hình tương tác",
                "violet",
            )

        with c2:
            kpi(
                "Hệ số sau 2020",
                fmt(field(h0, "post_beta")),
                f"Giai đoạn 2020–2025 · sau {selected_days} ngày · mô hình tương tác",
                "coral",
            )

        with c3:
            kpi(
                "q-value FDR",
                fmt(field(h0, "p_value_fdr")),
                f"Kiểm định chênh lệch · sau {selected_days} ngày",
                "teal",
            )

        conclusion(
            *difference_interpret(
                h0,
                "sau 2020 trừ trước 2020",
                [
                    "difference_post_minus_pre",
                    "difference",
                    "difference_stress_minus_calm",
                ],
                (
                    f"Đây là kết quả so sánh {asset} "
                    f"trước biến {shock} sau {selected_days} ngày."
                ),
            ),
            heading='DIỄN GIẢI KIỂM ĐỊNH CHÊNH LỆCH',
        )

    show_table(difference, "Kiểm định chênh lệch RQ3")
    show_table(sub, "Hệ số từng giai đoạn")

    section('Đối chiếu kết quả theo năm', 'Hai giai đoạn nghiên cứu được hiển thị trực tiếp bằng năm: 2018–2019 và 2020–2025.')
    st.caption('Dữ liệu RQ3 được ước lượng theo hai giai đoạn, không phải hệ số riêng cho từng năm. Vì vậy không thể gắn một hệ số riêng cho 2020, 2021, 2022… nếu chưa ước lượng thêm mô hình theo năm. Biểu đồ phía trên thể hiện đúng hai giai đoạn gốc; bảng bên dưới giữ nguyên toàn bộ kiểm định theo số ngày.')
    fdr_count_summary(DATA['rq3'], 'Kiểm định chênh lệch Pre/Post', asset)
    deep_analysis('Vì sao nhìn khác mà chưa kết luận thay đổi?',
        'Các đường Pre/Post có thể cách nhau ở một số chân trời nhưng kiểm định chênh lệch mới là cơ sở kết luận.',
        'Sau 2020, thị trường crypto có thể thay đổi về quy mô và nhà đầu tư, trong khi chính sách tiền tệ trải qua nhiều chế độ. Những thay đổi này làm giả thuyết đứt gãy cấu trúc hợp lý về kinh tế.',
        'Trong 186 kiểm định chênh lệch Pre/Post, không có kiểm định nào còn ý nghĩa sau BH-FDR 5%. Độ lớn chênh lệch ước lượng không đủ để bác bỏ giả thuyết bằng nhau.',
        'Không có bằng chứng khác biệt không chứng minh hai giai đoạn tương đương. Cỡ mẫu, độ nhiễu và cách chọn mốc 2020 đều ảnh hưởng sức mạnh kiểm định.')

    answer(
        "RQ3",
        "Chưa đủ bằng chứng về thay đổi truyền dẫn "
        "có hệ thống sau năm 2020.",
        "Trong 186 kiểm định chênh lệch trước/sau 2020, "
        "không có kiểm định nào còn ý nghĩa "
        "sau điều chỉnh BH-FDR 5%. "
        "Điều này không chứng minh hai giai đoạn "
        "hoàn toàn giống nhau, mà cho thấy dữ liệu "
        "chưa cung cấp bằng chứng đủ mạnh về khác biệt.",
    )


# ============================================================
# 12. RQ4 — CALM / STRESS
# ============================================================

elif PAGE == "rq4":

    section("Calm và Stress – toàn bộ BTC/ETH", "Biểu đồ gốc từ mô hình Local Projections có điều kiện.")
    original_figure("regime_comparison.png", "Trục ngang là số ngày phản ứng; vùng màu là khoảng tin cậy của từng trạng thái.")

    hero(
        "RESEARCH QUESTION 04",
        "RQ4 · <em>Calm và Stress</em>",
        "Liệu thị trường crypto phản ứng khác đi "
        "khi điều kiện tài chính căng thẳng "
        "so với khi thị trường bình ổn?",
    )

    question("RQ4")

    method_note(
        "Phân loại trạng thái theo VIX",
        "Stress khi VIX của phiên vĩ mô trước đó "
        "từ 30 trở lên; các quan sát còn lại là Calm. "
        "Việc dùng VIX phiên trước giúp tránh "
        "dùng thông tin cùng ngày để xác định trạng thái.",
    )

    c1, c2 = st.columns(2)

    with c1:
        kpi(
            "Calm", "1.839",
            "Quan sát ở trạng thái bình ổn",
            "teal",
        )

    with c2:
        kpi(
            "Stress", "151",
            "Quan sát ở trạng thái căng thẳng",
            "coral",
        )

    insight(
        "LƯU Ý VỀ CỠ MẪU",
        "Stress có ít quan sát hơn đáng kể.",
        "Số quan sát Stress nhỏ khiến hệ số "
        "có thể kém chính xác và khoảng tin cậy rộng. "
        "Vì vậy, kết quả không có ý nghĩa thống kê "
        "cần được diễn giải thận trọng.",
        "gold",
    )

    research_story(
        'Bối cảnh RQ4: truyền dẫn có thể phụ thuộc trạng thái rủi ro',
        'Trong những giai đoạn căng thẳng, nhu cầu nắm giữ tiền mặt, yêu cầu ký quỹ và hoạt động giảm đòn bẩy có thể làm phản ứng của tài sản rủi ro khác so với giai đoạn bình ổn. Đây là động cơ kinh tế của giả thuyết phi tuyến theo trạng thái.',
        'Nhóm dùng VIX phiên vĩ mô trước đó ≥ 30 để phân loại Stress; những phiên còn lại là Calm. Quy tắc trễ nhằm tránh sử dụng VIX cùng ngày để gắn nhãn trạng thái. Chênh lệch hệ số cần được kiểm định trực tiếp, không chỉ quan sát hai đường.',
        'Nếu bằng chứng đủ mạnh, phân tích trạng thái có thể hỗ trợ xây dựng các kịch bản stress testing cho danh mục crypto. Nhưng trong dữ liệu hiện tại, kết quả chưa đạt FDR nên chỉ nên coi đây là giả thuyết quản trị rủi ro cần kiểm tra thêm.',
        'Stress chỉ có 151 quan sát so với 1.839 Calm. Mẫu mất cân đối làm độ bất định cao và hạn chế khả năng phát hiện khác biệt thực sự. Ngưỡng 30 là quy ước nghiên cứu, không phải ranh giới kinh tế tuyệt đối.')

    asset, shock = selectors("rq4")

    section(
        "Biểu đồ · Phản ứng trong hai trạng thái",
        f"So sánh {asset} trước {shock} · Calm và Stress trong mẫu 2018–2025.",
    )

    guide(
        "Khi thị trường căng thẳng, hệ số có thay đổi không?",
        "So sánh đường Calm và Stress ở cùng chân trời. "
        "Đường càng xa 0 thì hệ số ước lượng "
        "có độ lớn tuyệt đối càng cao.",
        "Phải kiểm tra chênh lệch Stress − Calm "
        "bằng kiểm định thống kê, không chỉ nhìn hình.",
    )

    regime = filter_df(
        DATA["regime"], response=asset, shock=shock
    )

    calm = filter_df(regime, regime="Calm")
    stress = filter_df(regime, regime="Stress")

    two_lines(
        [
            ("Calm", calm, C["teal"]),
            ("Stress", stress, C["coral"]),
        ],
        "rq4_regime_lines",
        "Số ngày sau biến động (ngày lịch)",
        "Hệ số LP",
    )

    difference = filter_df(
        DATA["rq4"], response=asset, shock=shock
    )

    h0 = first(filter_df(difference, horizon=0))

    if h0 is not None:
        conclusion(
            *difference_interpret(
                h0,
                "Stress trừ Calm",
                [
                    "difference_stress_minus_calm",
                    "difference",
                ],
                (
                    f"Đây là kiểm định cho {asset} "
                    f"và {shock} tại h = 0."
                ),
            ),
            heading='DIỄN GIẢI KIỂM ĐỊNH CHÊNH LỆCH',
        )
    else:
        insight(
            "KIỂM ĐỊNH",
            "Chưa có dòng kiểm định tại h = 0.",
            "Biểu đồ phản ứng không thay thế "
            "được kiểm định chênh lệch hệ số.",
            "gold",
        )

    show_table(difference, "Kiểm định Calm/Stress")
    show_table(regime, "Hệ số theo trạng thái")

    rq4_all = DATA['rq4']
    if not rq4_all.empty:
        raw_col = col(rq4_all, 'difference_p_value', 'p_value')
        fdr_col = col(rq4_all, 'p_value_fdr')
        if raw_col and fdr_col:
            raw = pd.to_numeric(rq4_all[raw_col], errors='coerce')
            adjusted = pd.to_numeric(rq4_all[fdr_col], errors='coerce')
            c_raw, c_fdr = st.columns(2)
            with c_raw:
                kpi('Đạt kiểm định ban đầu', f'{int(raw.lt(.05).sum())}/{int(raw.notna().sum())}',
                    'p-value < 0,05 · toàn bộ RQ4', 'violet')
            with c_fdr:
                kpi('Đạt sau BH-FDR', f'{int(adjusted.lt(.05).sum())}/{int(adjusted.notna().sum())}',
                    'q-value < 0,05 · toàn bộ RQ4', 'teal')

    section('Phân tích bổ sung · Chênh lệch Stress − Calm', 'Đọc chênh lệch cùng với quy mô mẫu hai trạng thái.')
    regime_difference_safe(filter_df(DATA['rq4'], response=asset, shock=shock), 'rq4_difference_bars')
    fdr_count_summary(DATA['rq4'], 'Kiểm định chênh lệch Calm/Stress', asset)
    deep_analysis('Stress có làm truyền dẫn mạnh hơn không?',
        'Không thể kết luận Stress làm phản ứng mạnh hơn chỉ vì đường Stress cao hoặc thấp hơn Calm.',
        'Trong giai đoạn VIX cao, nhu cầu thanh khoản và giảm đòn bẩy có thể tăng. Crypto có thể trở nên nhạy cảm hơn với cùng một thay đổi vĩ mô, nhưng cơ chế này cần được kiểm định.',
        'Mẫu Calm gồm 1.839 quan sát, Stress 151. Trong 186 kiểm định chênh lệch, không có kết quả nào còn ý nghĩa sau BH-FDR 5%.',
        'Mẫu Stress nhỏ khiến khoảng tin cậy rộng và độ mạnh thống kê thấp. Chưa phát hiện khác biệt không đồng nghĩa Stress và Calm có cùng cơ chế.')

    answer(
        "RQ4",
        "Chưa xác nhận được khác biệt truyền dẫn "
        "giữa trạng thái Calm và Stress.",
        "Trong 186 kiểm định chênh lệch, "
        "không có kết quả nào còn ý nghĩa "
        "sau điều chỉnh BH-FDR 5%. "
        "Đặc biệt, mẫu Stress nhỏ nên "
        "không thể xem kết quả này là bằng chứng "
        "hai trạng thái phản ứng hoàn toàn giống nhau.",
    )


# ============================================================
# 13. RQ5 — MACHINE LEARNING
# ============================================================

elif PAGE == "rq5":

    section("Dự báo so với thực tế trong năm 2025", "Biểu đồ gốc 365 ngày của cả BTC và ETH.")
    original_figure("forecast_comparison.png", "Đường xám là độ lớn lợi suất thực tế, các đường còn lại là dự báo; trục ngang hiển thị tháng năm 2025.")

    hero(
        "RESEARCH QUESTION 05",
        "RQ5 · <em>Machine Learning</em>",
        "Kiểm tra giá trị thực tế của dữ liệu vĩ mô: "
        "khi thêm VIX, DXY và US2Y, mô hình "
        "có dự báo chính xác hơn trên dữ liệu mới không?",
    )

    question("RQ5")

    method_note(
        "Dự báo độ lớn lợi suất ngày tiếp theo",
        "Biến mục tiêu là |r(t+1)|, không phải "
        "dự báo giá hay chiều tăng giảm. "
        "So sánh Historical30, Elastic Net và XGBoost "
        "trên tập kiểm tra năm 2025 bằng MAE, RMSE.",
    )

    research_story(
        'Bối cảnh RQ5: giải thích được chưa chắc dự báo được',
        'Một biến vĩ mô có thể có liên hệ thống kê với lợi suất crypto trong mẫu nhưng không giúp giảm sai số trên dữ liệu chưa quan sát. Thông tin có thể đã được phản ánh trong lịch sử giá, hoặc quan hệ thay đổi theo thời gian.',
        'RQ5 dự báo độ lớn tuyệt đối của lợi suất log ngày tiếp theo, không dự báo dấu tăng/giảm. So sánh Crypto-only với Crypto + Macro trong cùng thuật toán nhằm cô lập phần đóng góp bổ sung của dữ liệu VIX, DXY và US2Y.',
        'Với quản trị rủi ro, một mô hình dự báo độ lớn biến động có thể giúp dự kiến ngày rủi ro cao, điều chỉnh giới hạn vị thế hoặc chuẩn bị thanh khoản. Nhưng lợi ích thực tiễn chỉ được củng cố khi sai số ngoài mẫu giảm ổn định và có bằng chứng thống kê.',
        'Không suy ra chiến lược mua/bán từ dự báo |r(t+1)|. Kết quả năm 2025 không bảo đảm lặp lại ở những năm khác; dữ liệu phải được chốt theo thời điểm sẵn có để tránh nhìn trước tương lai.')

    asset = st.selectbox(
        "🪙 Chọn tài sản dự báo",
        ["BTC", "ETH"],
        format_func=lambda x: ASSETS[x],
        key="rq5_asset",
    )

    section(
        "Biểu đồ 1 · Mô hình nào sai số thấp nhất?",
        "Sai số càng thấp, dự báo càng chính xác "
        "theo chỉ tiêu đang chọn.",
    )

    metric = st.selectbox(
        "📐 Chọn thước đo sai số",
        ["MAE", "RMSE"],
        key="rq5_metric",
    )

    guide(
        f"Mô hình nào dự báo {asset} tốt nhất theo {metric}?",
        (
            "MAE là sai số tuyệt đối trung bình. "
            "RMSE phạt mạnh hơn các sai số lớn. "
            "Với cả hai chỉ tiêu, giá trị thấp hơn là tốt hơn."
        ),
        "Quan sát mô hình tốt nhất, rồi so sánh "
        "Crypto-only với Crypto + Macro trong cùng thuật toán.",
    )

    comparison = DATA["comparison"].copy()

    if "response" in comparison.columns:
        comparison = filter_df(
            comparison, response=asset
        )
    elif "asset" in comparison.columns:
        comparison = filter_df(
            comparison, asset=asset
        )

    part = filter_df(comparison, metric=metric)

    if (
        not part.empty
        and {"model", "feature_set", "value"}.issubset(
            part.columns
        )
    ):
        part = numeric_frame(part, "value")
        part = part.dropna(subset=["value"])
        part = part.sort_values("value")

        if not part.empty:
            part["label"] = (
                part["model"].astype(str)
                + " · "
                + part["feature_set"].astype(str)
            )

            colors = [
                C["teal"]
                if "crypto_only" in str(x).lower()
                else C["coral"]
                for x in part["feature_set"]
            ]

            fig = go.Figure(
                go.Bar(
                    x=part["value"],
                    y=part["label"],
                    orientation="h",
                    marker_color=colors,
                    text=part["value"].round(4),
                    textposition="outside",
                    textfont=dict(
                        color=C["ink"], size=14
                    ),
                )
            )

            fig.update_layout(
                yaxis=dict(autorange="reversed")
            )
            fig.update_xaxes(title=metric)

            plot(fig, "rq5_comparison", 480)

            best = part.iloc[0]

            conclusion(
                (
                    f"Mô hình có {metric} thấp nhất "
                    f"là {best['model']} · "
                    f"{best['feature_set']}."
                ),
                (
                    f"Sai số {metric} = "
                    f"{fmt(best['value'])}. "
                    "Mô hình này có sai số thấp nhất "
                    "trong những cấu hình đang hiển thị."
                ),
                (
                    "Mô hình có sai số thấp nhất "
                    "chưa đủ để chứng minh thêm dữ liệu vĩ mô "
                    "là có ích. Cần so sánh hai bộ đặc trưng "
                    "trong cùng thuật toán và xét kiểm định "
                    "sai số dự báo."
                ),
            )

            section(
                "Biểu đồ 2 · Thêm Macro có thực sự tốt hơn?",
                "So sánh trực tiếp hai bộ đặc trưng "
                "trong từng thuật toán.",
            )

            guide(
                "Bổ sung VIX, DXY, US2Y làm sai số giảm hay tăng?",
                "Lấy sai số Crypto-only trừ sai số Crypto + Macro. "
                "Kết quả dương nghĩa là thêm Macro giúp giảm sai số; "
                "âm nghĩa là thêm Macro làm sai số tăng.",
                "Chỉ so sánh trong cùng thuật toán, "
                "cùng tài sản và cùng thước đo.",
            )

            compare_rows = []

            for model in unique_values(part, "model"):
                model_part = filter_df(
                    part, model=model
                )

                crypto_rows = model_part[
                    model_part["feature_set"]
                    .astype(str)
                    .str.lower()
                    .str.contains("crypto_only", regex=False)
                ]

                macro_rows = model_part[
                    model_part["feature_set"]
                    .astype(str)
                    .str.lower()
                    .str.contains("macro", regex=False)
                ]

                if crypto_rows.empty or macro_rows.empty:
                    continue

                base = num(crypto_rows.iloc[0]["value"])
                extended = num(macro_rows.iloc[0]["value"])

                if np.isfinite(base) and np.isfinite(extended):
                    compare_rows.append(
                        {
                            "model": str(model),
                            "crypto_only": base,
                            "crypto_macro": extended,
                            "improvement": base - extended,
                        }
                    )

            if compare_rows:
                compare_df = pd.DataFrame(compare_rows)

                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        x=compare_df["model"],
                        y=compare_df["crypto_only"],
                        name="Crypto-only",
                        marker_color=C["teal"],
                    )
                )

                fig.add_trace(
                    go.Bar(
                        x=compare_df["model"],
                        y=compare_df["crypto_macro"],
                        name="Crypto + Macro",
                        marker_color=C["coral"],
                    )
                )

                fig.update_layout(barmode="group")
                fig.update_yaxes(title=metric)

                plot(fig, "rq5_feature_comparison", 440)

                for _, item in compare_df.iterrows():
                    change = item["improvement"]

                    if change > 0:
                        finding = (
                            f"{item['model']}: thêm Macro "
                            "giúp giảm sai số."
                        )
                    elif change < 0:
                        finding = (
                            f"{item['model']}: thêm Macro "
                            "làm sai số tăng."
                        )
                    else:
                        finding = (
                            f"{item['model']}: hai bộ biến "
                            "có sai số bằng nhau."
                        )

                    insight(
                        "SO SÁNH TRỰC TIẾP",
                        finding,
                        (
                            f"Crypto-only = "
                            f"{fmt(item['crypto_only'])}; "
                            f"Crypto + Macro = "
                            f"{fmt(item['crypto_macro'])}; "
                            f"mức giảm sai số = "
                            f"{fmt(change)}. "
                            "Giá trị dương là cải thiện, "
                            "giá trị âm là suy giảm."
                        ),
                        "teal" if change > 0 else "coral",
                    )
            else:
                st.info(
                    "Chưa nhận diện được đầy đủ hai bộ "
                    "Crypto-only và Crypto + Macro "
                    "để so sánh trực tiếp."
                )

    else:
        st.info(
            "Chưa tìm thấy bảng model_comparison.csv "
            "đúng cấu trúc."
        )

    section(
        "Biểu đồ 3 · Dự báo và giá trị thực tế",
        "Kiểm tra mô hình có theo sát độ lớn "
        "lợi suất thực tế trong năm 2025 không.",
    )

    forecast = DATA["forecast"].copy()

    if "response" in forecast.columns:
        forecast = filter_df(
            forecast, response=asset
        )
    elif "asset" in forecast.columns:
        forecast = filter_df(
            forecast, asset=asset
        )

    model_options = unique_values(forecast, "model")

    if model_options:
        model = st.selectbox(
            "Chọn mô hình dự báo",
            model_options,
            key="rq5_forecast_model",
        )

        model_data = filter_df(
            forecast, model=model
        )

        features = unique_values(
            model_data, "feature_set"
        )

        if features:
            feature_set = st.selectbox(
                "Chọn bộ đặc trưng",
                features,
                key="rq5_forecast_features",
            )

            model_data = filter_df(
                model_data, feature_set=feature_set
            )

        guide(
            "Mô hình dự báo có theo kịp những ngày biến động mạnh?",
            "Đường thực tế thể hiện |r(t+1)| đã xảy ra. "
            "Đường dự báo thể hiện giá trị mô hình ước tính.",
            "Quan sát những thời điểm hai đường cách xa nhau, "
            "đặc biệt khi độ lớn lợi suất thực tế tăng vọt.",
        )

        if {
            "date", "actual", "predicted"
        }.issubset(model_data.columns):

            part = model_data.copy()
            part["date"] = pd.to_datetime(
                part["date"], errors="coerce"
            )

            part = numeric_frame(
                part, "actual", "predicted"
            )

            part = part.dropna(
                subset=["date", "actual", "predicted"]
            ).sort_values("date")

            if not part.empty:
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=part["date"],
                        y=part["actual"],
                        mode="lines",
                        name="Thực tế",
                        line=dict(
                            color=C["plum"], width=2.5
                        ),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=part["date"],
                        y=part["predicted"],
                        mode="lines",
                        name="Dự báo",
                        line=dict(
                            color=C["coral"], width=2.5
                        ),
                    )
                )

                fig.update_yaxes(
                    title="Độ lớn lợi suất (%)"
                )
                fig.update_xaxes(title="Ngày")

                plot(fig, "rq5_forecast_series", 460)

                mae = (
                    part["actual"] - part["predicted"]
                ).abs().mean()

                conclusion(
                    "Đường dự báo và thực tế "
                    "không trùng nhau hoàn toàn.",
                    (
                        f"Với lựa chọn hiện tại, "
                        f"MAE tính từ các dòng đang hiển thị "
                        f"là {fmt(mae)} điểm phần trăm. "
                        "Khoảng cách giữa hai đường "
                        "phản ánh sai số dự báo từng ngày."
                    ),
                    (
                        "Biểu đồ này mô tả chất lượng dự báo "
                        "của một cấu hình. "
                        "Muốn kết luận Macro có giá trị bổ sung "
                        "phải so sánh hai bộ biến "
                        "và kiểm định chênh lệch sai số."
                    ),
                )
            else:
                st.info(
                    "Không có dòng dự báo hợp lệ."
                )
        else:
            st.info(
                "Chưa nhận diện được các cột "
                "date, actual, predicted."
            )
    else:
        st.info(
            "Chưa có dữ liệu dự báo theo ngày "
            "trong forecast_results.csv."
        )

    section(
        "Bằng chứng thống kê về lợi ích dự báo",
        "Kiểm tra xem mức cải thiện hoặc suy giảm "
        "có đáng tin về mặt thống kê hay không.",
    )

    significance = DATA["significance"].copy()

    if "response" in significance.columns:
        significance = filter_df(
            significance, response=asset
        )
    elif "asset" in significance.columns:
        significance = filter_df(
            significance, asset=asset
        )

    insight(
        "CÁCH HIỂU KIỂM ĐỊNH",
        "Sai số thấp hơn chưa chắc là cải thiện đáng tin.",
        "Block bootstrap so sánh chênh lệch sai số "
        "trên các khối 7 ngày, với 2.000 lần lặp. "
        "Nếu khoảng tin cậy của mức giảm sai số "
        "chứa 0, chưa thể khẳng định "
        "một bộ biến dự báo tốt hơn.",
        "violet",
    )

    show_table(
        significance,
        "Kiểm định khác biệt dự báo",
    )

    section(
        "Những biến nào được mô hình sử dụng nhiều?",
        "Feature importance là công cụ hỗ trợ "
        "giải thích mô hình, không phải bằng chứng nhân quả.",
    )

    importance = DATA["importance"].copy()

    if "response" in importance.columns:
        importance = filter_df(
            importance, response=asset
        )
    elif "asset" in importance.columns:
        importance = filter_df(
            importance, asset=asset
        )

    if (
        not importance.empty
        and {"feature", "importance"}.issubset(
            importance.columns
        )
    ):
        model_values = unique_values(
            importance, "model"
        )

        if model_values:
            chosen_model = st.selectbox(
                "Chọn mô hình giải thích",
                model_values,
                key="rq5_importance_model",
            )

            importance = filter_df(
                importance, model=chosen_model
            )

        feature_values = unique_values(
            importance, "feature_set"
        )

        if feature_values:
            chosen_features = st.selectbox(
                "Chọn bộ biến giải thích",
                feature_values,
                key="rq5_importance_features",
            )

            importance = filter_df(
                importance, feature_set=chosen_features
            )

        importance = numeric_frame(
            importance, "importance"
        )

        importance = importance.dropna(
            subset=["importance"]
        ).sort_values(
            "importance", ascending=False
        ).head(12)

        if not importance.empty:
            fig = go.Figure(
                go.Bar(
                    x=importance["importance"].iloc[::-1],
                    y=importance["feature"].iloc[::-1],
                    orientation="h",
                    marker_color=C["violet"],
                )
            )

            fig.update_xaxes(
                title="Mức độ quan trọng theo mô hình"
            )

            plot(fig, "rq5_importance", 470)

            conclusion(
                "Một số đặc trưng đóng góp nhiều hơn "
                "vào dự báo của mô hình.",
                "Biểu đồ xếp hạng các đặc trưng "
                "theo thước đo importance đã xuất "
                "từ mô hình.",
                "Importance không có nghĩa là "
                "biến đó gây ra thay đổi của BTC/ETH. "
                "Các thuật toán cũng có thể sử dụng "
                "những cách tính importance khác nhau.",
            )
    else:
        st.info(
            "Chưa có dữ liệu feature importance "
            "đúng cấu trúc."
        )

    show_table(comparison, "Bảng so sánh mô hình")

    section('Phân tích bổ sung · Giá trị gia tăng của Macro', 'So sánh chênh lệch sai số giữa hai bộ đặc trưng trong cùng thuật toán.')
    feature_increment_chart(DATA['comparison'], asset, metric, 'rq5_macro_increment')
    section('Biểu đồ bổ sung · Khoảng tin cậy bootstrap',
            'Chênh lệch MAE và khoảng tin cậy 95% từ bảng kiểm định của nhóm.')
    forecast_bootstrap_chart(DATA['significance'], asset)
    deep_analysis('Thêm Macro có tạo giá trị dự báo thực tế?',
        'Giá trị gia tăng của Macro phải được đánh giá qua mức giảm MAE/RMSE ngoài mẫu, không qua độ lớn hệ số hồi quy hay feature importance.',
        'VIX, DXY và US2Y có thể phản ánh rủi ro hệ thống, nhưng thông tin đó có thể đã nằm trong chuỗi crypto. Thêm đặc trưng làm tăng chiều mô hình và có nguy cơ học nhiễu.',
        'Tập kiểm tra năm 2025 gồm 365 ngày. Với BTC, Elastic Net Crypto-only MAE ≈ 1,1309 và Crypto+Macro ≈ 1,1643: thêm Macro làm xấu đi, được block bootstrap xác nhận. Với ETH, cải thiện nhỏ chưa được xác nhận thống kê.',
        'Mô hình dự báo |lợi suất log ngày tiếp theo|, không dự báo chiều giá hoặc lợi nhuận giao dịch. Phải đánh giá bootstrap và tính ổn định ngoài mẫu, không chọn mô hình dựa trên một đồ thị đẹp.')

    answer(
        "RQ5",
        "Bổ sung dữ liệu vĩ mô không cải thiện "
        "dự báo một cách nhất quán.",
        "Trên tập ngoài mẫu năm 2025, "
        "không có bằng chứng ổn định rằng "
        "Crypto + Macro luôn tốt hơn Crypto-only. "
        "Một số cấu hình cải thiện rất nhỏ, "
        "trong khi một số khác có sai số tăng. "
        "Đặc biệt, với BTC Elastic Net, "
        "việc thêm Macro làm MAE xấu đi "
        "và khác biệt này được xác nhận "
        "trong kiểm định bootstrap của nghiên cứu.",
    )


# ============================================================
# 14. DỮ LIỆU VÀ CÁCH ĐỌC
# ============================================================

elif PAGE == "methods":

    hero(
        "DATA & RESEARCH GUIDE",
        "Dữ liệu <em>& cách đọc kết quả</em>",
        "Giải thích các biến, cách chuẩn bị dữ liệu "
        "và ý nghĩa của những thuật ngữ "
        "xuất hiện trên dashboard.",
    )

    research_story(
        'Thiết kế nghiên cứu và khả năng tái lập',
        'Dữ liệu được đồng bộ trên lịch ngày liên tục từ 01/01/2018 đến 31/12/2025, gồm 2.922 ngày. Vì crypto giao dịch cả cuối tuần còn các chuỗi tài chính truyền thống có ngày nghỉ, không phải mọi dòng đều có quan sát vĩ mô hợp lệ.',
        'BTC và ETH dùng lợi suất log theo phần trăm. VIX dùng thay đổi theo điểm chỉ số; DXY dùng lợi suất log phần trăm; US2Y dùng thay đổi điểm phần trăm. Sự khác nhau về thước đo cần được giữ nguyên khi diễn giải hệ số LP/VAR.',
        'Các CSV được tạo bởi pipeline nghiên cứu; dashboard chỉ đọc và trình bày kết quả. Khi tái lập, cần giữ nhật ký nguồn, định nghĩa biến, thời điểm công bố dữ liệu, chia mẫu theo thời gian và cùng phiên bản bảng đầu ra.',
        'Ngày quan sát không nhất thiết là thời điểm nhà đầu tư có thể biết thông tin. Không tự điền 0 vào ngày vĩ mô không giao dịch; cần kiểm tra lịch phiên, khoảng cách giữa các quan sát hợp lệ và nguy cơ rò rỉ thông tin ở bài toán ML.')

    section(
        "Nghiên cứu sử dụng dữ liệu gì?",
        "Hai tài sản tiền mã hóa và ba biến "
        "đại diện cho điều kiện tài chính toàn cầu.",
    )

    variable_info = [
        (
            "BTC",
            "Bitcoin",
            "Lợi suất log theo ngày, tính bằng phần trăm.",
            "teal",
        ),
        (
            "ETH",
            "Ethereum",
            "Lợi suất log theo ngày, tính bằng phần trăm.",
            "coral",
        ),
        (
            "VIX",
            "Bất ổn tài chính",
            "Thay đổi VIX theo điểm chỉ số.",
            "violet",
        ),
        (
            "DXY",
            "Sức mạnh USD",
            "Lợi suất log DXY theo phần trăm.",
            "gold",
        ),
        (
            "US2Y",
            "Lợi suất trái phiếu Mỹ 2 năm",
            "Thay đổi lợi suất theo điểm phần trăm.",
            "white",
        ),
    ]

    for code, title, body, tone in variable_info:
        insight(code, title, body, tone)

    section(
        "Vì sao có dữ liệu thiếu?",
        "Crypto giao dịch liên tục, còn dữ liệu "
        "tài chính truyền thống theo phiên.",
    )

    insight(
        "KHÁC BIỆT LỊCH GIAO DỊCH",
        "Dữ liệu thiếu không nhất thiết là lỗi thu thập.",
        "BTC và ETH giao dịch 24/7, bao gồm cuối tuần "
        "và ngày lễ. Trong khi đó VIX, DXY và US2Y "
        "không có quan sát ở nhiều ngày như vậy. "
        "Nghiên cứu cần đồng bộ lịch phù hợp "
        "với từng phương pháp thay vì mặc định "
        "mọi giá trị thiếu bằng 0.",
        "gold",
    )

    section(
        "Kiểm tra chất lượng dữ liệu",
        "Các bảng đầu ra của bước tiền xử lý.",
    )

    show_table(
        DATA["quality"],
        "Báo cáo chất lượng dữ liệu",
    )

    show_table(
        DATA["descriptive"],
        "Thống kê mô tả",
    )

    section(
        "Từ điển thuật ngữ",
        "Đọc kết quả mà không cần biết "
        "trước toàn bộ phương pháp kinh tế lượng.",
    )

    glossary = [
        (
            "Hệ số âm và dương",
            "Hệ số âm cho thấy mối liên hệ ngược chiều; "
            "hệ số dương cho thấy mối liên hệ cùng chiều. "
            "Chiều hệ số không tự động chứng minh nhân quả.",
        ),
        (
            "Số ngày sau biến động",
            "Ngày 0 là cùng thời điểm; các ngày tiếp theo "
            "là các thời điểm tiếp theo. "
            "LP và VAR có thể dùng đơn vị thời gian khác nhau.",
        ),
        (
            "Khoảng tin cậy",
            "Thể hiện mức độ bất định của ước lượng. "
            "Nếu khoảng tin cậy chứa 0, chưa đủ "
            "bằng chứng rằng hệ số khác 0 "
            "theo kiểm định tương ứng.",
        ),
        (
            "p-value",
            "Dùng để đánh giá bằng chứng thống kê "
            "trong một kiểm định. "
            "Không phải xác suất giả thuyết đúng.",
        ),
        (
            "q-value FDR",
            "Giá trị kiểm định sau điều chỉnh "
            "nhiều giả thuyết. "
            "Giúp hạn chế kết luận dương tính giả "
            "khi kiểm tra nhiều hệ số.",
        ),
        (
            "VAR và IRF",
            "VAR mô tả tương tác động giữa nhiều biến. "
            "IRF thể hiện phản ứng ước lượng "
            "trước một đổi mới trong hệ thống.",
        ),
        (
            "Local Projections",
            "Ước lượng riêng hệ số tại từng chân trời "
            "thời gian để mô tả đường phản ứng động.",
        ),
        (
            "Calm và Stress",
            "Hai trạng thái thị trường được phân loại "
            "theo VIX phiên trước, với ngưỡng Stress là 30.",
        ),
        (
            "MAE và RMSE",
            "Hai thước đo sai số dự báo. "
            "Cả hai càng thấp càng tốt; RMSE "
            "nhạy hơn với các sai số lớn.",
        ),
        (
            "Block bootstrap",
            "Phương pháp lấy mẫu lại theo các khối "
            "thời gian nhằm đánh giá độ bất định "
            "của chênh lệch sai số dự báo.",
        ),
    ]

    for title, description in glossary:
        insight(
            "GIẢI THÍCH THUẬT NGỮ",
            title,
            description,
            "white",
        )

    section(
        "Các file dữ liệu dashboard đang đọc",
        "Kiểm tra nhanh file CSV nào đã có "
        "và file nào đang thiếu.",
    )

    rows = []

    for key, (filename, folder) in FILES.items():
        path = folder / filename

        rows.append(
            {
                "dataset": key,
                "filename": filename,
                "status": (
                    "Có dữ liệu"
                    if not DATA[key].empty
                    else "Thiếu hoặc rỗng"
                ),
                "rows": len(DATA[key]),
                "path": str(path.relative_to(ROOT)),
            }
        )

    status_df = pd.DataFrame(rows)

    show_table(
        status_df,
        "Tình trạng các file CSV",
    )

    missing = status_df[
        status_df["status"] == "Thiếu hoặc rỗng"
    ]

    if not missing.empty:
        st.warning(
            f"Có {len(missing)} file chưa đọc được "
            "hoặc không có dữ liệu. "
            "Các biểu đồ phụ thuộc vào chúng "
            "có thể không hiển thị."
        )
    else:
        st.success(
            "Tất cả các file CSV được khai báo "
            "đều đã đọc được."
        )

    answer(
        "PHƯƠNG PHÁP",
        "Dashboard trình bày bằng chứng, "
        "không tự tạo ra kết quả mô hình mới.",
        "Các biểu đồ được xây dựng từ CSV "
        "đã xuất bởi pipeline nghiên cứu. "
        "Mỗi kết luận cần được đọc cùng với "
        "đơn vị biến, khoảng tin cậy, kiểm định "
        "và giới hạn phương pháp. "
        "Đặc biệt, liên hệ thống kê "
        "không đồng nghĩa quan hệ nhân quả.",
    )




# ============================================================
# 15. KẾT LUẬN & ỨNG DỤNG — từ Chương 05 của paper
# ============================================================

elif PAGE == "final_conclusion":
    hero(
        "RESEARCH CONCLUSION · 2018–2025",
        "Kết luận <em>& ứng dụng</em>",
        "Tổng hợp năm câu hỏi nghiên cứu từ Chương 05: mối liên hệ, phản ứng động, "
        "khác biệt giai đoạn/trạng thái và giá trị dự báo ngoài mẫu.",
    )

    section("Nhóm đang nghiên cứu điều gì?", "Đọc 60 giây để hiểu bài, không cần mở báo cáo.")
    insight("BÀI TOÁN", "Khi USD mạnh lên, lãi suất hoặc lo ngại rủi ro thay đổi, Bitcoin và Ethereum phản ứng thế nào?",
            "Nhóm theo dõi BTC và ETH trong 2018–2025, đối chiếu với ba thước đo tài chính toàn cầu: VIX (rủi ro), DXY (sức mạnh USD) và US2Y (lợi suất trái phiếu Mỹ 2 năm). Không chỉ hỏi hai thị trường có liên hệ không, nhóm còn hỏi liệu liên hệ ấy có dùng để dự báo ngày mai hay không.", "violet")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Tài sản số", "2", "BTC và ETH", "violet")
    with c2: kpi("Nhân tố vĩ mô", "3", "VIX, DXY, US2Y", "coral")
    with c3: kpi("Thời gian", "2018–25", "Dữ liệu lịch sử", "teal")
    with c4: kpi("Dự báo kiểm tra", "2025", "365 ngày ngoài mẫu", "gold")

    section("5 bước nhóm đã thực hiện", "Từ đặt câu hỏi đến kiểm tra ứng dụng thật.")
    insight("BƯỚC 1 · RQ1", "Tìm mối liên hệ", "Ước lượng Local Projections để xem lợi suất BTC/ETH liên hệ với biến động VIX, DXY, US2Y tại ngày đầu và các ngày sau. Dùng khoảng tin cậy và BH-FDR để tránh đọc nhầm những tín hiệu ngẫu nhiên.", "violet")
    insight("BƯỚC 2 · RQ2", "Xem phản ứng kéo dài bao lâu", "Đối chiếu đường LP với phản ứng động VAR(5). Chú ý phản ứng ngay thời điểm đầu so với các ngày/phiên tiếp theo, không gán kết quả này cho từng năm lịch.", "teal")
    insight("BƯỚC 3 · RQ3", "Kiểm tra trước và sau 2020", "Đặt 2018–2019 cạnh 2020–2025 và kiểm định trực tiếp chênh lệch hệ số. Xem thêm rolling 252 phiên theo trục năm để hiểu hệ số biến thiên liên tục.", "coral")
    insight("BƯỚC 4 · RQ4", "Kiểm tra khi thị trường căng thẳng", "Phân loại Calm/Stress theo VIX phiên trước (Stress khi VIX ≥ 30), rồi xem quan hệ vĩ mô–crypto có thay đổi đủ rõ về thống kê hay không.", "gold")
    insight("BƯỚC 5 · RQ5", "Kiểm tra liệu Macro có giúp dự báo", "Cho Elastic Net và XGBoost dự báo độ lớn lợi suất ngày tiếp theo. So sánh bộ chỉ có dữ liệu crypto với bộ bổ sung vĩ mô trên năm 2025 chưa dùng huấn luyện; đối chiếu benchmark lịch sử 30 ngày.", "violet")

    section("3 phát hiện người xem cần nhớ", "Những kết luận có thể rút ra mà không cần hiểu hết công thức.")
    insight("PHÁT HIỆN 01", "Rủi ro tăng hoặc USD mạnh thường đi kèm lợi suất crypto yếu hơn trong cùng ngày.", "Đây là mối liên hệ có điều kiện trong mẫu, không phải dự báo chắc chắn ngày tiếp theo và không chứng minh quan hệ nhân quả.", "coral")
    insight("PHÁT HIỆN 02", "Chưa xác nhận thay đổi hệ số có hệ thống sau 2020 hoặc khi VIX cao.", "RQ3 và RQ4 đều có 0/186 kiểm định chênh lệch đạt BH-FDR 5%. Không tìm thấy bằng chứng đủ mạnh KHÔNG có nghĩa hai giai đoạn hay trạng thái giống hệt nhau.", "gold")
    insight("PHÁT HIỆN 03", "Biết bối cảnh không đồng nghĩa dự báo tốt hơn.", "Các biến vĩ mô có thể hữu ích để theo dõi rủi ro, nhưng bổ sung chúng không mang lại cải thiện dự báo ngoài mẫu ổn định cho BTC/ETH trong thiết kế kiểm tra năm 2025.", "teal")

    section("Bằng chứng trực quan", "Đối chiếu biểu đồ gốc để tự kiểm tra câu chuyện nghiên cứu.")
    original_figure("rolling_sensitivity.png", "Hệ số rolling 252 phiên biến động qua 2019–2025; đây là quan sát mô tả, không thay thế kiểm định chênh lệch.")
    original_figure("forecast_comparison.png", "Năm 2025: các mô hình bám xu hướng độ lớn lợi suất nhưng khó bắt trọn các ngày biến động cực đoan.")

    section("Ứng dụng thế nào cho đúng?", "Ba tình huống gần với quyết định thực tế.")
    insight("NẾU BẠN LÀ NHÀ ĐẦU TƯ", "Thấy VIX tăng không có nghĩa phải bán BTC ngay.", "Dùng VIX/DXY như tín hiệu cảnh báo bối cảnh, kết hợp thanh khoản, biến động và giới hạn rủi ro; nghiên cứu không kiểm định chiến lược mua bán sau phí.", "violet")
    insight("NẾU BẠN QUẢN TRỊ RỦI RO", "Xây dựng kịch bản thay vì tin vào một hệ số cố định.", "Đặt các kịch bản USD mạnh lên, bất ổn tăng, lãi suất thay đổi; đánh giá danh mục BTC/ETH theo mức chịu lỗ, không mặc định Stress sẽ tạo hệ số khác có ý nghĩa.", "teal")
    insight("NẾU BẠN XÂY DỰNG MÔ HÌNH", "Thêm biến mới phải chứng minh giảm lỗi trên dữ liệu chưa thấy.", "Đặt benchmark đơn giản trước, sau đó kiểm tra MAE/RMSE, độ ổn định qua thời gian và thời điểm dữ liệu thực sự có sẵn; không chọn mô hình chỉ vì có nhiều biến.", "coral")

    section("Thông điệp trung tâm", "Kết luận tổng hợp dựa trên Chương 05 của bài nghiên cứu.")
    insight(
        "KẾT LUẬN CHÍNH",
        "VIX và DXY có liên hệ âm cùng ngày với BTC/ETH — nhưng chưa đủ để dự báo tốt hơn.",
        "Trong mẫu 2018–2025, VIX và DXY có hệ số âm cùng ngày và vẫn có ý nghĩa sau "
        "điều chỉnh BH-FDR 5%. Bằng chứng về US2Y yếu hơn. Phản ứng ở các ngày sau "
        "không ổn định; chưa xác nhận khác biệt có hệ thống giữa hai giai đoạn hoặc "
        "giữa Calm và Stress; thêm biến vĩ mô cũng chưa cải thiện dự báo ngoài mẫu "
        "một cách nhất quán.",
        "teal",
    )

    section("Kết quả theo 5 câu hỏi nghiên cứu", "Đọc kết luận theo đúng trình tự RQ1 → RQ5.")
    insight(
        "RQ1 · MỐI LIÊN HỆ CÙNG NGÀY",
        "VIX và DXY: liên hệ âm có ý nghĩa thống kê; US2Y: chưa đủ bằng chứng.",
        "LP cùng ngày: VIX → BTC −0,5725, ETH −0,7824; DXY → BTC −0,8489, "
        "ETH −0,9866. Cả bốn hệ số đạt BH-FDR 5%. US2Y → BTC −2,3639 "
        "(q = 0,8634), ETH −2,7575 (q = 0,8358): không đạt FDR. "
        "Đây là liên hệ thống kê có điều kiện, không phải tác động nhân quả đã nhận diện.",
        "coral",
    )
    insight(
        "RQ2 · PHẢN ỨNG ĐỘNG",
        "Bằng chứng rõ nhất xuất hiện cùng ngày; phản ứng kéo dài không ổn định.",
        "LP và VAR(5)/IRF đều cho thấy phản ứng ban đầu âm nổi bật với VIX/DXY. "
        "Ở những ngày hoặc phiên sau, dấu và độ lớn thay đổi, nhiều khoảng tin cậy "
        "chứa 0. IRF Cholesky phụ thuộc thứ tự biến và khác LP về đơn vị phản ứng; "
        "không diễn giải các đường này như quan hệ nhân quả chắc chắn.",
        "violet",
    )
    insight(
        "RQ3 · TRƯỚC VÀ SAU 2020",
        "Chưa xác nhận thay đổi có hệ thống giữa 2018–2019 và 2020–2025.",
        "Trong 186 kiểm định chênh lệch, 20 kiểm định đạt p < 0,05 trước điều chỉnh "
        "nhưng 0 kiểm định còn ý nghĩa sau BH-FDR 5%. Việc chưa phát hiện khác biệt "
        "không chứng minh hai giai đoạn giống hệt nhau; giai đoạn 2018–2019 ngắn hơn.",
        "gold",
    )
    insight(
        "RQ4 · CALM VÀ STRESS",
        "Chưa xác nhận hệ số truyền dẫn khác nhau theo trạng thái thị trường.",
        "Stress được xác định bằng VIX phiên trước ≥ 30. Có 1.839 quan sát Calm "
        "và 151 Stress. Trong 186 kiểm định, 13 có p < 0,05 trước điều chỉnh "
        "nhưng 0 còn ý nghĩa sau FDR. Kiểm tra ngưỡng 25/35 cũng không cho "
        "khác biệt bền vững sau FDR. Mất cân đối cỡ mẫu là một giới hạn quan trọng.",
        "teal",
    )
    insight(
        "RQ5 · DỰ BÁO NGOÀI MẪU 2025",
        "Thêm VIX, DXY, US2Y không cải thiện dự báo nhất quán.",
        "Dự báo trị tuyệt đối lợi suất log ngày tiếp theo trên 365 ngày năm 2025. "
        "Với BTC, Elastic Net thêm macro làm MAE tăng từ 1,1309 lên 1,1643; "
        "chênh lệch cải thiện = −0,0334, khoảng tin cậy bootstrap 95% "
        "[−0,0597; −0,0068]. Với ETH, một số cải thiện nhỏ không có ý nghĩa "
        "thống kê theo bootstrap. Giá trị giải thích không đồng nghĩa giá trị dự báo.",
        "coral",
    )

    section("Hàm ý thực tiễn", "Cách sử dụng kết quả mà không suy diễn quá mức.")
    insight(
        "DÀNH CHO NHÀ ĐẦU TƯ",
        "Dùng VIX và DXY để quan sát bối cảnh rủi ro, không dùng riêng để mua/bán.",
        "VIX tăng và USD mạnh lên có thể đồng hành với môi trường bất lợi cho "
        "crypto trong dữ liệu nghiên cứu. Tuy nhiên, liên hệ cùng ngày không bảo đảm "
        "hướng giá ngày mai và chưa tạo thành chiến lược giao dịch đã kiểm định sau phí.",
        "violet",
    )
    insight(
        "DÀNH CHO QUẢN TRỊ DANH MỤC",
        "Sử dụng kịch bản và stress testing thay vì cố định một hệ số rủi ro.",
        "Kết hợp thông tin VIX/DXY với biến động, thanh khoản, tương quan và "
        "mức sụt giảm của BTC/ETH. Không giả định hệ số tăng theo tỷ lệ cố định "
        "khi VIX vượt 30 vì RQ4 chưa xác nhận khác biệt sau FDR.",
        "teal",
    )
    insight(
        "DÀNH CHO PHÁT TRIỂN MÔ HÌNH",
        "Chỉ bổ sung macro nếu kiểm định ngoài mẫu chứng minh lợi ích ổn định.",
        "So sánh MAE, RMSE, khoảng tin cậy bootstrap và benchmark đơn giản; "
        "kiểm tra độ trễ công bố, nguy cơ rò rỉ dữ liệu và hiệu quả qua nhiều giai đoạn. "
        "Feature importance không thay thế đánh giá giá trị dự báo tăng thêm.",
        "gold",
    )

    section("Giới hạn nghiên cứu", "Những điều cần nhớ trước khi áp dụng kết quả.")
    method_note(
        "Giới hạn của bằng chứng",
        "Mẫu chỉ gồm BTC, ETH, VIX, DXY, US2Y giai đoạn 2018–2025; "
        "crypto giao dịch 24/7 trong khi biến vĩ mô theo lịch phiên. "
        "LP và VAR/IRF không nhận diện cú sốc nhân quả ngoại sinh. "
        "Mốc chia 2020 và ngưỡng VIX 30 là quy ước; mẫu Stress nhỏ. "
        "ML chỉ kiểm tra một năm 2025 và mục tiêu độ lớn lợi suất ngày tiếp theo, "
        "không phải mọi thước đo biến động hay rủi ro đuôi.",
    )

    section("Hướng nghiên cứu tiếp theo", "Mở rộng kiểm định, không khẳng định vượt quá dữ liệu hiện tại.")
    insight(
        "PHÁT TRIỂN NGHIÊN CỨU",
        "Mở rộng dữ liệu, nhận diện cú sốc và kiểm định dự báo trên nhiều giai đoạn.",
        "Có thể bổ sung tài sản crypto, thước đo thanh khoản/tín dụng, điểm gãy "
        "cấu trúc từ dữ liệu và cách phân loại trạng thái khác. Nghiên cứu tiếp theo "
        "nên dùng cú sốc chính sách tần suất cao nếu muốn tiếp cận nhân quả, "
        "kiểm tra nhiều thứ tự Cholesky, và dự báo thêm realized volatility, "
        "VaR, Expected Shortfall với nhiều tập ngoài mẫu.",
        "violet",
    )
    answer(
        "KẾT LUẬN",
        "Có liên hệ thống kê, nhưng chưa đủ bằng chứng về tính ổn định hoặc lợi ích dự báo tăng thêm.",
        "VIX và DXY hữu ích như chỉ báo bối cảnh để quản trị rủi ro và xây dựng "
        "kịch bản. Chúng không phải tín hiệu giao dịch độc lập. "
        "Kết quả cần được kiểm chứng thêm trước khi ứng dụng dự báo thực tế.",
    )
    st.caption("Nguồn nội dung: 05_discussion_conclusion_formatted_revised.docx · Mục 5.1–5.7. "
               "Các con số được giữ theo tài liệu; dashboard không ước lượng lại mô hình.")


# ============================================================
# ============================================================
# 15. FOOTER
# ============================================================

st.divider()

st.caption(
    "MACRO × CRYPTO INTELLIGENCE · 2018–2025 · "
    "Research Dashboard · "
    "Kết quả mang mục đích nghiên cứu học thuật, "
    "không phải khuyến nghị đầu tư."
)
