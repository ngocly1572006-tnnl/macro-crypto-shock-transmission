
# ============================================================
# MACRO × CRYPTO INTELLIGENCE
# COMPLETE RESEARCH DASHBOARD — VERSION 3
# Plum / Coral / Teal / Champagne
# ============================================================

from pathlib import Path
import html
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 01. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Macro × Crypto Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "model_results"
TABLES = ROOT / "outputs" / "tables"

C = {
    "plum": "#503A55",
    "plum_dark": "#382A3F",
    "coral": "#DA7774",
    "teal": "#25877E",
    "violet": "#9572BA",
    "gold": "#D3A15B",
    "ink": "#392E3F",
    "muted": "#756678",
    "bg": "#F3EDF1",
    "white": "#FFFFFF",
}

RQ = {
    "RQ1": (
        "Các cú sốc tài chính toàn cầu truyền dẫn đến lợi suất "
        "Bitcoin và Ethereum như thế nào?"
    ),
    "RQ2": (
        "Phản ứng của Bitcoin và Ethereum trước các cú sốc "
        "tài chính toàn cầu diễn biến như thế nào theo thời gian?"
    ),
    "RQ3": (
        "Mối quan hệ truyền dẫn giữa điều kiện tài chính toàn cầu "
        "và thị trường tiền mã hóa có thay đổi giữa giai đoạn "
        "trước và sau năm 2020 không?"
    ),
    "RQ4": (
        "Mức độ truyền dẫn của các cú sốc tài chính toàn cầu "
        "đến Bitcoin và Ethereum có khác nhau giữa trạng thái "
        "bình ổn (Calm) và căng thẳng (Stress) không?"
    ),
    "RQ5": (
        "Việc bổ sung các biến tài chính vĩ mô có cải thiện "
        "khả năng dự báo độ lớn lợi suất ngày tiếp theo của "
        "Bitcoin và Ethereum so với mô hình chỉ sử dụng "
        "dữ liệu tiền mã hóa không?"
    ),
}

SHOCK_LABELS = {
    "VIX": "VIX · Chỉ số bất định thị trường",
    "DXY": "DXY · Sức mạnh đồng USD",
    "US2Y": "US2Y · Lợi suất TPCP Mỹ 2 năm",
}

PAGES = {
    "🏠 Tổng quan nghiên cứu": "overview",
    "💌 RQ1 · Truyền dẫn cú sốc": "rq1",
    "📈 RQ2 · Phản ứng động": "rq2",
    "🔄 RQ3 · Trước/sau 2020": "rq3",
    "🛡️ RQ4 · Calm/Stress": "rq4",
    "🧠 RQ5 · Dự báo ML": "rq5",
    "📚 Dữ liệu & phương pháp": "methods",
}


# ============================================================
# 02. GLOBAL CSS — ONE SINGLE STYLE BLOCK
# ============================================================

CSS = """
<style>
:root {
    color-scheme: light;
    --plum: #503A55;
    --coral: #DA7774;
    --teal: #25877E;
    --violet: #9572BA;
    --gold: #D3A15B;
    --ink: #392E3F;
}

.stApp {
    background: #F3EDF1 !important;
    color: #392E3F !important;
}

[data-testid="stHeader"] {
    background: #F3EDF1 !important;
}

.block-container {
    max-width: 1500px !important;
    padding-top: 4.5rem !important;
    padding-bottom: 3.5rem !important;
}

.stApp h1,
.stApp h2,
.stApp h3 {
    color: #392E3F !important;
    font-weight: 900 !important;
}

.stApp p {
    font-size: 15px;
    line-height: 1.75;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg, #503A55 0%, #382A3F 100%
    ) !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #F6EBF3 !important;
    font-size: 14px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 12px 12px !important;
    border-radius: 12px;
    margin: 4px 0;
}

[data-testid="stSidebar"]
[role="radiogroup"] label:has(input:checked) {
    background: #DA7774 !important;
}

[data-testid="stSidebar"]
[role="radiogroup"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 900 !important;
}

.brand {
    background: linear-gradient(
        135deg, #77577E, #A06C88
    );
    border: 1px solid #AE88A3;
    border-radius: 19px;
    padding: 24px 19px;
    margin-bottom: 23px;
}

.brand-title {
    color: white !important;
    font-size: 24px;
    font-weight: 950;
    letter-spacing: -.6px;
}

.brand-sub {
    color: #FFE6EE !important;
    font-size: 12px;
    font-weight: 750;
    margin-top: 9px;
}

.side-note {
    background: #624B68;
    border: 1px solid #816989;
    border-radius: 15px;
    padding: 19px;
    color: #F6EDF4;
    font-size: 13px;
    font-weight: 550;
    line-height: 2;
}

.side-note strong {
    color: #FFD1B7;
    font-size: 13px;
}

/* ============================================================
   HERO — FULLY ROUNDED / LARGE TYPOGRAPHY
   ============================================================ */

.hero {
    position: relative;
    isolation: isolate;
    overflow: hidden;

    background: linear-gradient(
        112deg,
        #503A55 0%,
        #705173 61%,
        #A16D87 100%
    );

    padding: 39px 42px;
    border-radius: 25px !important;

    margin-top: 18px;
    margin-bottom: 27px;

    box-shadow: 0 13px 32px rgba(69,42,74,.14);
}

/* Subtle concentric circles instead of a giant star */

.hero::after {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    right: -57px;
    top: -75px;
    border-radius: 50%;
    border: 1px solid rgba(255,218,204,.24);
    box-shadow:
        0 0 0 32px rgba(255,218,204,.052),
        0 0 0 68px rgba(255,218,204,.032),
        0 0 0 105px rgba(255,218,204,.016);
    pointer-events: none;
    z-index: -1;
}

.hero-tag {
    color: #FFD0B7 !important;
    font-size: 13px;
    font-weight: 950;
    letter-spacing: 2px;
}

.hero-title {
    color: #FFFFFF !important;
    font-size: clamp(37px, 3.5vw, 53px);
    font-weight: 950;
    letter-spacing: -1.5px;
    line-height: 1.23;
    margin: 15px 0 13px;
    max-width: 940px;
}

.hero-title em {
    color: #FFC7A9;
    font-style: normal;
}

.hero-desc {
    color: #F8EDF5 !important;
    font-size: 17px;
    font-weight: 650;
    line-height: 1.8;
    max-width: 900px;
}

/* ============================================================
   SECTION HEADINGS
   ============================================================ */

.section-head {
    margin: 34px 0 18px;
}

.section-eyebrow {
    color: #B65B67 !important;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.6px;
}

.section-title {
    color: #392E3F !important;
    font-size: 29px;
    font-weight: 950;
    letter-spacing: -.6px;
    margin-top: 7px;
}

.section-sub {
    color: #6F6073 !important;
    font-size: 16px;
    font-weight: 550;
    margin-top: 8px;
    line-height: 1.75;
}

/* ============================================================
   RESEARCH QUESTION CARD
   ============================================================ */

.question {
    background: #FFFFFF;
    border: 1px solid #E3D5E1;
    border-left: 6px solid #DA7774;
    border-radius: 17px;
    padding: 25px 28px;
    margin: 17px 0 25px;
    box-shadow: 0 5px 18px rgba(60,40,65,.04);
}

.question-tag {
    color: #B65B67 !important;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.4px;
}

.question-text {
    color: #392E3F !important;
    font-size: 21px;
    font-weight: 850;
    line-height: 1.75;
    margin-top: 10px;
}

/* ============================================================
   KPI CARDS
   ============================================================ */

.kpi {
    background: #FFFFFF;
    border: 1px solid #E4D8E3;
    border-top: 6px solid #DA7774;
    border-radius: 19px;
    padding: 24px 23px;
    min-height: 165px;
    box-shadow: 0 6px 20px rgba(67,43,72,.06);
}

.kpi.coral {border-top-color: #DA7774;}
.kpi.teal {border-top-color: #25877E;}
.kpi.violet {border-top-color: #9572BA;}
.kpi.gold {border-top-color: #D3A15B;}

.kpi-label {
    color: #745E78 !important;
    font-size: 13px;
    font-weight: 950;
    letter-spacing: .8px;
    text-transform: uppercase;
}

.kpi-value {
    color: #503A55 !important;
    font-size: clamp(31px, 2.8vw, 44px);
    font-weight: 950;
    letter-spacing: -1px;
    margin-top: 15px;
}

.kpi-sub {
    color: #6F6174 !important;
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
}

/* ============================================================
   INSIGHT CARDS
   ============================================================ */

.insight {
    border-left: 6px solid #DA7774;
    border-radius: 17px;
    padding: 25px 27px;
    margin: 13px 0 21px;
}

.insight.coral {
    background: #F9E1E1;
    border-left-color: #DA7774;
}

.insight.teal {
    background: #DDEFE9;
    border-left-color: #25877E;
}

.insight.violet {
    background: #EAE1F4;
    border-left-color: #9572BA;
}

.insight.gold {
    background: #F9ECD6;
    border-left-color: #D3A15B;
}

.insight.white {
    background: #FFFFFF;
    border-left-color: #77577E;
}

.insight-tag {
    color: #895368 !important;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.2px;
}

.insight-title {
    color: #392E3F !important;
    font-size: 21px;
    font-weight: 950;
    margin: 11px 0;
    line-height: 1.5;
}

.insight-body {
    color: #4F4253 !important;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.9;
}

/* ============================================================
   SELECTBOX / MULTISELECT — NO DARK BACKGROUND
   ============================================================ */

[data-testid="stSelectbox"] label p,
[data-testid="stMultiSelect"] label p {
    color: #503A55 !important;
    font-size: 16px !important;
    font-weight: 900 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] {
    background: #FFFFFF !important;
    border-radius: 13px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 2px solid #C8AEC8 !important;
    border-radius: 13px !important;
    min-height: 51px !important;
    box-shadow: none !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] span {
    color: #503A55 !important;
    -webkit-text-fill-color: #503A55 !important;
    font-size: 16px !important;
    font-weight: 850 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {
    color: #A06C88 !important;
    fill: #A06C88 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
    background: #FFF8F7 !important;
    border-color: #DA7774 !important;
}

/* Dropdown menu */

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #FFFFFF !important;
    color: #503A55 !important;
}

li[role="option"] {
    background: #FFFFFF !important;
    color: #503A55 !important;
    font-size: 15px !important;
}

li[role="option"] *,
ul[role="listbox"] * {
    color: #503A55 !important;
    -webkit-text-fill-color: #503A55 !important;
}

li[role="option"]:hover,
li[aria-selected="true"] {
    background: #F3E3ED !important;
}

/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E1D3DF !important;
    border-radius: 15px !important;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    background: #F4E9F0 !important;
}

[data-testid="stExpander"] summary p {
    color: #503A55 !important;
    font-size: 15px !important;
    font-weight: 900 !important;
}

/* ============================================================
   COLORFUL TABLES
   ============================================================ */

.table-scroll {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 460px;
    border-radius: 13px;
    border: 1px solid #E3D5E0;
}

.color-table {
    width: 100%;
    min-width: 720px;
    border-collapse: collapse;
    font-size: 14px;
}

.color-table th {
    background: #5F4565;
    color: #FFFFFF;
    padding: 15px;
    text-align: left;
    position: sticky;
    top: 0;
    z-index: 2;
    font-weight: 900;
}

.color-table th:nth-child(4n+2) {
    background: #785A80;
}

.color-table th:nth-child(4n+3) {
    background: #347F79;
}

.color-table th:nth-child(4n+4) {
    background: #BB7079;
}

.color-table td {
    padding: 13px 15px;
    color: #483A4C;
    background: #FFFFFF;
    border-bottom: 1px solid #EDE3EB;
    white-space: nowrap;
    font-size: 14px;
}

.color-table tr:nth-child(even) td {
    background: #F8F1F6;
}

.color-table tr:hover td {
    background: #FBE7E5;
}

.cell-tag {
    display: inline-block;
    background: #E9DCF1;
    color: #674A7B;
    border-radius: 8px;
    padding: 5px 9px;
    font-weight: 900;
}

.cell-pos {
    color: #237E72;
    font-weight: 850;
}

.cell-neg {
    color: #C15E6C;
    font-weight: 850;
}

/* ============================================================
   BUTTONS / MISC
   ============================================================ */

.stButton > button {
    border-radius: 12px !important;
    background: #503A55 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-size: 14px !important;
    font-weight: 900 !important;
}

.stButton > button p {
    color: #FFFFFF !important;
    font-weight: 900 !important;
}

.stCaption,
[data-testid="stCaptionContainer"] p {
    color: #756678 !important;
    font-size: 13px !important;
}

hr {
    border-color: #DDCFDC !important;
}

@media (max-width: 900px) {
    .block-container {
        padding-top: 3.5rem !important;
    }

    .hero {
        padding: 28px 24px;
    }

    .hero-title {
        font-size: 35px;
    }

    .section-title {
        font-size: 25px;
    }

    .insight-title {
        font-size: 19px;
    }
}
</style>
"""

# IMPORTANT: Render CSS once.
# Do not paste CSS elsewhere in the Python file.
st.html(CSS)


# ============================================================
# 03. DATA LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def read_csv(name, folder="model_results"):
    base = RESULTS if folder == "model_results" else TABLES
    path = base / name

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Không đọc được {name}: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_data():
    return {
        "lp": read_csv("lp_results.csv"),
        "lp_fdr": read_csv("lp_fdr.csv"),
        "irf": read_csv("irf_results.csv"),
        "subperiod": read_csv("subperiod_results.csv"),
        "rq3": read_csv("subperiod_difference_fdr.csv"),
        "regime": read_csv("regime_results.csv"),
        "rq4": read_csv("regime_difference_fdr.csv"),
        "regime_diag": read_csv("regime_diagnostics.csv"),
        "comparison": read_csv("model_comparison.csv"),
        "forecast": read_csv("forecast_results.csv"),
        "significance": read_csv("forecast_significance.csv"),
        "importance": read_csv("feature_importance.csv"),
        "quality": read_csv(
            "preprocessing_quality_report.csv",
            "tables",
        ),
        "correlation": read_csv(
            "correlation_matrix.csv",
            "tables",
        ),
        "descriptive": read_csv(
            "descriptive_stats.csv",
            "tables",
        ),
        "var_diag": read_csv("var_lag_diagnostics.csv"),
    }


D = load_data()


# ============================================================
# 04. DATA HELPERS
# ============================================================

def normalize(df):
    if df.empty:
        return df.copy()

    df = df.copy()

    aliases = {
        "response": ["response", "asset", "coin", "target"],
        "shock": ["shock", "impulse", "variable"],
        "horizon": ["horizon", "h", "step"],
        "estimate": ["estimate", "beta", "coefficient"],
        "ci_lower": [
            "ci_lower", "lower_ci", "ci_low",
            "lower", "ci95_lower",
            "ci_lower_95", "ci_low_95",
        ],
        "ci_upper": [
            "ci_upper", "upper_ci", "ci_high",
            "upper", "ci95_upper",
            "ci_upper_95", "ci_high_95",
        ],
        "p_value": ["p_value", "pvalue", "p"],
        "p_value_fdr": [
            "p_value_fdr", "q_value", "p_fdr",
        ],
    }

    rename = {}
    used = set()

    for target, possibilities in aliases.items():
        if target in df.columns:
            continue

        for name in possibilities:
            if name in df.columns and name not in used:
                rename[name] = target
                used.add(name)
                break

    return df.rename(columns=rename)


for key in D:
    D[key] = normalize(D[key])


def filtered(df, **kwargs):
    if df.empty:
        return df.copy()

    result = df.copy()

    for col, value in kwargs.items():
        if col in result.columns and value is not None:
            result = result[
                result[col].astype(str).str.lower()
                == str(value).lower()
            ]

    return result.copy()


def first(df):
    return None if df.empty else df.iloc[0]


def fmt(value, digits=4):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return "N/A"


def safe(value):
    return html.escape(str(value), quote=True)


# ============================================================
# 05. UI HELPERS
# ============================================================

def hero(tag, title, description):
    st.html(
        f"""
<div class="hero">
    <div class="hero-tag">{safe(tag)}</div>
    <div class="hero-title">{title}</div>
    <div class="hero-desc">{safe(description)}</div>
</div>
"""
    )


def section(title, subtitle="", eyebrow="RESEARCH ANALYTICS"):
    st.html(
        f"""
<div class="section-head">
    <div class="section-eyebrow">{safe(eyebrow)}</div>
    <div class="section-title">{safe(title)}</div>
    <div class="section-sub">{safe(subtitle)}</div>
</div>
"""
    )


def question(number):
    st.html(
        f"""
<div class="question">
    <div class="question-tag">
        {number} · CÂU HỎI NGHIÊN CỨU
    </div>
    <div class="question-text">{safe(RQ[number])}</div>
</div>
"""
    )


def kpi(label, value, subtitle="", tone="coral"):
    st.html(
        f"""
<div class="kpi {tone}">
    <div class="kpi-label">{safe(label)}</div>
    <div class="kpi-value">{safe(value)}</div>
    <div class="kpi-sub">{safe(subtitle)}</div>
</div>
"""
    )


def insight(tag, title, body, tone="teal"):
    st.html(
        f"""
<div class="insight {tone}">
    <div class="insight-tag">{safe(tag)}</div>
    <div class="insight-title">{safe(title)}</div>
    <div class="insight-body">{safe(body)}</div>
</div>
"""
    )


def show_table(df, label="📋 Xem dữ liệu chi tiết"):
    with st.expander(label):
        if df.empty:
            st.info("Chưa tìm thấy dữ liệu.")
            return

        display = df.head(100).copy()

        headers = "".join(
            f"<th>{safe(c)}</th>" for c in display.columns
        )

        rows = []

        for _, record in display.iterrows():
            cells = []

            for name, value in record.items():
                if pd.isna(value):
                    text = "—"

                elif str(name).lower() in [
                    "response", "asset", "shock",
                    "period", "regime",
                ]:
                    text = (
                        f'<span class="cell-tag">'
                        f'{safe(value)}</span>'
                    )

                elif isinstance(value, (int, float, np.number)):
                    css = (
                        "cell-pos" if value > 0
                        else "cell-neg" if value < 0
                        else ""
                    )

                    text = (
                        f'<span class="{css}">'
                        f'{fmt(value, 4)}</span>'
                    )

                else:
                    text = safe(value)

                cells.append(f"<td>{text}</td>")

            rows.append("<tr>" + "".join(cells) + "</tr>")

        st.html(
            '<div class="table-scroll">'
            '<table class="color-table">'
            f'<thead><tr>{headers}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>'
            '</table></div>'
        )

        if len(df) > 100:
            st.caption(
                f"Hiển thị 100/{len(df):,} dòng đầu tiên."
            )


# ============================================================
# 06. PLOTLY THEME — HIGH CONTRAST TYPOGRAPHY
# ============================================================

def plot_style(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            color="#392E3F",
            size=16,
        ),
        title_font=dict(
            color="#392E3F",
            size=22,
        ),
        margin=dict(l=50, r=40, t=65, b=65),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(color="#503A55", size=15),
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#D6C6D6",
            font=dict(color="#392E3F", size=14),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#CDBDCD",
        tickfont=dict(color="#503A55", size=14),
        title_font=dict(color="#503A55", size=16),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EDE5EB",
        zeroline=True,
        zerolinecolor="#CDBDCD",
        tickfont=dict(color="#503A55", size=14),
        title_font=dict(color="#503A55", size=16),
    )

    return fig


def chart(fig, key, height=420):
    fig = plot_style(fig, height)

    st.plotly_chart(
        fig,
        width="stretch",
        key=key,
        config={"displaylogo": False},
        theme=None,
    )


def line_chart(
    df,
    key,
    color,
    x="horizon",
    y="estimate",
    x_title="Chân trời phản ứng",
):
    if df.empty or x not in df or y not in df:
        st.info("Chưa có dữ liệu biểu đồ.")
        return

    part = df.copy()
    part[x] = pd.to_numeric(part[x], errors="coerce")
    part[y] = pd.to_numeric(part[y], errors="coerce")
    part = part.dropna(subset=[x, y]).sort_values(x)

    fig = go.Figure()

    if (
        "ci_lower" in part.columns
        and "ci_upper" in part.columns
    ):
        ci = part.copy()

        ci["ci_lower"] = pd.to_numeric(
            ci["ci_lower"], errors="coerce"
        )

        ci["ci_upper"] = pd.to_numeric(
            ci["ci_upper"], errors="coerce"
        )

        ci = ci.dropna(
            subset=["ci_lower", "ci_upper"]
        )

        if not ci.empty:
            xx = ci[x].tolist()

            fig.add_trace(
                go.Scatter(
                    x=xx + xx[::-1],
                    y=(
                        ci["ci_upper"].tolist()
                        + ci["ci_lower"].tolist()[::-1]
                    ),
                    fill="toself",
                    fillcolor="rgba(149,114,186,.17)",
                    line=dict(color="rgba(0,0,0,0)"),
                    hoverinfo="skip",
                    name="Khoảng tin cậy",
                )
            )

    fig.add_trace(
        go.Scatter(
            x=part[x],
            y=part[y],
            mode="lines+markers",
            line=dict(color=color, width=3.5),
            marker=dict(size=7),
            name="Hệ số phản ứng",
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#9E8A9F",
    )

    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title="Hệ số phản ứng")

    chart(fig, key)


def selectors(prefix):
    c1, c2 = st.columns(2)

    with c1:
        asset = st.selectbox(
            "🪙 Chọn tài sản",
            ["BTC", "ETH"],
            key=f"{prefix}_asset",
        )

    with c2:
        shock = st.selectbox(
            "🌐 Chọn cú sốc vĩ mô",
            ["VIX", "DXY", "US2Y"],
            format_func=lambda x: SHOCK_LABELS[x],
            key=f"{prefix}_shock",
        )

    return asset, shock


# ============================================================
# 07. SIDEBAR
# ============================================================

with st.sidebar:
    st.html(
        """
<div class="brand">
    <div class="brand-title">✦ Crypto Insights</div>
    <div class="brand-sub">
        MACRO × CRYPTO RESEARCH DASHBOARD
    </div>
</div>
"""
    )

    selection = st.radio(
        "Điều hướng",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    st.html(
        """
<div class="side-note">
    <strong>THÔNG TIN NGHIÊN CỨU</strong><br>
    Giai đoạn: 2018–2025<br>
    Tài sản: BTC · ETH<br>
    Biến vĩ mô: VIX · DXY · US2Y<br>
    Phương pháp: VAR · LP · ML<br>
    Dự báo ngoài mẫu: 2025
</div>
"""
    )

    if st.button(
        "↻ Làm mới dữ liệu",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()


page = PAGES[selection]


# ============================================================
# 08. OVERVIEW
# ============================================================

if page == "overview":

    hero(
        "GLOBAL FINANCIAL RESEARCH · 2018–2025",
        "Macro <em>× Crypto</em> Intelligence",
        "Phân tích sự truyền dẫn cú sốc tài chính toàn cầu "
        "đến Bitcoin và Ethereum thông qua VAR, "
        "Local Projections và Machine Learning.",
    )

    cols = st.columns(4)

    with cols[0]:
        kpi("Ngày nghiên cứu", "2.922", "Ngày lịch", "coral")

    with cols[1]:
        kpi("Câu hỏi nghiên cứu", "05", "RQ1 đến RQ5", "teal")

    with cols[2]:
        kpi("Biến vĩ mô", "03", "VIX · DXY · US2Y", "violet")

    with cols[3]:
        kpi("Kiểm tra ngoài mẫu", "2025", "365 ngày", "gold")

    section(
        "Khung nghiên cứu",
        "Năm câu hỏi kết nối phân tích truyền dẫn "
        "và giá trị dự báo của dữ liệu vĩ mô.",
        "RESEARCH FRAMEWORK",
    )

    for number in RQ:
        question(number)

    section(
        "Những phát hiện quan trọng",
        "Các kết quả nổi bật cần chú ý khi đọc dashboard.",
        "EXECUTIVE FINDINGS",
    )

    c1, c2 = st.columns(2)

    with c1:
        insight(
            "RQ1 · TRUYỀN DẪN",
            "VIX và DXY liên hệ âm với lợi suất crypto.",
            "Hệ số LP cùng ngày cho thấy mối liên hệ "
            "âm đối với BTC và ETH. Đây là quan hệ "
            "thống kê có điều kiện, không phải bằng chứng "
            "nhân quả chắc chắn.",
            "teal",
        )

        insight(
            "RQ3 · TRƯỚC/SAU 2020",
            "Chưa đủ bằng chứng về thay đổi có hệ thống.",
            "Các kiểm định chênh lệch hệ số không còn "
            "ý nghĩa sau điều chỉnh FDR.",
            "violet",
        )

    with c2:
        insight(
            "RQ4 · CALM/STRESS",
            "Chưa xác nhận khác biệt truyền dẫn theo trạng thái.",
            "Mẫu Stress nhỏ và các kiểm định chênh lệch "
            "không còn ý nghĩa sau FDR.",
            "coral",
        )

        insight(
            "RQ5 · MACHINE LEARNING",
            "Macro không cải thiện dự báo một cách nhất quán.",
            "Bổ sung dữ liệu vĩ mô không tạo ra cải thiện "
            "MAE có ý nghĩa thống kê ổn định ngoài mẫu.",
            "gold",
        )

    section(
        "Tương quan giữa các biến",
        "Tương quan mô tả không đồng nghĩa quan hệ nhân quả.",
    )

    corr = D["correlation"]

    if not corr.empty:
        temp = corr.copy()

        try:
            temp = temp.set_index(temp.columns[0])
            temp = temp.apply(
                pd.to_numeric,
                errors="coerce",
            )

            fig = go.Figure(
                go.Heatmap(
                    z=temp.values,
                    x=temp.columns.tolist(),
                    y=temp.index.tolist(),
                    zmin=-1,
                    zmax=1,
                    colorscale=[
                        [0, "#DA7774"],
                        [0.5, "#FFF8F2"],
                        [1, "#25877E"],
                    ],
                    text=np.round(temp.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(
                        color="#392E3F",
                        size=14,
                    ),
                )
            )

            chart(fig, "overview_heatmap", 450)

        except Exception:
            st.info("Chưa thể dựng heatmap từ bảng tương quan.")

    else:
        st.info("Chưa tìm thấy correlation_matrix.csv.")

    show_table(corr, "📋 Xem dữ liệu tương quan")


# ============================================================
# 09. RQ1 — TRANSMISSION
# ============================================================

elif page == "rq1":

    hero(
        "RESEARCH QUESTION 01",
        "RQ1 · <em>Truyền dẫn cú sốc</em>",
        "Đánh giá chiều hướng và độ lớn mối liên hệ "
        "giữa các cú sốc vĩ mô và lợi suất BTC, ETH.",
    )

    question("RQ1")

    insight(
        "PHƯƠNG PHÁP",
        "Local Projections tại h = 0",
        "Hệ số h = 0 phản ánh mối liên hệ cùng ngày. "
        "VIX, DXY và US2Y có đơn vị khác nhau nên "
        "không so sánh trực tiếp trị tuyệt đối hệ số "
        "để kết luận cú sốc nào mạnh nhất.",
        "violet",
    )

    asset, shock = selectors("rq1")

    lp = (
        D["lp_fdr"]
        if not D["lp_fdr"].empty
        else D["lp"]
    )

    current = filtered(
        lp,
        response=asset,
        shock=shock,
        horizon=0,
    )

    row = first(current)

    if row is not None:
        beta = row.get("estimate", np.nan)
        lower = row.get("ci_lower", np.nan)
        upper = row.get("ci_upper", np.nan)
        p = row.get("p_value", np.nan)
        q = row.get("p_value_fdr", np.nan)

        section(
            "Hệ số truyền dẫn cùng ngày",
            f"{asset} · {SHOCK_LABELS[shock]}",
        )

        a, b, c = st.columns(3)

        with a:
            kpi(
                "Hệ số h = 0",
                fmt(beta),
                f"{asset} · {shock}",
                "coral",
            )

        with b:
            kpi(
                "Cận dưới CI 95%",
                fmt(lower),
                "Khoảng tin cậy",
                "teal",
            )

        with c:
            kpi(
                "Cận trên CI 95%",
                fmt(upper),
                "Khoảng tin cậy",
                "violet",
            )

        if pd.notna(beta):
            direction = "giảm" if beta < 0 else "tăng"

            insight(
                "GIẢI THÍCH KINH TẾ",
                f"Lợi suất {asset} có mối liên hệ "
                f"{direction} với cú sốc {shock}.",
                f"Hệ số ước lượng là {fmt(beta)}. "
                f"p-value = {fmt(p)}, "
                f"q-value FDR = {fmt(q)}. "
                "Cần diễn giải theo đơn vị của biến "
                "và giả định mô hình; không mặc định "
                "đây là tác động nhân quả.",
                "teal",
            )

        if pd.notna(q):
            significant = float(q) < 0.05

            insight(
                "KẾT QUẢ KIỂM ĐỊNH FDR",
                (
                    "Có ý nghĩa thống kê sau FDR."
                    if significant
                    else "Chưa có ý nghĩa thống kê sau FDR."
                ),
                "Điều chỉnh Benjamini–Hochberg giúp "
                "kiểm soát phát hiện dương tính giả "
                "khi thực hiện nhiều kiểm định.",
                "gold",
            )

    else:
        st.warning("Không tìm thấy hệ số LP h = 0.")

    section(
        "So sánh BTC và ETH",
        "Hệ số cùng ngày theo từng biến vĩ mô.",
    )

    all_h0 = filtered(lp, horizon=0)

    if not all_h0.empty:
        fig = go.Figure()

        for coin, color in [
            ("BTC", C["teal"]),
            ("ETH", C["coral"]),
        ]:
            part = filtered(all_h0, response=coin)

            fig.add_trace(
                go.Bar(
                    x=part["shock"],
                    y=part["estimate"],
                    name=coin,
                    marker_color=color,
                    text=part["estimate"].round(3),
                    textposition="outside",
                )
            )

        fig.update_layout(barmode="group")
        fig.update_yaxes(title="Hệ số LP h = 0")

        chart(fig, "rq1_comparison")

    show_table(all_h0, "📋 Hệ số LP cùng ngày")


# ============================================================
# 10. RQ2 — DYNAMIC RESPONSES
# ============================================================

elif page == "rq2":

    hero(
        "RESEARCH QUESTION 02",
        "RQ2 · <em>Phản ứng động</em>",
        "Theo dõi phản ứng lợi suất crypto qua các "
        "chân trời sau cú sốc tài chính toàn cầu.",
    )

    question("RQ2")

    asset, shock = selectors("rq2")

    section(
        "Local Projections",
        "Đường phản ứng theo ngày lịch.",
    )

    lp = filtered(
        D["lp"],
        response=asset,
        shock=shock,
    )

    line_chart(
        lp,
        "rq2_lp",
        C["coral"],
        x_title="Chân trời h · Ngày lịch",
    )

    insight(
        "CÁCH ĐỌC",
        "Mỗi chân trời là phản ứng lợi suất "
        "của một ngày riêng biệt.",
        "LP trong nghiên cứu không trực tiếp "
        "ước lượng lợi suất tích lũy. "
        "Vì vậy không cộng các hệ số "
        "để diễn giải thành tổng lợi suất.",
        "teal",
    )

    section(
        "VAR(5) · Impulse Response",
        "Hàm phản ứng xung lực theo phiên vĩ mô.",
    )

    irf = filtered(
        D["irf"],
        response=asset,
        shock=shock,
    )

    line_chart(
        irf,
        "rq2_irf",
        C["violet"],
        x_title="Chân trời · Phiên vĩ mô",
    )

    insight(
        "LƯU Ý PHƯƠNG PHÁP",
        "Không so sánh trực tiếp độ lớn VAR và LP.",
        "VAR sử dụng cú sốc trực giao hóa Cholesky "
        "và chân trời phiên vĩ mô; LP sử dụng "
        "đơn vị cú sốc gốc và chân trời ngày lịch. "
        "Hai cách ước lượng bổ trợ nhau nhưng "
        "không có cùng thang đo.",
        "gold",
    )

    show_table(lp, "📋 Dữ liệu LP")
    show_table(irf, "📋 Dữ liệu VAR IRF")


# ============================================================
# 11. RQ3 — PRE / POST 2020
# ============================================================

elif page == "rq3":

    hero(
        "RESEARCH QUESTION 03",
        "RQ3 · <em>Trước và sau 2020</em>",
        "Kiểm tra sự thay đổi của hệ số truyền dẫn "
        "giữa hai giai đoạn nghiên cứu.",
    )

    question("RQ3")

    asset, shock = selectors("rq3")

    df = filtered(
        D["rq3"],
        response=asset,
        shock=shock,
    )

    row = first(filtered(df, horizon=0))

    if row is not None:
        section(
            "So sánh hệ số h = 0",
            f"{asset} · {SHOCK_LABELS[shock]}",
        )

        a, b, c = st.columns(3)

        with a:
            kpi(
                "Trước 2020",
                fmt(row.get("pre_beta")),
                "2018–2019",
                "violet",
            )

        with b:
            kpi(
                "Sau 2020",
                fmt(row.get("post_beta")),
                "2020–2025",
                "coral",
            )

        with c:
            kpi(
                "Chênh lệch",
                fmt(row.get("difference")),
                "Sau trừ trước",
                "teal",
            )

        insight(
            "KIỂM ĐỊNH",
            "Khác biệt hệ số cần được kiểm định.",
            "p-value chênh lệch = "
            f"{fmt(row.get('difference_p_value'))}; "
            "q-value FDR = "
            f"{fmt(row.get('p_value_fdr'))}. "
            "Hệ số thay đổi về độ lớn chưa đủ "
            "để khẳng định điểm gãy cấu trúc.",
            "gold",
        )

    section(
        "Đường phản ứng theo giai đoạn",
        "So sánh LP trước và sau 2020.",
    )

    sub = filtered(
        D["subperiod"],
        response=asset,
        shock=shock,
    )

    if not sub.empty:
        fig = go.Figure()

        for period, color in [
            ("pre_2020", C["violet"]),
            ("post_2020", C["coral"]),
        ]:
            part = filtered(sub, period=period)
            part = part.sort_values("horizon")

            fig.add_trace(
                go.Scatter(
                    x=part["horizon"],
                    y=part["estimate"],
                    mode="lines+markers",
                    name=period,
                    line=dict(color=color, width=3.5),
                )
            )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#9E8A9F",
        )

        fig.update_xaxes(title="Chân trời ngày lịch")
        fig.update_yaxes(title="Hệ số LP")

        chart(fig, "rq3_period_chart")

    insight(
        "KẾT LUẬN RQ3",
        "Chưa đủ bằng chứng về thay đổi truyền dẫn "
        "mang tính hệ thống sau năm 2020.",
        "Không có kiểm định chênh lệch nào "
        "duy trì ý nghĩa sau điều chỉnh FDR. "
        "Vì vậy không nên suy luận thay đổi cấu trúc "
        "chỉ từ việc hai đường hệ số khác nhau.",
        "teal",
    )

    show_table(
        df,
        "📋 Kiểm định chênh lệch trước/sau 2020",
    )


# ============================================================
# 12. RQ4 — CALM / STRESS
# ============================================================

elif page == "rq4":

    hero(
        "RESEARCH QUESTION 04",
        "RQ4 · <em>Calm vs Stress</em>",
        "Đánh giá sự khác biệt truyền dẫn cú sốc "
        "giữa thị trường bình ổn và căng thẳng.",
    )

    question("RQ4")

    insight(
        "ĐỊNH NGHĨA",
        "Stress: VIX phiên vĩ mô trước đó ≥ 30.",
        "Sử dụng trạng thái dựa trên VIX "
        "phiên trước để hạn chế thông tin đồng thời. "
        "Calm và Stress được so sánh bằng "
        "các hệ số tương tác LP.",
        "violet",
    )

    asset, shock = selectors("rq4")

    regimes = filtered(
        D["regime"],
        response=asset,
        shock=shock,
    )

    h0 = filtered(regimes, horizon=0)

    calm = first(filtered(h0, regime="Calm"))
    stress = first(filtered(h0, regime="Stress"))

    if calm is not None and stress is not None:
        section(
            "So sánh hệ số cùng ngày",
            f"{asset} · {SHOCK_LABELS[shock]}",
        )

        a, b, c = st.columns(3)

        with a:
            kpi(
                "Calm",
                fmt(calm.get("estimate")),
                "Thị trường bình ổn",
                "teal",
            )

        with b:
            kpi(
                "Stress",
                fmt(stress.get("estimate")),
                "Thị trường căng thẳng",
                "coral",
            )

        with c:
            kpi(
                "Stress − Calm",
                fmt(
                    stress.get(
                        "difference_stress_minus_calm"
                    )
                ),
                "Chênh lệch hệ số",
                "violet",
            )

    section(
        "Phản ứng theo trạng thái",
        "Đường LP của Calm và Stress.",
    )

    if not regimes.empty:
        fig = go.Figure()

        for name, color in [
            ("Calm", C["teal"]),
            ("Stress", C["coral"]),
        ]:
            part = filtered(regimes, regime=name)
            part = part.sort_values("horizon")

            fig.add_trace(
                go.Scatter(
                    x=part["horizon"],
                    y=part["estimate"],
                    mode="lines+markers",
                    name=name,
                    line=dict(color=color, width=3.5),
                )
            )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#9E8A9F",
        )

        fig.update_xaxes(title="Chân trời ngày lịch")
        fig.update_yaxes(title="Hệ số LP")

        chart(fig, "rq4_regime_chart")

    diag = filtered(
        D["regime_diag"],
        response=asset,
        horizon=0,
    )

    dr = first(diag)

    if dr is not None:
        a, b = st.columns(2)

        with a:
            kpi(
                "Quan sát Calm",
                fmt(dr.get("n_calm"), 0),
                "Kích thước mẫu",
                "teal",
            )

        with b:
            kpi(
                "Quan sát Stress",
                fmt(dr.get("n_stress"), 0),
                "Kích thước mẫu",
                "coral",
            )

    insight(
        "KẾT LUẬN RQ4",
        "Chưa xác nhận được khác biệt truyền dẫn "
        "giữa Calm và Stress.",
        "Các kiểm định chênh lệch không duy trì "
        "ý nghĩa thống kê sau FDR. "
        "Mẫu Stress nhỏ hơn đáng kể, "
        "khiến độ bất định của ước lượng cao hơn. "
        "Không có ý nghĩa thống kê không đồng nghĩa "
        "hai trạng thái hoàn toàn giống nhau.",
        "teal",
    )

    show_table(
        filtered(
            D["rq4"],
            response=asset,
            shock=shock,
        ),
        "📋 Kiểm định Calm–Stress",
    )


# ============================================================
# 13. RQ5 — MACHINE LEARNING
# ============================================================

elif page == "rq5":

    hero(
        "RESEARCH QUESTION 05",
        "RQ5 · <em>Dự báo Machine Learning</em>",
        "Đánh giá giá trị bổ sung của dữ liệu vĩ mô "
        "trong dự báo độ lớn lợi suất BTC và ETH.",
    )

    question("RQ5")

    insight(
        "BIẾN MỤC TIÊU",
        "Dự báo |r(t+1)| — độ lớn lợi suất ngày kế tiếp.",
        "Đây là trị tuyệt đối của lợi suất log, "
        "không phải VaR hay realized volatility. "
        "Năm 2025 được giữ làm tập kiểm tra ngoài mẫu.",
        "violet",
    )

    asset = st.selectbox(
        "🪙 Chọn tài sản",
        ["BTC", "ETH"],
        key="rq5_asset",
    )

    section(
        "So sánh sai số dự báo",
        "MAE và RMSE càng thấp càng tốt.",
    )

    comparison = filtered(
        D["comparison"],
        asset=asset,
    )

    if not comparison.empty:
        metric = st.selectbox(
            "📐 Chọn chỉ tiêu",
            ["MAE", "RMSE"],
            key="rq5_metric",
        )

        part = filtered(comparison, metric=metric)

        if not part.empty:
            part = part.copy()

            part["label"] = (
                part["model"].astype(str)
                + " · "
                + part["feature_set"].astype(str)
            )

            part = part.sort_values("value")

            fig = go.Figure(
                go.Bar(
                    x=part["value"],
                    y=part["label"],
                    orientation="h",
                    marker_color=[
                        C["teal"]
                        if f == "crypto_only"
                        else C["coral"]
                        for f in part["feature_set"]
                    ],
                    text=part["value"].round(4),
                    textposition="outside",
                )
            )

            fig.update_layout(
                yaxis=dict(autorange="reversed")
            )

            fig.update_xaxes(title=metric)

            chart(fig, "rq5_model_comparison", 450)

            best = part.iloc[0]

            insight(
                "MÔ HÌNH TỐT NHẤT THEO CHỈ TIÊU",
                f"{best['model']} · {best['feature_set']}",
                f"{metric} = {fmt(best['value'])}. "
                "Mô hình tốt nhất theo MAE "
                "không nhất thiết tốt nhất theo RMSE.",
                "teal",
            )

    section(
        "Dự báo và thực tế",
        "So sánh trên tập kiểm tra năm 2025.",
    )

    forecast = filtered(
        D["forecast"],
        asset=asset,
        split="test",
    )

    if not forecast.empty:
        models = sorted(
            forecast["model"].dropna().unique().tolist()
        )

        model = st.selectbox(
            "🤖 Chọn mô hình",
            models,
            key="rq5_model",
        )

        part = filtered(forecast, model=model)

        feature_sets = sorted(
            part["feature_set"].dropna().unique().tolist()
        )

        feature_set = st.selectbox(
            "🧩 Chọn bộ biến",
            feature_sets,
            key="rq5_feature_set",
        )

        part = filtered(
            part,
            feature_set=feature_set,
        )

        part = part.copy()

        part["date"] = pd.to_datetime(
            part["date"],
            errors="coerce",
        )

        part = part.sort_values("date")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=part["date"],
                y=part["actual"],
                mode="lines",
                name="Thực tế",
                line=dict(
                    color=C["plum"],
                    width=3,
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
                    color=C["coral"],
                    width=3,
                ),
            )
        )

        fig.update_xaxes(title="Ngày")
        fig.update_yaxes(title="|Lợi suất log| (%)")

        chart(fig, "rq5_forecast", 460)

    section(
        "Kiểm định lợi ích của dữ liệu vĩ mô",
        "Block bootstrap cho chênh lệch MAE.",
    )

    sig = filtered(
        D["significance"],
        asset=asset,
    )

    if not sig.empty:
        needed = {
            "candidate_feature_set",
            "reference_feature_set",
            "mae_reduction",
            "candidate_model",
            "ci95_lower",
            "ci95_upper",
        }

        if needed.issubset(sig.columns):
            sig = sig[
                (sig["candidate_feature_set"] == "crypto_macro")
                & (sig["reference_feature_set"] == "crypto_only")
            ].copy()

            fig = go.Figure()

            for _, r in sig.iterrows():
                gain = float(r["mae_reduction"])

                fig.add_trace(
                    go.Scatter(
                        x=[gain],
                        y=[str(r["candidate_model"])],
                        mode="markers",
                        marker=dict(
                            size=16,
                            color=(
                                C["teal"]
                                if gain > 0
                                else C["coral"]
                            ),
                        ),
                        error_x=dict(
                            type="data",
                            symmetric=False,
                            array=[
                                max(
                                    0,
                                    float(r["ci95_upper"]) - gain
                                )
                            ],
                            arrayminus=[
                                max(
                                    0,
                                    gain - float(r["ci95_lower"])
                                )
                            ],
                        ),
                        showlegend=False,
                    )
                )

            fig.add_vline(
                x=0,
                line_dash="dash",
                line_color=C["plum"],
            )

            fig.update_xaxes(
                title="Giảm MAE khi thêm biến vĩ mô"
            )

            chart(fig, "rq5_bootstrap", 370)

    insight(
        "CÁCH ĐỌC",
        "Giảm MAE dương nghĩa là dữ liệu vĩ mô "
        "giúp giảm sai số.",
        "Nếu khoảng tin cậy 95% cắt qua 0, "
        "chưa đủ bằng chứng về cải thiện. "
        "Nếu toàn bộ khoảng nằm dưới 0, "
        "việc thêm macro làm dự báo kém đi "
        "một cách có ý nghĩa thống kê.",
        "gold",
    )

    insight(
        "KẾT LUẬN RQ5",
        "Dữ liệu vĩ mô không cải thiện dự báo "
        "một cách nhất quán.",
        "Kết quả ngoài mẫu 2025 không cho thấy "
        "lợi ích dự báo ổn định từ việc thêm macro. "
        "Một số mô hình còn có MAE cao hơn "
        "khi bổ sung các biến tài chính toàn cầu.",
        "teal",
    )

    section(
        "Feature importance",
        "Các biến đóng góp nhiều cho mô hình.",
    )

    imp = filtered(
        D["importance"],
        asset=asset,
    )

    if not imp.empty:
        models = sorted(
            imp["model"].dropna().unique().tolist()
        )

        chosen = st.selectbox(
            "Chọn mô hình giải thích",
            models,
            key="rq5_importance_model",
        )

        imp = filtered(imp, model=chosen)

        feature_sets = sorted(
            imp["feature_set"].dropna().unique().tolist()
        )

        chosen_set = st.selectbox(
            "Chọn bộ biến giải thích",
            feature_sets,
            key="rq5_importance_features",
        )

        imp = filtered(
            imp,
            feature_set=chosen_set,
        )

        imp = imp.sort_values(
            "importance",
            ascending=False,
        ).head(12)

        fig = go.Figure(
            go.Bar(
                x=imp["importance"].iloc[::-1],
                y=imp["feature"].iloc[::-1],
                orientation="h",
                marker_color=C["violet"],
            )
        )

        fig.update_xaxes(title="Độ quan trọng")

        chart(fig, "rq5_importance", 510)

        insight(
            "GIỚI HẠN DIỄN GIẢI",
            "Không so sánh trực tiếp importance "
            "của Elastic Net và XGBoost.",
            "Elastic Net sử dụng độ lớn hệ số "
            "chuẩn hóa; XGBoost sử dụng gain. "
            "Hai thước đo không cùng ý nghĩa.",
            "violet",
        )

    show_table(comparison, "📋 MAE / RMSE")
    show_table(sig, "📋 Kiểm định dự báo")
    show_table(forecast, "📋 Dữ liệu dự báo")


# ============================================================
# 14. DATA & METHODOLOGY
# ============================================================

elif page == "methods":

    hero(
        "DATA & RESEARCH DESIGN",
        "Dữ liệu <em>& Phương pháp</em>",
        "Trình bày nguồn dữ liệu, cách xử lý, "
        "các mô hình và giới hạn nghiên cứu.",
    )

    section(
        "Nguồn dữ liệu",
        "Các biến được sử dụng trong nghiên cứu.",
    )

    a, b, c = st.columns(3)

    with a:
        insight(
            "CRYPTO",
            "Bitcoin và Ethereum",
            "Lợi suất log được tính theo "
            "100 × ln(Pt/Pt−1).",
            "coral",
        )

    with b:
        insight(
            "RỦI RO & USD",
            "VIX và DXY",
            "VIX phản ánh bất định thị trường; "
            "DXY đại diện cho sức mạnh đồng USD.",
            "teal",
        )

    with c:
        insight(
            "LÃI SUẤT",
            "US2Y",
            "Lợi suất trái phiếu Kho bạc Mỹ "
            "kỳ hạn 2 năm.",
            "violet",
        )

    section(
        "Chất lượng dữ liệu",
        "Tỷ lệ thiếu và cách xử lý.",
    )

    quality = D["quality"]

    if not quality.empty:
        show_table(
            quality,
            "📋 Báo cáo chất lượng dữ liệu",
        )

        if {
            "variable",
            "missing_rate_percent",
        }.issubset(quality.columns):
            q = quality.sort_values(
                "missing_rate_percent",
                ascending=False,
            ).head(12)

            fig = go.Figure(
                go.Bar(
                    x=q["missing_rate_percent"],
                    y=q["variable"],
                    orientation="h",
                    marker_color=C["coral"],
                )
            )

            fig.update_layout(
                yaxis=dict(autorange="reversed")
            )

            fig.update_xaxes(title="Tỷ lệ thiếu (%)")

            chart(fig, "methods_missing", 460)

    insight(
        "XỬ LÝ DỮ LIỆU",
        "Không thay giá trị thiếu bằng 0.",
        "Crypto giao dịch cả cuối tuần, "
        "trong khi dữ liệu vĩ mô có ngày nghỉ. "
        "Các quan sát thiếu được xử lý "
        "phù hợp với từng mô hình, "
        "không mặc định bằng 0.",
        "gold",
    )

    section(
        "Phương pháp nghiên cứu",
        "Các phương pháp bổ trợ cho nhau.",
    )

    insight(
        "VAR",
        "VAR(5) và IRF Cholesky",
        "Thứ tự nhận dạng: "
        "VIX → DXY → US2Y → BTC → ETH.",
        "violet",
    )

    insight(
        "LOCAL PROJECTIONS",
        "LP theo từng chân trời",
        "Ước lượng phản ứng lợi suất "
        "tại các chân trời h = 0 đến 30. "
        "Sử dụng HAC và điều chỉnh FDR "
        "cho kiểm định nhiều lần.",
        "teal",
    )

    insight(
        "SO SÁNH TRẠNG THÁI",
        "Pre/Post 2020 và Calm/Stress",
        "Kiểm định sự khác biệt hệ số "
        "bằng các mô hình tương tác.",
        "coral",
    )

    insight(
        "MACHINE LEARNING",
        "Historical30 · Elastic Net · XGBoost",
        "Dự báo |r(t+1)|, đánh giá ngoài mẫu "
        "năm 2025 bằng MAE, RMSE "
        "và block bootstrap.",
        "gold",
    )

    show_table(
        D["descriptive"],
        "📋 Thống kê mô tả",
    )

    show_table(
        D["var_diag"],
        "📋 Chẩn đoán VAR",
    )


# ============================================================
# 15. FOOTER
# ============================================================

st.divider()

st.html(
    """
<div style="
    text-align:center;
    padding:19px 0 30px;
    color:#756779;
    font-size:14px;
    line-height:2;
">
    <strong style="
        color:#503A55;
        font-size:15px;
    ">
        ✦ MACRO × CRYPTO INTELLIGENCE
    </strong><br>
    Research Analytics Dashboard · 2018–2025<br>
    Nội dung phục vụ nghiên cứu học thuật,
    không phải khuyến nghị đầu tư.
</div>
"""
)

