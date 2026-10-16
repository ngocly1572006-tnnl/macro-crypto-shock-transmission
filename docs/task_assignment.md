
# KẾ HOẠCH TRIỂN KHAI & PHÂN CÔNG CÔNG VIỆC

**Dự án:** Global Financial Conditions and Cryptocurrency Markets: Nonlinear Transmission of Monetary, Dollar and Risk Shocks to Bitcoin and Ethereum

**Thời gian thực hiện:** 16/10/2026 – 25/10/2026  
**Nhóm:** 06 thành viên  
**Repository:** `macro-crypto-shock-transmission`  
**Giai đoạn nghiên cứu:** 01/01/2018 – 31/12/2025

---

## 1. MỤC TIÊU NGHIÊN CỨU

Nghiên cứu phân tích sự truyền dẫn của điều kiện tài chính toàn cầu đến thị trường tiền mã hóa, tập trung vào Bitcoin (BTC) và Ethereum (ETH), thông qua ba chỉ báo: lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm (US2Y), chỉ số sức mạnh đồng USD (DXY hoặc proxy phù hợp) và chỉ số biến động VIX.

### 1.1. Câu hỏi nghiên cứu đã thống nhất

- **RQ1:** Biến động lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm có liên hệ với phản ứng lợi suất BTC/ETH như thế nào?
- **RQ2:** Biến động USD và VIX truyền dẫn đến BTC/ETH với độ lớn và thời gian phản ứng ra sao?
- **RQ3:** Mức độ nhạy cảm của BTC/ETH có thay đổi giữa giai đoạn trước năm 2020 và từ năm 2020 trở đi không?
- **RQ4:** Sự truyền dẫn có khác biệt giữa trạng thái thị trường bình thường (Calm) và căng thẳng (Stress) không?
- **RQ5:** Các biến tài chính toàn cầu có cải thiện khả năng dự báo biến động BTC/ETH ngoài mẫu so với mô hình benchmark hay không?

**Lưu ý:** RQ1–RQ5 đã được nhóm thống nhất. Các thành viên không tự ý thay đổi câu hỏi nghiên cứu.

### 1.2. Phạm vi dữ liệu

| Nội dung | Quy định |
|---|---|
| Thời gian | 01/01/2018 – 31/12/2025 |
| Tần suất | Dữ liệu ngày (Daily) |
| Tài sản | BTC, ETH |
| Biến tài chính | VIX, DXY hoặc USD proxy, US2Y |
| Pre-2020 | 2018–2019 |
| Post-2020 | 2020–2025 |
| ML Train/Validation | 2018–2024 |
| ML Test | 2025 |
| Ngôn ngữ lập trình | Python |
| Dashboard | Streamlit |
| Quản lý mã nguồn | GitHub |

US2Y là lợi suất trái phiếu Kho bạc Mỹ **kỳ hạn 2 năm**, không phải dữ liệu chỉ thu thập trong 2 năm.

Hai giai đoạn Pre/Post-2020 không cân bằng về số quan sát. Khi phân tích, cần báo cáo quy mô mẫu và thực hiện kiểm tra độ nhạy phù hợp.

### 1.3. Phương pháp nghiên cứu

- Thống kê mô tả và phân tích tương quan.
- Vector Autoregression (VAR) và Impulse Response Function (IRF).
- Local Projection (LP).
- Phân tích Calm/Stress.
- So sánh Pre/Post-2020.
- Rolling Regression và Robustness.
- Machine Learning: Elastic Net và mô hình benchmark.
- Đánh giá dự báo ngoài mẫu bằng MAE và RMSE.

Không mặc định biến động US2Y hoặc VAR innovation là cú sốc chính sách tiền tệ có quan hệ nhân quả.

---

## 2. BẢNG TỔNG HỢP PHÂN CÔNG

| Thành viên | Vai trò | Công việc chính | Số file |
|---|---|---|---:|
| Yến Nhi | Research & Academic Review | Cơ sở lý thuyết, Literature Review, giả thuyết H1–H5, Research Config, kiểm tra học thuật | 6 |
| Hoài Nhi | Data Engineering & Statistics | Thu thập, làm sạch dữ liệu 2018–2025, thống kê mô tả, Data Dictionary | 12 |
| Hải Bình | Econometric Modeling | VAR/IRF, LP, Calm/Stress, Pre/Post-2020, Rolling, Robustness | 17 |
| Mai Phương | ML & Forecasting | ML Features, Elastic Net, Benchmark, đánh giá dự báo ngoài mẫu | 9 |
| Lam Kiều | Paper & Research Synthesis | Discussion, Conclusion, tổng hợp và hoàn thiện báo cáo | 3 |
| Ngọc Ly | Dashboard, Pipeline & QA | Streamlit Dashboard, Pipeline, Tests, GitHub, nghiệm thu | 9 |
| **Tổng** | | | **56** |

---

## 3. PHÂN CÔNG CHI TIẾT

### TV1 – YẾN NHI
**Research & Academic Review**

**Nhiệm vụ:**

1. Tổng quan các nghiên cứu về ảnh hưởng của điều kiện tài chính toàn cầu đến BTC/ETH.
2. Xây dựng khung lý thuyết về cơ chế truyền dẫn của US2Y, USD và VIX.
3. Xây dựng giả thuyết H1–H5 tương ứng RQ1–RQ5 đã chốt.
4. Giải thích cơ sở lựa chọn dữ liệu 2018–2025 và phân kỳ 2020.
5. Xác định định nghĩa biến, đơn vị đo lường và cách xây dựng bộ chỉ báo tài chính toàn cầu.
6. Thiết lập cấu hình nghiên cứu thống nhất.
7. Lập Literature Matrix và tài liệu tham khảo.
8. Phối hợp TV6 kiểm tra nội dung học thuật của báo cáo.

**File bàn giao:**

| File | Deadline |
|---|---|
| `config/research_config.json` | 17/10 |
| `src/research/01_research_config.py` | 17/10 |
| `paper/references/references.bib` | 17/10 |
| `docs/literature_matrix.xlsx` | 19/10 |
| `paper/drafts/01_introduction_literature.docx` | 19/10 |
| `docs/academic_review_checklist.md` | 23/10 |

**Tiêu chí nghiệm thu:**

- Literature Review có nguồn nghiên cứu thật.
- Giả thuyết phù hợp RQ1–RQ5.
- Cấu hình xác định rõ giai đoạn 2018–2025.
- Định nghĩa biến và bộ chỉ báo thống nhất với TV2–TV4.
- Trích dẫn và tài liệu tham khảo nhất quán.

---

### TV2 – HOÀI NHI
**Data Engineering & Descriptive Statistics**

**Nhiệm vụ:**

1. Thu thập dữ liệu BTC, ETH, VIX, DXY hoặc USD proxy, US2Y từ 2018–2025.
2. Ghi rõ nguồn, đơn vị và thời điểm truy xuất dữ liệu.
3. Đồng bộ lịch giao dịch crypto 24/7 với lịch thị trường tài chính Mỹ.
4. Xử lý dữ liệu thiếu, dữ liệu trùng lặp và sai định dạng.
5. Tính lợi suất log BTC/ETH và các biến đổi tài chính cần thiết.
6. Tạo bộ dữ liệu chính cho TV3, TV4 và TV6.
7. Thống kê mô tả, tương quan và trực quan hóa dữ liệu.
8. Viết phần Data & Methodology liên quan đến dữ liệu.

**File bàn giao:**

| File | Deadline |
|---|---|
| `src/data/02_download_data.py` | 17/10 |
| `data/raw/crypto_macro_raw.csv` | 17/10 |
| `docs/data_source_log.xlsx` | 17/10 |
| `src/data/03_preprocess_data.py` | 18/10 |
| `data/processed/model_dataset.csv` | 18/10 |
| `docs/data_dictionary.xlsx` | 18/10 |
| `src/data/04_descriptive_stats.py` | 19/10 |
| `outputs/tables/descriptive_stats.csv` | 19/10 |
| `outputs/tables/correlation_matrix.csv` | 19/10 |
| `outputs/figures/crypto_price_trends.png` | 19/10 |
| `outputs/figures/correlation_heatmap.png` | 19/10 |
| `paper/drafts/02_data_methodology.docx` | 19/10 |

**Tiêu chí nghiệm thu:**

- Dữ liệu bao phủ 2018–2025 theo nguồn thực tế.
- Có Data Dictionary và Source Log.
- Có báo cáo số quan sát và dữ liệu thiếu.
- Dataset có ngày duy nhất, được sắp xếp đúng.
- Không dùng dữ liệu tương lai để lấp dữ liệu quá khứ.
- TV3, TV4 và TV6 đọc được dataset mà không phải tự sửa tên cột.

---

### TV3 – HẢI BÌNH
**Econometric Modeling**

**Nhiệm vụ:**

1. Xây dựng và ước lượng mô hình VAR.
2. Tính và trực quan hóa IRF cho BTC và ETH.
3. Thực hiện Local Projection.
4. So sánh phản ứng theo trạng thái Calm/Stress.
5. So sánh giai đoạn 2018–2019 với 2020–2025.
6. Thực hiện Rolling Regression để đánh giá độ nhạy thay đổi theo thời gian.
7. Kiểm tra Robustness và độ nhạy kết quả.
8. Xuất bảng kết quả, khoảng tin cậy và hình.
9. Viết phần Econometric Results.

**File bàn giao:**

| File | Deadline |
|---|---|
| `src/econometrics/05_var_irf.py` | 19/10 |
| `outputs/model_results/var_results.csv` | 19/10 |
| `outputs/model_results/irf_results.csv` | 19/10 |
| `outputs/figures/irf_btc.png` | 19/10 |
| `outputs/figures/irf_eth.png` | 19/10 |
| `src/econometrics/06_local_projection.py` | 20/10 |
| `src/econometrics/07_regime_analysis.py` | 20/10 |
| `outputs/model_results/lp_results.csv` | 20/10 |
| `outputs/model_results/regime_results.csv` | 20/10 |
| `outputs/figures/lp_responses.png` | 20/10 |
| `outputs/figures/regime_comparison.png` | 20/10 |
| `src/econometrics/08_robustness.py` | 21/10 |
| `src/econometrics/08_rolling_sensitivity.py` | 21/10 |
| `outputs/model_results/subperiod_results.csv` | 21/10 |
| `outputs/model_results/rolling_sensitivity.csv` | 21/10 |
| `outputs/model_results/robustness_results.csv` | 21/10 |
| `paper/drafts/03_econometric_results.docx` | 21/10 |

**Tiêu chí nghiệm thu:**

- Có kết quả VAR/IRF và LP.
- Có phân tích Calm/Stress và Pre/Post-2020.
- Có kết quả Rolling và Robustness.
- CSV thể hiện được biến phản ứng, biến tác động, horizon, estimate và CI khi được ước lượng.
- Có giải thích mô hình, số quan sát và giới hạn nhận diện.
- Kết quả CSV và hình PNG nhất quán.

---

### TV4 – MAI PHƯƠNG
**Machine Learning & Forecasting**

**Nhiệm vụ:**

1. Xây dựng đặc trưng ML từ dữ liệu đã xử lý.
2. Tạo các biến có độ trễ để tránh Data Leakage.
3. Xác định biến mục tiêu là proxy biến động BTC/ETH ngày tiếp theo.
4. Chia Train/Validation theo thời gian trong giai đoạn 2018–2024.
5. Sử dụng năm 2025 làm tập Test ngoài mẫu.
6. Xây dựng Elastic Net và mô hình Benchmark.
7. Đánh giá bằng MAE và RMSE.
8. Phân tích mức độ đóng góp của các biến tài chính toàn cầu.
9. Xuất kết quả dự báo, bảng so sánh và biểu đồ.
10. Viết phần ML Results.

**File bàn giao:**

| File | Deadline |
|---|---|
| `src/ml/09_ml_features.py` | 19/10 |
| `data/processed/ml_dataset.csv` | 19/10 |
| `src/ml/10_ml_forecast.py` | 20/10 |
| `outputs/model_results/forecast_results.csv` | 20/10 |
| `src/ml/11_model_evaluation.py` | 21/10 |
| `outputs/model_results/model_comparison.csv` | 21/10 |
| `outputs/model_results/feature_importance.csv` | 21/10 |
| `outputs/figures/forecast_comparison.png` | 21/10 |
| `paper/drafts/04_ml_results.docx` | 21/10 |

**Tiêu chí nghiệm thu:**

- Dự báo proxy biến động ngày kế tiếp cho BTC/ETH.
- Không sử dụng thông tin tương lai trong đặc trưng.
- Có Train/Validation và Test theo thời gian.
- Có kết quả Elastic Net và Benchmark trên cùng tập Test.
- Có Actual, Predicted, MAE và RMSE.
- Có kết quả CSV để TV6 trực quan hóa.

---

### TV5 – LAM KIỀU
**Paper & Research Synthesis**

**Nhiệm vụ:**

1. Tổng hợp kết quả nghiên cứu từ TV1–TV4.
2. Viết Discussion và giải thích ý nghĩa kinh tế của kết quả.
3. Trả lời lần lượt RQ1–RQ5 bằng kết quả thực nghiệm.
4. Viết Limitations và Conclusion.
5. Ghép các bản thảo thành báo cáo hoàn chỉnh.
6. Chuẩn hóa bảng, hình, trích dẫn và tài liệu tham khảo.
7. Xuất báo cáo Word và PDF.
8. Sửa lỗi theo phản hồi của TV1 và TV6.

**File bàn giao:**

| File | Deadline |
|---|---|
| `paper/drafts/05_discussion_conclusion.docx` | 23/10 |
| `paper/final/research_paper_final.docx` | 24/10 |
| `paper/final/research_paper_final.pdf` | 24/10 |

**Tiêu chí nghiệm thu:**

- Paper trả lời RQ1–RQ5.
- Không tự tạo hoặc suy diễn kết quả không có trong dữ liệu.
- Bảng, hình và số liệu khớp với kết quả Python.
- Có giới hạn nghiên cứu và kết luận rõ ràng.
- TV1 kiểm tra học thuật, TV6 nghiệm thu cuối.

---

### TV6 – NGỌC LY
**Dashboard, Pipeline & Quality Control**

**Nhiệm vụ:**

1. Quản lý cấu trúc repository và quy trình GitHub.
2. Xây dựng dashboard bằng Streamlit.
3. Tích hợp dữ liệu và kết quả của TV2–TV4.
4. Xây dựng pipeline chạy các bước nghiên cứu.
5. Xây dựng các bài kiểm thử.
6. Kiểm tra schema CSV, đường dẫn và dữ liệu thiếu.
7. Kiểm tra dashboard trên dữ liệu thật.
8. Kiểm tra tính nhất quán giữa dashboard và báo cáo.
9. Phản hồi lỗi cho thành viên phụ trách sửa.
10. Nghiệm thu repository trước khi nộp.

**File bàn giao:**

| File | Deadline |
|---|---|
| `README.md` | 18/10 |
| `requirements.txt` | 18/10 |
| `.gitignore` | 18/10 |
| `docs/task_assignment.md` | 18/10 |
| `dashboard/12_dashboard_app.py` | 22/10 |
| `dashboard/13_dashboard_utils.py` | 22/10 |
| `src/pipeline/14_run_pipeline.py` | 22/10 |
| `tests/test_pipeline.py` | 22/10 |
| `docs/integration_qa_checklist.md` | 24/10 |

**Tiêu chí nghiệm thu:**

- Dashboard chạy được bằng Streamlit.
- Có đủ 4 tab và các biểu đồ dựa trên dữ liệu thật.
- Bộ lọc hoạt động đúng với kết quả được bàn giao.
- Pipeline chạy được theo hướng dẫn README.
- Tests kiểm tra được dữ liệu, schema và các đầu ra quan trọng.
- Không có dữ liệu giả hoặc kết quả mô hình tự tạo.
- Dashboard và báo cáo thống nhất.

---

## 4. THIẾT KẾ DASHBOARD ĐẦU RA

Dashboard gồm 4 tab chính.

### Tab 1 – Overview

**Mục tiêu:** Tổng quan điều kiện tài chính toàn cầu và thị trường crypto.

**Nội dung:**

- Thời gian nghiên cứu và số quan sát.
- Biểu đồ giá BTC/ETH.
- Diễn biến VIX, USD Index và US2Y.
- Thống kê mô tả.
- Ma trận tương quan.
- Bộ lọc tài sản và thời gian nếu dữ liệu hỗ trợ.

**Nguồn dữ liệu:**

- `data/processed/model_dataset.csv`
- `outputs/tables/descriptive_stats.csv`
- `outputs/tables/correlation_matrix.csv`

### Tab 2 – Econometrics

**Mục tiêu:** Trực quan hóa phản ứng động của BTC/ETH trước các biến tài chính.

**Nội dung:**

- VAR/IRF.
- Local Projection.
- Đường phản ứng theo Horizon.
- Khoảng tin cậy khi có kết quả ước lượng.
- Bộ lọc Asset, Shock, Model và Horizon.

**Nguồn dữ liệu:**

- `outputs/model_results/var_results.csv`
- `outputs/model_results/irf_results.csv`
- `outputs/model_results/lp_results.csv`

### Tab 3 – Regime

**Mục tiêu:** Đánh giá tính phi tuyến và sự thay đổi độ nhạy.

**Nội dung:**

- So sánh Calm/Stress.
- So sánh Pre/Post-2020.
- Rolling Sensitivity.
- Biểu đồ so sánh hệ số và khoảng tin cậy.
- Bộ lọc Asset, Shock, Regime và Horizon.

**Nguồn dữ liệu:**

- `outputs/model_results/regime_results.csv`
- `outputs/model_results/subperiod_results.csv`
- `outputs/model_results/rolling_sensitivity.csv`

### Tab 4 – Forecast

**Mục tiêu:** Đánh giá khả năng cải thiện dự báo rủi ro crypto.

**Nội dung:**

- Dự báo biến động BTC/ETH.
- Biểu đồ Actual vs Predicted.
- So sánh Elastic Net và Benchmark.
- MAE và RMSE ngoài mẫu.
- Feature Importance hoặc hệ số đặc trưng.
- Bộ lọc Asset và Model.

**Nguồn dữ liệu:**

- `outputs/model_results/forecast_results.csv`
- `outputs/model_results/model_comparison.csv`
- `outputs/model_results/feature_importance.csv`

**Nguyên tắc:** Dashboard sử dụng CSV kết quả thật làm nguồn dữ liệu chính. PNG phục vụ báo cáo hoặc hiển thị phụ trợ, không thay thế CSV khi cần tương tác.

---

## 5. QUY ƯỚC DỮ LIỆU CHUNG

### 5.1. Dataset chính

File: `data/processed/model_dataset.csv`

Các cột đề xuất:

| Cột | Nội dung |
|---|---|
| `date` | Ngày quan sát |
| `btc_close` | Giá đóng cửa BTC |
| `eth_close` | Giá đóng cửa ETH |
| `btc_log_return` | Lợi suất log BTC |
| `eth_log_return` | Lợi suất log ETH |
| `vix` | Chỉ số VIX |
| `usd_index` | Chỉ số USD |
| `us2y` | Lợi suất TPCP Mỹ kỳ hạn 2 năm |
| `period` | pre_2020 hoặc post_2020 |

Các biến biến đổi, độ trễ và quy tắc xử lý dữ liệu phải được mô tả trong Data Dictionary.

### 5.2. Kết quả IRF/LP

File:

- `irf_results.csv`
- `lp_results.csv`

Các cột tối thiểu:

`response, shock, horizon, estimate, ci_lower, ci_upper, specification`

### 5.3. Kết quả Regime

File: `regime_results.csv`

Các cột tối thiểu:

`response, shock, regime, horizon, estimate, ci_lower, ci_upper`

### 5.4. Kết quả Pre/Post-2020

File: `subperiod_results.csv`

Các cột tối thiểu:

`response, shock, period, horizon, estimate, ci_lower, ci_upper`

Giá trị `period`:

- `pre_2020`
- `post_2020`

### 5.5. Rolling Sensitivity

File: `rolling_sensitivity.csv`

Các cột tối thiểu:

`date, asset, shock, rolling_beta, window, specification`

### 5.6. Kết quả ML

File: `forecast_results.csv`

Các cột tối thiểu:

`date, asset, target, actual, predicted, benchmark, split, model`

File: `model_comparison.csv`

Các cột tối thiểu:

`asset, model, metric, value, sample_period`

**Lưu ý:** TV2, TV3, TV4 và TV6 phải thống nhất schema trước khi triển khai chính thức. Nếu thay đổi tên cột, cần thông báo các thành viên liên quan.

---

## 6. TIẾN ĐỘ TRIỂN KHAI

| Ngày | Công việc | Phụ trách |
|---|---|---|
| **16/10** | Chốt phạm vi 2018–2025, phân công, cấu trúc repo và quy ước đầu ra | Cả nhóm |
| **17/10** | Research Config, dữ liệu raw, source log; chuẩn bị khung mô hình | TV1, TV2, TV3, TV4 |
| **18/10** | Khóa `model_dataset.csv` V1, Data Dictionary và schema dùng chung | TV2, TV3, TV4, TV6 |
| **19/10** | Literature/Data draft, VAR/IRF V1, ML Dataset | TV1–TV4 |
| **20/10** | LP, Calm/Stress, Pre/Post-2020, ML Forecast và Benchmark | TV3, TV4 |
| **21/10** | Khóa kết quả mô hình V1, CSV/PNG và bản thảo chuyên môn | TV3, TV4 |
| **22/10** | Hoàn thành Dashboard/Pipeline V1 và chạy Tests | TV6 |
| **23/10** | Review học thuật, kiểm tra kỹ thuật, ghép Paper, sửa lỗi | TV1, TV5, TV6 |
| **24/10** | Kiểm thử tổng thể, xuất DOCX/PDF, nghiệm thu | Cả nhóm |
| **25/10** | Dự phòng, hoàn thiện repository và nộp | TV6 phối hợp cả nhóm |

---

## 7. QUY TRÌNH LÀM VIỆC TRÊN GITHUB

1. Mỗi thành viên phụ trách đúng các file đã được phân công.
2. Trước khi chỉnh sửa cần cập nhật phiên bản mới nhất từ repository.
3. Commit rõ nội dung công việc.
4. Không tự ý thay đổi cấu trúc thư mục hoặc tên file đã thống nhất.
5. Thay đổi liên quan đến dữ liệu và schema phải thông báo TV2, TV3, TV4 và TV6.
6. Không sử dụng `git push --force`.
7. Không push `.venv`, API key, secrets hoặc dữ liệu giả.
8. TV6 kiểm tra kết quả sau mỗi mốc bàn giao.
9. Thành viên phụ trách phải tự sửa lỗi thuộc phần công việc của mình.

---

## 8. CHECKLIST NGHIỆM THU

### Dữ liệu

- [ ] Dữ liệu bao phủ giai đoạn 2018–2025 theo nguồn thực tế.
- [ ] Có Data Dictionary và Source Log.
- [ ] Dataset có schema thống nhất.
- [ ] Có thống kê mô tả và ma trận tương quan.
- [ ] Không có dữ liệu giả hoặc dữ liệu tương lai bị sử dụng sai.

### Kinh tế lượng

- [ ] Có kết quả VAR/IRF.
- [ ] Có kết quả Local Projection.
- [ ] Có phân tích Calm/Stress.
- [ ] Có so sánh Pre/Post-2020.
- [ ] Có Rolling Sensitivity và Robustness.
- [ ] Có bảng kết quả và khoảng tin cậy khi được ước lượng.

### Machine Learning

- [ ] Có ML Dataset.
- [ ] Có Elastic Net và Benchmark.
- [ ] Có Train/Validation/Test theo thời gian.
- [ ] Test ngoài mẫu năm 2025.
- [ ] Có MAE/RMSE.
- [ ] Không Data Leakage.

### Dashboard

- [ ] Streamlit chạy thành công.
- [ ] Tab Overview hiển thị đúng.
- [ ] Tab Econometrics hiển thị đúng.
- [ ] Tab Regime hiển thị đúng.
- [ ] Tab Forecast hiển thị đúng.
- [ ] Bộ lọc hoạt động với dữ liệu thật.
- [ ] Không lỗi thiếu file hoặc thiếu cột.
- [ ] Dashboard đọc được CSV do TV2–TV4 bàn giao.

### Báo cáo

- [ ] Có đầy đủ các bản thảo chuyên môn.
- [ ] Paper trả lời RQ1–RQ5.
- [ ] Số liệu paper khớp kết quả Python.
- [ ] Trích dẫn và tài liệu tham khảo đầy đủ.
- [ ] Có bản DOCX và PDF cuối.

### Tích hợp

- [ ] `requirements.txt` cài đặt thành công.
- [ ] Pipeline chạy được.
- [ ] Tests pass.
- [ ] README hướng dẫn chạy chính xác.
- [ ] Clone repository trên máy khác có thể tái lập kết quả.
- [ ] TV1 hoàn thành Academic Review.
- [ ] TV6 hoàn thành Integration QA.

---

## 9. NGUYÊN TẮC CHUNG

- RQ1–RQ5 đã chốt, không tự ý thay đổi.
- Giai đoạn nghiên cứu thống nhất là 2018–2025.
- Tất cả mô hình sử dụng dữ liệu có nguồn và có thể tái lập.
- Không diễn giải tương quan thống kê thành quan hệ nhân quả khi chưa có phương pháp nhận diện phù hợp.
- Không tạo CSV, PNG hoặc kết quả mô hình giả để hoàn thiện dashboard.
- Không thay đổi schema sau khi đã khóa nếu chưa thống nhất với các thành viên liên quan.
- Các phương pháp mở rộng như SVAR, Event Study, TVP-VAR, XGBoost hoặc LightGBM chỉ triển khai nếu còn thời gian và không ảnh hưởng tiến độ chính.

**Mốc quan trọng:** 18/10 khóa dataset và schema; 21/10 khóa kết quả mô hình V1; 22/10 dashboard V1; 24/10 nghiệm thu; 25/10 nộp sản phẩm.
