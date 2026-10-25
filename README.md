
# MACRO × CRYPTO | Crypto Insights

**Điều kiện tài chính toàn cầu và thị trường tiền mã hóa: Phân tích mối liên hệ động, sự khác biệt theo giai đoạn/trạng thái và khả năng dự báo lợi suất Bitcoin, Ethereum**

Dự án nghiên cứu ứng dụng Python để khảo sát mối liên hệ giữa **Bitcoin (BTC), Ethereum (ETH)** và ba chỉ báo tài chính toàn cầu:

- **US2Y:** Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm.
- **DXY:** Chỉ số sức mạnh đồng USD (sử dụng chuỗi đại diện/proxy).
- **VIX:** Chỉ số biến động thị trường chứng khoán Mỹ.

Nghiên cứu kết hợp **kinh tế lượng, học máy và dashboard tương tác Streamlit**, nhằm phân tích các mối liên hệ vĩ mô – tiền mã hóa và đánh giá khả năng dự báo ngoài mẫu.

> **Lưu ý:** Các kết quả VAR/IRF và Local Projections phản ánh mối liên hệ thống kê có điều kiện, không mặc nhiên chứng minh quan hệ nhân quả. Nội dung chỉ phục vụ nghiên cứu và học tập, không phải khuyến nghị đầu tư.

---

## 1. Mục tiêu và câu hỏi nghiên cứu

| Câu hỏi | Nội dung | Phương pháp |
|---|---|---|
| **RQ1** | US2Y, DXY và VIX liên hệ như thế nào với lợi suất BTC/ETH? | Local Projections (LP), HAC |
| **RQ2** | Phản ứng của BTC/ETH thay đổi ra sao theo các khoảng thời gian sau biến động vĩ mô? | LP và VAR(5)/IRF |
| **RQ3** | Mối liên hệ có khác biệt giữa giai đoạn 2018–2019 và 2020–2025 không? | Phân tích trước/sau 2020, kiểm định chênh lệch |
| **RQ4** | Mối liên hệ có khác biệt giữa trạng thái Calm và Stress không? | LP có tương tác trạng thái |
| **RQ5** | Thêm biến vĩ mô có cải thiện dự báo ngoài mẫu độ lớn lợi suất ngày kế tiếp không? | Elastic Net, XGBoost |

Các kiểm định nhiều giả thuyết được đánh giá bằng phương pháp **Benjamini–Hochberg FDR** ở mức ý nghĩa 5%.

---

## 2. Dữ liệu nghiên cứu

**Giai đoạn nghiên cứu:** 01/01/2018 – 31/12/2025.

| Biến | Nội dung | Nguồn |
|---|---|---|
| BTC | Giá và lợi suất Bitcoin | Yahoo Finance |
| ETH | Giá và lợi suất Ethereum | Yahoo Finance |
| US2Y | Lợi suất TPCP Mỹ kỳ hạn 2 năm | FRED (`DGS2`) |
| DXY | Chỉ số USD (proxy) | Yahoo Finance (`DX-Y.NYB`) |
| VIX | Chỉ số biến động thị trường | Yahoo Finance (`^VIX`) |

**Quy tắc xử lý dữ liệu:**

- BTC và ETH được tính lợi suất log theo ngày lịch.
- Biến động US2Y, DXY và VIX được tính giữa hai quan sát vĩ mô hợp lệ liên tiếp.
- Dữ liệu vĩ mô thiếu được giữ dưới dạng `NA`, không tự động thay bằng 0 hoặc nội suy.
- Phân biệt ngày giao dịch crypto với ngày có quan sát vĩ mô.
- Bộ dữ liệu chuẩn có **2.922 ngày lịch**; số quan sát dùng trong từng mô hình có thể khác nhau.

Đối với RQ5, biến mục tiêu là **giá trị tuyệt đối của lợi suất log ngày kế tiếp**, không phải VaR hay Expected Shortfall.

---

## 3. Cấu trúc repository

```text
macro-crypto-shock-transmission-main/
│
├── .streamlit/
│   └── config.toml
│
├── config/
│   └── research_config.json
│
├── dashboard/
│   ├── 12_dashboard_app.py
│   └── 13_dashboard_utils.py
│
├── data/
│   ├── raw/
│   │   ├── crypto_macro_raw.csv
│   │   └── crypto_macro_raw.xlsx
│   └── processed/
│       ├── model_dataset.csv
│       └── ml_dataset.csv
│
├── docs/
│   ├── academic_review_checklist.md
│   ├── integration_qa_checklist.md
│   ├── data_dictionary.xlsx
│   ├── data_source_log.xlsx
│   ├── literature_matrix.xlsx
│   └── task_assignment.md
│
├── src/
│   ├── research/
│   │   └── 01_research_config.py
│   │
│   ├── data/
│   │   ├── 02_download_data.py
│   │   ├── 03_preprocess_data.py
│   │   └── 04_descriptive_stats.py
│   │
│   ├── econometrics/
│   │   ├── 05_var_irf.py
│   │   ├── 05_var_lag_diagnostics.py
│   │   ├── 06_local_projection.py
│   │   ├── 07_regime_analysis.py
│   │   ├── 08_hac_sensitivity.py
│   │   ├── 08_multiple_testing.py
│   │   ├── 08_robustness.py
│   │   ├── 08_rolling_sensitivity.py
│   │   ├── 08_subperiod_difference.py
│   │   └── 08_var_sensitivity.py
│   │
│   ├── ml/
│   │   ├── 09_ml_features.py
│   │   ├── 10_ml_forecast.py
│   │   ├── 11_model_evaluation.py
│   │   └── ml_common.py
│   │
│   └── pipeline/
│       └── 14_run_pipeline.py
│
├── outputs/
│   ├── figures/
│   │   ├── correlation_heatmap.png
│   │   ├── crypto_price_trends.png
│   │   ├── forecast_comparison.png
│   │   ├── irf_btc.png
│   │   ├── irf_eth.png
│   │   ├── lp_responses.png
│   │   ├── regime_comparison.png
│   │   └── rolling_sensitivity.png
│   │
│   ├── model_results/
│   │   ├── lp_results.csv
│   │   ├── lp_fdr.csv
│   │   ├── irf_results.csv
│   │   ├── subperiod_results.csv
│   │   ├── subperiod_difference_fdr.csv
│   │   ├── regime_results.csv
│   │   ├── regime_difference_fdr.csv
│   │   ├── rolling_sensitivity.csv
│   │   ├── model_comparison.csv
│   │   ├── forecast_results.csv
│   │   ├── forecast_significance.csv
│   │   └── ... (các kết quả và kiểm định bổ sung)
│   │
│   └── tables/
│       ├── correlation_matrix.csv
│       ├── descriptive_stats.csv
│       └── preprocessing_quality_report.csv
│
├── paper/
│   ├── drafts/
│   │   ├── 01_introduction_literature.docx
│   │   ├── 02_data_methodology.docx
│   │   ├── 03_econometric_results.docx
│   │   ├── 04_ml_results.docx
│   │   └── 05_discussion_conclusion_formatted_revised.docx
│   │
│   ├── final/
│   │   ├── research_paper_final.docx
│   │   └── research_paper_final.pdf
│   │
│   └── references/
│       └── references.bib
│
├── tests/
│   └── test_pipeline.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

**Ghi chú:** Đây là cấu trúc theo repository đã kiểm tra. Thư mục `outputs/model_results/` chứa thêm các kết quả kiểm định FDR, độ nhạy HAC/VAR, robustness và các chỉ tiêu đánh giá mô hình.

---

## 4. Cài đặt môi trường

### Bước 1. Clone repository

```bash
git clone <repository-url>
cd macro-crypto-shock-transmission-main
```

Thay `<repository-url>` bằng đường dẫn GitHub của nhóm.

### Bước 2. Tạo môi trường Python

Khuyến nghị sử dụng Python 3.11.

```powershell
python -m venv .venv
```

Kích hoạt môi trường ảo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn kích hoạt:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Bước 3. Cài đặt thư viện

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 5. Chạy dashboard Streamlit

Từ thư mục gốc chứa `dashboard/` và `requirements.txt`, chạy:

```powershell
python -m streamlit run .\dashboard\12_dashboard_app.py
```

Sau đó mở:

**http://localhost:8501**

### Xử lý lỗi không tìm thấy file

Nếu xuất hiện:

```text
Error: Invalid value: File does not exist:
dashboard\12_dashboard_app.py
```

Kiểm tra thư mục hiện tại:

```powershell
Get-Location
Get-ChildItem
```

Tìm đường dẫn thực tế của dashboard:

```powershell
Get-ChildItem -Recurse -Filter 12_dashboard_app.py |
    Select-Object -ExpandProperty FullName
```

Di chuyển đến đúng thư mục gốc rồi chạy lại lệnh Streamlit.

### Kiểm tra kết quả đầu ra

Repository có script hỗ trợ kiểm tra output và mở dashboard:

```powershell
python .\src\pipeline\14_run_pipeline.py --check
```

```powershell
python .\src\pipeline\14_run_pipeline.py --dashboard
```

**Lưu ý:** Các lệnh này dùng để kiểm tra sự hiện diện của output và mở dashboard, không đồng nghĩa với việc chạy lại toàn bộ mô hình kinh tế lượng và học máy.

---

## 6. Dashboard nghiên cứu

Dashboard **Crypto Insights** được xây dựng bằng Streamlit để trình bày các kết quả nghiên cứu dưới dạng biểu đồ tương tác.

### Các mục hiện có trong repository

| Tab | Nội dung |
|---|---|
| Tổng quan nghiên cứu | Phạm vi dữ liệu, xu hướng BTC/ETH và tương quan |
| RQ1 – Truyền dẫn | Phân tích Local Projections |
| RQ2 – Phản ứng động | Phản ứng theo thời gian, đối chiếu LP và VAR/IRF |
| RQ3 – Trước/sau 2020 | So sánh giai đoạn 2018–2019 và 2020–2025 |
| RQ4 – Calm/Stress | Phân tích khác biệt theo trạng thái thị trường |
| RQ5 – Dự báo ML | Đánh giá Elastic Net, XGBoost và benchmark |
| Dữ liệu & cách đọc | Giải thích dữ liệu, phương pháp và ý nghĩa biểu đồ |

**Lưu ý phiên bản:** File dashboard trong ZIP hiện có 7 mục điều hướng. Tab **Kết luận & ứng dụng** chưa có trong phiên bản mã nguồn này.

### Cách đọc biểu đồ

- Trục **2018–2025** biểu thị thời gian lịch.
- Trục **h = 0–30** trong LP/IRF biểu thị số ngày hoặc phiên sau biến động vĩ mô, không phải năm.
- Dải tin cậy 95% thể hiện mức độ bất định của ước lượng.
- Q-value FDR dùng để đánh giá ý nghĩa thống kê sau hiệu chỉnh nhiều kiểm định.

Hai hệ số ước lượng khác nhau về giá trị không có nghĩa chênh lệch giữa chúng đã có ý nghĩa thống kê.

---

## 7. Kết quả nghiên cứu chính

### RQ1–RQ2: Mối liên hệ và phản ứng động

- VIX và DXY có mối liên hệ âm cùng ngày với lợi suất BTC và ETH trong kết quả cơ sở.
- Phản ứng theo các khoảng thời gian sau biến động vĩ mô không hoàn toàn ổn định.
- Khoảng tin cậy cần được xem xét khi diễn giải ý nghĩa của các ước lượng.
- Kết quả VAR/IRF không được mặc nhiên diễn giải là bằng chứng nhân quả.

### RQ3: So sánh trước và sau năm 2020

- Nghiên cứu so sánh hai giai đoạn **2018–2019** và **2020–2025**.
- Các hệ số ước lượng có thể khác nhau về độ lớn và dấu.
- Tuy nhiên, chưa có bằng chứng thống kê đủ mạnh về sự khác biệt có hệ thống sau điều chỉnh BH-FDR.

### RQ4: Calm và Stress

- Trạng thái thị trường được phân loại dựa trên VIX của phiên quan sát trước.
- Ngưỡng Stress cơ sở là **VIX ≥ 30**.
- Nhóm thực hiện kiểm tra độ nhạy với ngưỡng 25 và 35.
- Chưa có bằng chứng đủ mạnh về sự khác biệt giữa Calm và Stress sau FDR.
- Kết quả không đồng nghĩa hai trạng thái hoàn toàn giống nhau.

### RQ5: Dự báo bằng học máy

Nghiên cứu so sánh:

- Benchmark trung bình lịch sử 30 ngày.
- Elastic Net với dữ liệu Crypto-only.
- Elastic Net với dữ liệu Crypto + Macro.
- XGBoost với dữ liệu Crypto-only.
- XGBoost với dữ liệu Crypto + Macro.

Tập kiểm tra ngoài mẫu là **năm 2025**.

Ví dụ đối với BTC, MAE của Elastic Net:

| Bộ đặc trưng | MAE |
|---|---:|
| Crypto-only | 1,1309 |
| Crypto + Macro | 1,1643 |

Việc bổ sung biến vĩ mô làm sai số tăng trong trường hợp này.

**Kết luận chung:** Các biến vĩ mô có thể liên hệ với lợi suất tiền mã hóa, nhưng không nhất thiết cải thiện khả năng dự báo ngoài mẫu.

---

## 8. Phương pháp và kiểm định

### Kinh tế lượng

- Vector Autoregression (VAR).
- Impulse Response Functions (IRF).
- Local Projections (LP).
- Sai số chuẩn HAC.
- Kiểm định khác biệt trước/sau 2020.
- Kiểm định khác biệt Calm/Stress.
- Benjamini–Hochberg FDR.
- Kiểm tra độ nhạy mô hình.

### Học máy

- Elastic Net.
- XGBoost.
- Crypto-only và Crypto + Macro.
- Historical30 benchmark.
- MAE và RMSE.
- Block bootstrap để đánh giá chênh lệch sai số.

---

## 9. Báo cáo nghiên cứu

Các phần báo cáo được xây dựng theo trình tự:

| File | Nội dung |
|---|---|
| `01_introduction_literature.docx` | Giới thiệu, cơ sở lý thuyết và nghiên cứu trước |
| `02_data_methodology.docx` | Dữ liệu và phương pháp |
| `03_econometric_results.docx` | Kết quả kinh tế lượng |
| `04_ml_results.docx` | Kết quả dự báo học máy |
| `05_discussion_conclusion_formatted_revised.docx` | Thảo luận, kết luận và ứng dụng |

### Báo cáo hoàn chỉnh

- [Bản Word](paper/final/research_paper_final.docx)
- [Bản PDF](paper/final/research_paper_final.pdf)

### Tài liệu tham khảo

Danh mục tài liệu tham khảo được quản lý tại:

`paper/references/references.bib`

---

## 10. Giới hạn nghiên cứu

- Các mối liên hệ thống kê không mặc nhiên phản ánh quan hệ nhân quả.
- Lịch giao dịch crypto và thị trường tài chính truyền thống khác nhau.
- Thời điểm thông tin vĩ mô thực sự sẵn có có thể ảnh hưởng đến diễn giải dự báo.
- Giai đoạn trước năm 2020 và mẫu Stress có ít quan sát hơn.
- Kết quả kiểm tra ngoài mẫu năm 2025 chưa đủ để khẳng định hiệu quả dự báo trong mọi chu kỳ.
- Kết quả phụ thuộc vào mẫu dữ liệu, đặc tả và giả định của mô hình.

---

## 11. Công nghệ sử dụng

- **Ngôn ngữ:** Python
- **Xử lý dữ liệu:** pandas, NumPy
- **Kinh tế lượng:** statsmodels
- **Học máy:** scikit-learn, XGBoost
- **Trực quan hóa:** Matplotlib, Plotly
- **Dashboard:** Streamlit
- **Quản lý mã nguồn:** Git, GitHub

---

## 12. Tình trạng dự án

Repository hiện có:

- Dữ liệu gốc và dữ liệu đã xử lý.
- Các script kinh tế lượng và học máy.
- Kết quả mô hình và kiểm định.
- Biểu đồ nghiên cứu.
- Dashboard Streamlit.
- Các bản thảo nghiên cứu 01–05.
- Báo cáo final dạng DOCX và PDF.
- Research config và tài liệu kiểm tra chất lượng.

**Lưu ý:** `tests/test_pipeline.py` hiện chưa chứa bộ kiểm thử tự động hoàn chỉnh. Việc có đủ output không thay thế cho kiểm thử tái lập toàn bộ pipeline.

---

**MACRO × CRYPTO — Crypto Insights**

*Dự án nghiên cứu học thuật ứng dụng kinh tế lượng, học máy và trực quan hóa dữ liệu trong tài chính.*

**Disclaimer:** Nội dung phục vụ mục đích học tập và nghiên cứu, không cấu thành khuyến nghị đầu tư.
