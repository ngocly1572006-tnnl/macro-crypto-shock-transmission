# macro-crypto-shock-transmission
Research on global financial shocks and their transmission to Bitcoin and Ethereum using Econometrics, Machine Learning, and Streamlit Dashboard

# NGHIÊN CỨU TÁC ĐỘNG CỦA ĐIỀU KIỆN TÀI CHÍNH TOÀN CẦU ĐẾN THỊ TRƯỜNG TIỀN MÃ HÓA

### Global Financial Conditions and Cryptocurrency Markets: Nonlinear Transmission of Monetary, Dollar and Risk Shocks to Bitcoin and Ethereum

**Thời gian nghiên cứu:** 01/01/2018 – 31/12/2025  
**Thời gian thực hiện dự án:** 16/10/2026 – 25/10/2026  
**Ngôn ngữ lập trình:** Python  
**Nền tảng Dashboard:** Streamlit  
**Số thành viên:** 06  
**Trạng thái:** Đang triển khai

---

## 1. Giới thiệu dự án

Dự án nghiên cứu mối quan hệ giữa điều kiện tài chính toàn cầu và thị trường tiền mã hóa, tập trung vào hai tài sản Bitcoin (BTC) và Ethereum (ETH).

Nghiên cứu sử dụng ba chỉ báo tài chính toàn cầu:

- **US2Y:** Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm.
- **USD Index:** Chỉ số sức mạnh đồng USD (DXY hoặc chỉ số thay thế có nguồn dữ liệu phù hợp).
- **VIX:** Chỉ số phản ánh kỳ vọng biến động của thị trường chứng khoán Mỹ.

Thông qua các phương pháp kinh tế lượng và Machine Learning, nhóm phân tích mức độ phản ứng của BTC/ETH trước biến động của các chỉ báo trên, sự khác biệt giữa các giai đoạn và trạng thái thị trường, đồng thời đánh giá khả năng dự báo biến động tiền mã hóa.

### Sản phẩm dự kiến

1. Bộ dữ liệu tài chính và tiền mã hóa giai đoạn 2018–2025.
2. Kết quả phân tích thống kê và kinh tế lượng.
3. Mô hình Machine Learning dự báo biến động.
4. Dashboard tương tác xây dựng bằng Streamlit.
5. Báo cáo nghiên cứu khoa học.
6. Mã nguồn Python và tài liệu hướng dẫn tái lập kết quả.

---

## 2. Mục tiêu và câu hỏi nghiên cứu

Dự án tập trung giải quyết năm câu hỏi nghiên cứu đã được nhóm thống nhất.

| Câu hỏi | Nội dung |
|---|---|
| RQ1 | Biến động lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm có liên hệ với phản ứng lợi suất BTC/ETH như thế nào? |
| RQ2 | Biến động USD và VIX truyền dẫn đến BTC/ETH với độ lớn và thời gian phản ứng ra sao? |
| RQ3 | Mức độ nhạy cảm của BTC/ETH có thay đổi giữa giai đoạn trước năm 2020 và từ năm 2020 trở đi không? |
| RQ4 | Sự truyền dẫn có khác biệt giữa trạng thái thị trường bình thường (Calm) và căng thẳng (Stress) không? |
| RQ5 | Các biến tài chính toàn cầu có cải thiện khả năng dự báo biến động BTC/ETH ngoài mẫu so với mô hình tham chiếu (Benchmark) hay không? |

---

## 3. Phạm vi nghiên cứu

### 3.1. Giai đoạn nghiên cứu

Dữ liệu được thu thập trong giai đoạn:

**01/01/2018 – 31/12/2025**

Đối với phân tích sự thay đổi theo thời kỳ, mẫu nghiên cứu được chia thành:

| Giai đoạn | Khoảng thời gian |
|---|---|
| Trước năm 2020 (Pre-2020) | 2018–2019 |
| Từ năm 2020 (Post-2020) | 2020–2025 |

Hai giai đoạn có số năm khác nhau. Nhóm sẽ xem xét quy mô mẫu và kiểm tra độ nhạy khi diễn giải kết quả so sánh.

### 3.2. Các biến nghiên cứu

| Biến | Ý nghĩa | Vai trò |
|---|---|---|
| BTC | Giá và lợi suất Bitcoin | Biến phản ứng |
| ETH | Giá và lợi suất Ethereum | Biến phản ứng |
| US2Y | Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm | Chỉ báo lãi suất |
| USD Index | DXY hoặc chỉ số USD thay thế | Chỉ báo sức mạnh USD |
| VIX | Chỉ số biến động kỳ vọng | Chỉ báo rủi ro |

**Lưu ý:** US2Y là lợi suất của trái phiếu có kỳ hạn 2 năm, không có nghĩa là nghiên cứu chỉ sử dụng dữ liệu trong 2 năm.

### 3.3. Tần suất dữ liệu

- Dữ liệu được xử lý theo tần suất ngày.
- BTC và ETH giao dịch liên tục, bao gồm cuối tuần.
- Các chỉ báo tài chính Mỹ chủ yếu có dữ liệu theo ngày giao dịch.
- Nhóm sẽ thống nhất quy tắc đồng bộ ngày và xử lý dữ liệu thiếu để tránh sai lệch thời gian và sử dụng thông tin tương lai.

Nguồn dữ liệu, đơn vị đo lường và các phép biến đổi sẽ được ghi nhận trong `docs/data_source_log.xlsx` và `docs/data_dictionary.xlsx`.

---

## 4. Phương pháp nghiên cứu

### 4.1. Thống kê mô tả

Nhóm thực hiện:

- Thống kê mô tả các biến nghiên cứu.
- Phân tích diễn biến giá và lợi suất BTC/ETH.
- Phân tích biến động của VIX, USD Index và US2Y.
- Xây dựng ma trận tương quan.
- Trực quan hóa dữ liệu.

### 4.2. Mô hình VAR và IRF

Mô hình Vector Autoregression (VAR) được sử dụng để phân tích mối quan hệ động giữa các biến tài chính và lợi suất tiền mã hóa.

Hàm phản ứng xung (Impulse Response Function – IRF) được sử dụng để biểu diễn phản ứng ước lượng của BTC/ETH theo các khoảng thời gian sau một biến động trong hệ thống.

### 4.3. Local Projection

Phương pháp Local Projection (LP) được sử dụng để ước lượng phản ứng động theo từng khoảng thời gian dự báo.

Kết quả LP sẽ được đối chiếu với VAR/IRF nhằm đánh giá tính nhất quán của các phát hiện.

### 4.4. Phân tích trạng thái thị trường

Nghiên cứu xem xét sự khác biệt giữa:

- **Calm:** Trạng thái thị trường bình thường.
- **Stress:** Trạng thái thị trường căng thẳng.

Quy tắc phân loại trạng thái sẽ được xác định và ghi rõ trong phương pháp nghiên cứu.

### 4.5. Phân tích theo giai đoạn

Nhóm so sánh kết quả trong hai giai đoạn:

- Pre-2020: 2018–2019.
- Post-2020: 2020–2025.

Ngoài ra, Rolling Regression được sử dụng để đánh giá sự thay đổi độ nhạy theo thời gian.

### 4.6. Machine Learning

Nhóm dự kiến sử dụng Elastic Net và mô hình Benchmark để dự báo đại diện biến động BTC/ETH ngày tiếp theo, được đo bằng giá trị tuyệt đối của lợi suất log ngày tiếp theo.

Dữ liệu được chia theo thời gian:

| Tập dữ liệu | Giai đoạn |
|---|---|
| Training và Validation | 2018–2024 |
| Testing ngoài mẫu | 2025 |

Các chỉ tiêu đánh giá:

- **MAE:** Mean Absolute Error.
- **RMSE:** Root Mean Squared Error.

Việc đánh giá sử dụng cùng tập kiểm tra ngoài mẫu và không đưa thông tin tương lai vào các biến dự báo.

**Giới hạn phương pháp:** Kết quả tương quan hoặc phản ứng từ VAR không tự động chứng minh quan hệ nhân quả của cú sốc chính sách tiền tệ.

---

## 5. Cấu trúc thư mục dự án

```text
macro-crypto-shock-transmission/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   └── research_config.json
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
│   │   ├── 06_local_projection.py
│   │   ├── 07_regime_analysis.py
│   │   ├── 08_robustness.py
│   │   └── 08_rolling_sensitivity.py
│   │
│   ├── ml/
│   │   ├── 09_ml_features.py
│   │   ├── 10_ml_forecast.py
│   │   └── 11_model_evaluation.py
│   │
│   └── pipeline/
│       └── 14_run_pipeline.py
│
├── dashboard/
│   ├── 12_dashboard_app.py
│   └── 13_dashboard_utils.py
│
├── data/
│   ├── raw/
│   │   └── crypto_macro_raw.csv
│   │
│   └── processed/
│       ├── model_dataset.csv
│       └── ml_dataset.csv
│
├── outputs/
│   ├── tables/
│   │   ├── descriptive_stats.csv
│   │   └── correlation_matrix.csv
│   │
│   ├── model_results/
│   │   ├── var_results.csv
│   │   ├── irf_results.csv
│   │   ├── lp_results.csv
│   │   ├── regime_results.csv
│   │   ├── subperiod_results.csv
│   │   ├── rolling_sensitivity.csv
│   │   ├── robustness_results.csv
│   │   ├── forecast_results.csv
│   │   ├── model_comparison.csv
│   │   └── feature_importance.csv
│   │
│   └── figures/
│       ├── crypto_price_trends.png
│       ├── correlation_heatmap.png
│       ├── irf_btc.png
│       ├── irf_eth.png
│       ├── lp_responses.png
│       ├── regime_comparison.png
│       └── forecast_comparison.png
│
├── paper/
│   ├── drafts/
│   │   ├── 01_introduction_literature.docx
│   │   ├── 02_data_methodology.docx
│   │   ├── 03_econometric_results.docx
│   │   ├── 04_ml_results.docx
│   │   └── 05_discussion_conclusion.docx
│   │
│   ├── final/
│   │   ├── research_paper_final.docx
│   │   └── research_paper_final.pdf
│   │
│   └── references/
│       └── references.bib
│
├── docs/
│   ├── task_assignment.md
│   ├── literature_matrix.xlsx
│   ├── data_source_log.xlsx
│   ├── data_dictionary.xlsx
│   ├── academic_review_checklist.md
│   └── integration_qa_checklist.md
│
└── tests/
    └── test_pipeline.py
```

**Lưu ý:** Đây là cấu trúc dự kiến của dự án. Một số file dữ liệu, mã nguồn và kết quả sẽ được bổ sung theo tiến độ thực hiện.

---

## 6. Phân công thành viên

| Thành viên | Vai trò | Công việc chính |
|---|---|---|
| Yến Nhi | Research & Academic Review | Tổng quan nghiên cứu, khung lý thuyết, giả thuyết, cấu hình nghiên cứu và kiểm tra học thuật |
| Hoài Nhi | Data Engineering | Thu thập, xử lý dữ liệu, thống kê mô tả và chuẩn hóa dữ liệu |
| Hải Bình | Econometric Modeling | VAR/IRF, LP, Calm/Stress, Pre/Post-2020, Rolling và Robustness |
| Mai Phương | Machine Learning | Xây dựng đặc trưng, dự báo và đánh giá mô hình |
| Lam Kiều | Research Paper | Tổng hợp kết quả, thảo luận, kết luận và hoàn thiện báo cáo |
| Ngọc Ly | Dashboard & Integration | Xây dựng Streamlit, Pipeline, kiểm thử và quản lý GitHub |

Chi tiết công việc, file bàn giao và thời hạn hoàn thành:

**[Xem bảng phân công công việc](docs/task_assignment.md)**

---

## 7. Thiết kế Dashboard

Dashboard dự kiến được xây dựng bằng Streamlit với bốn tab chính.

### Tab 1 – Overview

**Mục tiêu:** Cung cấp cái nhìn tổng quan về thị trường tiền mã hóa và điều kiện tài chính toàn cầu.

Nội dung dự kiến:

- Biểu đồ giá BTC và ETH.
- Biểu đồ lợi suất BTC và ETH.
- Diễn biến VIX, USD Index và US2Y.
- Thống kê mô tả.
- Ma trận tương quan.
- Bộ lọc tài sản và thời gian nếu dữ liệu hỗ trợ.

### Tab 2 – Econometrics

**Mục tiêu:** Trực quan hóa kết quả phân tích kinh tế lượng.

Nội dung dự kiến:

- Kết quả VAR.
- Biểu đồ IRF.
- Kết quả Local Projection.
- Khoảng tin cậy của các ước lượng.
- Bộ lọc Asset, Shock, Model và Horizon.

### Tab 3 – Regime

**Mục tiêu:** So sánh mức độ truyền dẫn giữa các trạng thái và giai đoạn thị trường.

Nội dung dự kiến:

- Calm so với Stress.
- Pre-2020 so với Post-2020.
- Rolling Sensitivity.
- Biểu đồ so sánh kết quả theo trạng thái và thời kỳ.

### Tab 4 – Forecast

**Mục tiêu:** Đánh giá khả năng dự báo biến động BTC/ETH.

Nội dung dự kiến:

- Biểu đồ Actual và Predicted.
- So sánh Elastic Net với Benchmark.
- Chỉ tiêu MAE và RMSE.
- Feature Importance hoặc hệ số mô hình.
- Bộ lọc tài sản và mô hình.

**Nguyên tắc:** Dashboard sử dụng dữ liệu và kết quả thực tế được xuất từ các file CSV. Không tự tạo số liệu mô hình hoặc khoảng tin cậy để hiển thị.

---

## 8. Hướng dẫn cài đặt môi trường

Các bước sau là hướng dẫn chuẩn bị môi trường phát triển. Lệnh chạy mô hình và dashboard sẽ được kiểm tra khi các thành viên hoàn thành mã nguồn.

### Bước 1: Clone repository

```bash
git clone https://github.com/ngocly1572006-tnnl/macro-crypto-shock-transmission.git
```

### Bước 2: Truy cập thư mục dự án

```bash
cd macro-crypto-shock-transmission
```

### Bước 3: Tạo môi trường Python

```bash
python -m venv .venv
```

### Bước 4: Kích hoạt môi trường

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### Bước 5: Cài đặt thư viện

```bash
python -m pip install -r requirements.txt
```

Danh sách thư viện sẽ được cập nhật trong quá trình tích hợp.

---

## 9. Hướng dẫn chạy dự án

### 9.1. Chạy Pipeline

Lệnh dự kiến:

```bash
python src/pipeline/14_run_pipeline.py
```

Pipeline dự kiến thực hiện các bước:

1. Đọc cấu hình nghiên cứu.
2. Thu thập dữ liệu.
3. Tiền xử lý dữ liệu.
4. Thống kê mô tả.
5. Ước lượng mô hình kinh tế lượng.
6. Chạy mô hình Machine Learning.
7. Xuất kết quả phục vụ báo cáo và Dashboard.

### 9.2. Chạy Dashboard

Lệnh dự kiến:

```bash
streamlit run dashboard/12_dashboard_app.py
```

Sau khi khởi động thành công, truy cập địa chỉ localhost do Streamlit cung cấp.

### 9.3. Chạy kiểm thử

Lệnh dự kiến:

```bash
python -m pytest tests/
```

**Lưu ý:** Các lệnh trên chỉ được xác nhận hoạt động sau khi mã nguồn tương ứng đã hoàn thiện và được kiểm thử.

---

## 10. Quy trình thực hiện nghiên cứu

```text
XÁC ĐỊNH CẤU HÌNH NGHIÊN CỨU
              |
              v
      THU THẬP DỮ LIỆU
              |
              v
      TIỀN XỬ LÝ DỮ LIỆU
              |
              v
       MODEL DATASET
              |
       +------+------+
       |             |
       v             v
  KINH TẾ LƯỢNG   MACHINE LEARNING
       |             |
       v             v
 VAR / IRF / LP   ELASTIC NET
 REGIME / ROLLING  BENCHMARK
       |             |
       v             v
   KẾT QUẢ CSV   KẾT QUẢ CSV
       |             |
       +------+------+
              |
              v
      STREAMLIT DASHBOARD
              |
              v
      BÁO CÁO NGHIÊN CỨU
```

---

## 11. Tiến độ dự án

| Thời gian | Công việc |
|---|---|
| 16/10/2026 | Chốt phạm vi nghiên cứu, phân công và cấu trúc GitHub |
| 17–18/10/2026 | Hoàn thiện cấu hình nghiên cứu và dữ liệu |
| 19–21/10/2026 | Triển khai mô hình kinh tế lượng và Machine Learning |
| 22/10/2026 | Tích hợp Dashboard và Pipeline |
| 23/10/2026 | Kiểm tra học thuật và kỹ thuật |
| 24/10/2026 | Kiểm thử tổng thể, hoàn thiện báo cáo |
| 25/10/2026 | Hoàn thiện và nộp sản phẩm |

---

## 12. Nguyên tắc quản lý và chất lượng dữ liệu

1. Sử dụng dữ liệu có nguồn truy xuất rõ ràng.
2. Ghi nhận đầy đủ đơn vị đo lường và phép biến đổi.
3. Thống nhất cấu trúc dữ liệu giữa các thành viên.
4. Không sử dụng dữ liệu tương lai trong dự báo.
5. Không tự tạo kết quả mô hình để hoàn thiện Dashboard.
6. Các bảng và biểu đồ phải nhất quán với kết quả Python.
7. Không tự ý thay đổi tên file hoặc cấu trúc thư mục đã thống nhất.
8. Các thành viên chịu trách nhiệm kiểm tra phần việc trước khi bàn giao.
9. TV6 phụ trách kiểm thử tích hợp và nghiệm thu kỹ thuật.
10. TV1 phụ trách kiểm tra tính nhất quán học thuật.

---

## 13. Trạng thái triển khai

| Hạng mục | Trạng thái |
|---|---|
| Đề tài và câu hỏi nghiên cứu | Đã thống nhất |
| Phạm vi dữ liệu 2018–2025 | Đã thống nhất |
| Phân công thành viên | Đã hoàn thành |
| Cấu trúc repository | Đã lên kế hoạch |
| Thu thập và xử lý dữ liệu | Đang triển khai |
| Mô hình kinh tế lượng | Chưa nghiệm thu |
| Machine Learning | Chưa nghiệm thu |
| Streamlit Dashboard | Chưa nghiệm thu |
| Báo cáo nghiên cứu | Đang triển khai |
| Kiểm thử và tích hợp | Chưa nghiệm thu |

Bảng trạng thái sẽ được cập nhật theo tiến độ thực tế của nhóm.

---

## 14. Lưu ý học thuật

Dự án được thực hiện nhằm mục đích nghiên cứu khoa học và học tập.

Các kết quả phân tích phản ánh mối quan hệ thống kê trong phạm vi dữ liệu và phương pháp nghiên cứu được sử dụng. Kết quả không mặc nhiên chứng minh quan hệ nhân quả và không được xem là khuyến nghị đầu tư.

---

**Tên dự án:** Global Financial Conditions and Cryptocurrency Markets  
**Giai đoạn nghiên cứu:** 2018–2025  
**Hạn hoàn thành:** 25/10/2026
