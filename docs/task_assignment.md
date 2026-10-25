
# PHÂN CÔNG CÔNG VIỆC & BÀN GIAO DỰ ÁN

**Dự án:** Global Financial Conditions and Cryptocurrency Markets — nghiên cứu mối liên hệ động giữa US2Y, DXY, VIX và lợi suất Bitcoin/Ethereum.  
**Nhóm:** 6 thành viên | **Thời gian triển khai:** 16–25/10/2026  
**Giai đoạn dữ liệu:** 01/01/2018–31/12/2025  
**Repository:** `macro-crypto-shock-transmission`  
**Tài liệu này:** Cập nhật theo cấu trúc repository bàn giao ngày 25/10/2026.

> **Quy ước trạng thái:** “Có trong repo” chỉ xác nhận file hiện diện trong ZIP được đối chiếu, **không đồng nghĩa** script đã chạy lại thành công hoặc kết quả đã qua kiểm thử độc lập. Những hạng mục cần kiểm tra tiếp được ghi rõ.

---

## 1. Mục tiêu và luồng triển khai

Dự án sử dụng dữ liệu BTC, ETH, US2Y, DXY (proxy) và VIX để trả lời 5 câu hỏi nghiên cứu:

| RQ | Câu hỏi chính | Nhóm phụ trách |
|---|---|---|
| **RQ1** | US2Y liên hệ như thế nào với lợi suất BTC/ETH? | TV1, TV3 |
| **RQ2** | DXY và VIX liên hệ như thế nào với phản ứng lợi suất BTC/ETH theo các khoảng thời gian? | TV1, TV3 |
| **RQ3** | Mối liên hệ có khác biệt giữa **2018–2019** và **2020–2025** không? | TV3 |
| **RQ4** | Mối liên hệ có khác biệt giữa **Calm** và **Stress** không? | TV3 |
| **RQ5** | Biến vĩ mô có cải thiện dự báo ngoài mẫu **độ lớn lợi suất log ngày kế tiếp** không? | TV4 |

**Luồng dữ liệu và báo cáo:**

```text
TV1: Research Config + Literature Review
                   |
TV2: Raw Data → model_dataset.csv → Thống kê mô tả
                   |
             +-----+-----+
             |           |
       TV3: RQ1–RQ4  TV4: RQ5
       Kinh tế lượng  Machine Learning
             |           |
             +-----+-----+
                   |
        TV5: Discussion + Paper 01→05
                   |
        TV6: Dashboard + QA + GitHub
```

**Nguyên tắc:** `model_dataset.csv` do TV2 tạo là dữ liệu chuẩn dùng chung; TV3 tự chọn mẫu hợp lệ theo mô hình, TV4 tạo `ml_dataset.csv` nhưng không ghi đè dữ liệu chuẩn. Không xem tương quan/IRF Cholesky là bằng chứng nhân quả đã được nhận diện.

---

## 2. Tổng hợp phân công

| Thành viên | Vai trò | Trách nhiệm chính |
|---|---|---|
| **TV1 – Yến Nhi** | Research & Academic Review | Lý thuyết, RQ/giả thuyết, config, tài liệu tham khảo, rà soát học thuật |
| **TV2 – Hoài Nhi** | Data Engineering & Statistics | Thu thập, xử lý dữ liệu, thống kê mô tả, data dictionary, Chương 02 |
| **TV3 – Hải Bình** | Econometric Modeling | VAR/IRF, LP, Pre/Post, Calm/Stress, FDR, rolling, robustness, Chương 03 |
| **TV4 – Mai Phương** | ML & Forecasting | ML dataset, Elastic Net, XGBoost, benchmark, đánh giá 2025, Chương 04 |
| **TV5 – Lam Kiều** | Paper & Research Synthesis | Chương 05, tổng hợp paper, trích dẫn, DOCX/PDF final |
| **TV6 – Ngọc Ly** | Dashboard, Integration & QA | Streamlit, tích hợp outputs, pipeline kiểm tra, README, GitHub, QA |

---

## 3. Chi tiết bàn giao theo thành viên

### TV1 – Yến Nhi | Research & Academic Review

**Công việc:** Xây dựng cơ sở lý thuyết và câu hỏi nghiên cứu, tổng hợp nghiên cứu trước, định nghĩa biến, quy tắc phân kỳ, cấu hình nghiên cứu; kiểm tra sự nhất quán học thuật giữa các chương.

**File đã có trong repo:**

```text
config/research_config.json
src/research/01_research_config.py
docs/literature_matrix.xlsx
docs/academic_review_checklist.md
paper/references/references.bib
paper/drafts/01_introduction_literature.docx
```

**Điểm cần đối chiếu cuối:** Câu chữ RQ2/RQ4 không hàm ý nhân quả hoặc mặc định Stress mạnh hơn; RQ5 phải nói đúng mục tiêu `|r(t+1)|`; tên đề tài và cách trích dẫn thống nhất trong config, paper, README và dashboard.

### TV2 – Hoài Nhi | Data Engineering & Statistics

**Công việc:** Thu thập dữ liệu 2018–2025; xử lý lịch crypto 7 ngày/tuần và lịch vĩ mô; tính lợi suất log và biến đổi vĩ mô; ghi nguồn dữ liệu; xuất dataset chuẩn, bảng thống kê và hình.

**File đã có trong repo:**

```text
src/data/02_download_data.py
src/data/03_preprocess_data.py
src/data/04_descriptive_stats.py
data/raw/crypto_macro_raw.csv
data/raw/crypto_macro_raw.xlsx
data/processed/model_dataset.csv
docs/data_source_log.xlsx
docs/data_dictionary.xlsx
outputs/tables/descriptive_stats.csv
outputs/tables/correlation_matrix.csv
outputs/tables/preprocessing_quality_report.csv
outputs/figures/crypto_price_trends.png
outputs/figures/correlation_heatmap.png
paper/drafts/02_data_methodology.docx
```

**Quy tắc bàn giao:** Không tự điền dữ liệu vĩ mô thiếu bằng 0 hoặc dữ liệu tương lai; giữ `NA` trong dữ liệu chuẩn; lợi suất crypto tính trước khi TV3 lọc mẫu; không ghi đè `model_dataset.csv` từ script TV3/TV4.

### TV3 – Hải Bình | Econometric Modeling

**Công việc:** Phân tích RQ1–RQ4 bằng VAR/IRF, LP, kiểm định khác biệt giai đoạn và trạng thái; BH-FDR; kiểm tra độ nhạy HAC, VAR, ngưỡng VIX 25/30/35; rolling sensitivity; viết Chương 03.

**Script đã có trong repo:**

```text
src/econometrics/05_var_irf.py
src/econometrics/05_var_lag_diagnostics.py
src/econometrics/06_local_projection.py
src/econometrics/07_regime_analysis.py
src/econometrics/08_hac_sensitivity.py
src/econometrics/08_multiple_testing.py
src/econometrics/08_robustness.py
src/econometrics/08_rolling_sensitivity.py
src/econometrics/08_subperiod_difference.py
src/econometrics/08_var_sensitivity.py
```

**Kết quả đã có trong repo:**

```text
outputs/model_results/var_results.csv
outputs/model_results/var_lag_diagnostics.csv
outputs/model_results/var_sensitivity_results.csv
outputs/model_results/irf_results.csv
outputs/model_results/lp_results.csv
outputs/model_results/lp_fdr.csv
outputs/model_results/lp_var_h0_comparison.csv
outputs/model_results/subperiod_results.csv
outputs/model_results/subperiod_difference_tests.csv
outputs/model_results/subperiod_difference_fdr.csv
outputs/model_results/regime_results.csv
outputs/model_results/regime_diagnostics.csv
outputs/model_results/regime_difference_fdr.csv
outputs/model_results/threshold_difference_fdr.csv
outputs/model_results/hac_sensitivity_results.csv
outputs/model_results/multiple_testing_summary.csv
outputs/model_results/robustness_results.csv
outputs/model_results/rolling_sensitivity.csv
outputs/figures/irf_btc.png
outputs/figures/irf_eth.png
outputs/figures/lp_responses.png
outputs/figures/regime_comparison.png
outputs/figures/rolling_sensitivity.png
paper/drafts/03_econometric_results.docx
```

**Quy tắc nghiệm thu:** Phân biệt rõ 2018–2025 (năm lịch) với `h=0…30` (khoảng thời gian phản ứng); khoảng tin cậy riêng cho từng ước lượng; kiểm định chênh lệch dựa trên kết quả kiểm định trực tiếp, không suy từ hai hệ số nhìn khác nhau; báo cáo p-value và q-value FDR đúng họ kiểm định.

### TV4 – Mai Phương | ML & Forecasting

**Công việc:** Tạo đặc trưng từ dữ liệu TV2; dự báo `|r(t+1)|` cho BTC/ETH; so sánh Crypto-only và Crypto + Macro; benchmark Historical30, Elastic Net, XGBoost; đánh giá ngoài mẫu năm 2025 và kiểm định chênh lệch sai số.

**File đã có trong repo:**

```text
src/ml/09_ml_features.py
src/ml/10_ml_forecast.py
src/ml/11_model_evaluation.py
src/ml/ml_common.py
data/processed/ml_dataset.csv
outputs/model_results/cv_tuning_results.csv
outputs/model_results/forecast_results.csv
outputs/model_results/forecast_significance.csv
outputs/model_results/model_comparison.csv
outputs/model_results/feature_importance.csv
outputs/figures/forecast_comparison.png
paper/drafts/04_ml_results.docx
```

**Quy tắc nghiệm thu:** Giữ năm 2025 làm test ngoài mẫu; không dùng thông tin 2025 để chọn siêu tham số; so sánh mô hình trên cùng tập ngày và cùng biến mục tiêu; không gọi `|r(t+1)|` là VaR/Expected Shortfall.

### TV5 – Lam Kiều | Paper & Research Synthesis

**Công việc:** Tổng hợp các chương 01–04, trả lời RQ1–RQ5, viết Discussion/Limitations/Conclusion, hoàn thiện danh mục trích dẫn, chuẩn hóa tiêu đề và đánh số bảng/hình, xuất bản báo cáo cuối.

**File đã có trong repo:**

```text
paper/drafts/05_discussion_conclusion_formatted_revised.docx
paper/final/research_paper_final.docx
paper/final/research_paper_final.pdf
paper/references/references.bib
```

**Quy tắc nghiệm thu:** Số liệu và kết luận phải khớp output TV3–TV4; diễn giải “chưa đủ bằng chứng sau FDR” thay vì “không có khác biệt”; thống nhất References; kiểm tra mục lục, đánh số mục và trích dẫn trước khi nộp.

### TV6 – Ngọc Ly | Dashboard, Integration & QA

**Công việc:** Quản lý repo, tích hợp outputs, phát triển Streamlit dashboard, viết README và tài liệu bàn giao, kiểm tra schema/đường dẫn/biểu đồ, đối chiếu paper với dashboard, hướng dẫn nhóm chạy dự án.

**File đã có trong repo:**

```text
README.md
requirements.txt
.gitignore
.streamlit/config.toml
dashboard/12_dashboard_app.py
dashboard/13_dashboard_utils.py
src/pipeline/14_run_pipeline.py
tests/test_pipeline.py
docs/integration_qa_checklist.md
docs/task_assignment.md
```

**Lưu ý tình trạng:** Dashboard trong ZIP đối chiếu có **7 mục điều hướng** (Tổng quan, RQ1–RQ5, Dữ liệu & cách đọc); tab **Kết luận & ứng dụng** của phiên bản chỉnh sửa sau chưa nằm trong ZIP này. `tests/test_pipeline.py` hiện là file rỗng; **chưa được đánh dấu kiểm thử tự động hoàn tất**. Script pipeline cần được mô tả đúng theo hành vi thực tế, không mặc định là chạy lại toàn bộ mô hình.

---

## 4. Chuẩn đầu ra dashboard

| Mục | Nội dung | Nguồn chính |
|---|---|---|
| Tổng quan | Xu hướng BTC/ETH, thống kê, tương quan | `model_dataset.csv`, `outputs/tables/`, `outputs/figures/` |
| RQ1 | LP, hệ số và khoảng tin cậy | `lp_results.csv`, `lp_fdr.csv` |
| RQ2 | Phản ứng động LP/VAR/IRF | `irf_results.csv`, `lp_results.csv` |
| RQ3 | 2018–2019 vs 2020–2025, rolling sensitivity | `subperiod_results.csv`, `subperiod_difference_fdr.csv`, `rolling_sensitivity.csv` |
| RQ4 | Calm/Stress, ngưỡng VIX | `regime_results.csv`, `regime_difference_fdr.csv` |
| RQ5 | Dự báo năm 2025, MAE/RMSE | `forecast_results.csv`, `model_comparison.csv`, `forecast_significance.csv` |
| Dữ liệu & cách đọc | Giải thích biến, phương pháp, giới hạn | Config và các bảng dữ liệu |
| Kết luận & ứng dụng | Tổng hợp 5 RQ, quy trình nhóm, hàm ý | Chương 05 và output thực tế; **chưa có trong bản ZIP đối chiếu** |

**Nguyên tắc giao diện:** Giữ nguyên phong cách Streamlit hiện tại khi sửa lỗi; các ô chọn phải hiển thị rõ; biểu đồ và KPI dùng cùng bộ lọc; không vẽ lại sai giá trị hoặc thay hệ số từ CSV. Trục năm chỉ áp dụng cho chuỗi thời gian; LP/IRF giữ trục số ngày phản ứng.

---

## 5. Quy ước dữ liệu và tích hợp

1. **Dữ liệu nguồn chuẩn:** `data/processed/model_dataset.csv` do TV2 phụ trách.
2. **Dữ liệu ML:** `data/processed/ml_dataset.csv` do TV4 tạo từ dữ liệu chuẩn.
3. **Kết quả kinh tế lượng:** `outputs/model_results/` do TV3 xuất; các CSV kiểm định FDR và robustness được giữ riêng.
4. **Kết quả ML:** `outputs/model_results/` do TV4 xuất; ghi rõ mô hình, tập đặc trưng, tài sản và tập đánh giá.
5. **Hình gốc:** `outputs/figures/`; dashboard có thể hiển thị cùng CSV tương tác, nhưng phải giữ nhất quán với kết quả gốc.
6. **Paper:** `paper/drafts/01…05` và `paper/final/` phải dùng cùng số liệu, tên biến, đơn vị và cách diễn giải.
7. **Thay đổi schema:** Thành viên sửa file đầu ra phải thông báo TV6 và cập nhật các thành phần phụ thuộc; không tự ý đổi tên cột hoặc ghi đè kết quả của người khác.

---

## 6. Mốc tiến độ đã phân công

| Mốc | Công việc | Phụ trách |
|---|---|---|
| **16–18/10** | Chốt RQ, config, nguồn dữ liệu, schema | TV1, TV2, cả nhóm |
| **19–21/10** | Chương 01–04, ước lượng VAR/LP, kiểm định, ML | TV1–TV4 |
| **22/10** | Tích hợp dashboard và pipeline phiên bản đầu | TV6 |
| **23–24/10** | Chương 05, ghép paper, rà soát học thuật/QA | TV1, TV5, TV6 |
| **25/10** | Hoàn thiện README, tài liệu phân công, kiểm tra nộp | Cả nhóm |

Các mốc trên là **kế hoạch phân công**, không tự động xác nhận toàn bộ hạng mục đã nghiệm thu.

---

## 7. Checklist nghiệm thu cuối

### Dữ liệu — TV2
- [x] Có raw data, `model_dataset.csv`, Data Dictionary và Source Log.
- [x] Có thống kê mô tả, tương quan và hình cơ sở.
- [ ] Kiểm tra lại khả năng tái lập khi tải dữ liệu mới và vấn đề timestamp.

### Kinh tế lượng — TV3
- [x] Có script và output VAR/IRF, LP, Pre/Post, Calm/Stress.
- [x] Có file FDR, rolling và robustness/sensitivity.
- [ ] Kiểm tra tự động CSV–hình–số liệu trong paper khớp từng lựa chọn.

### Machine Learning — TV4
- [x] Có Elastic Net, XGBoost, benchmark và output dự báo 2025.
- [x] Có so sánh mô hình và kiểm định sai số.
- [ ] Xác nhận tái lập toàn bộ quy trình tuning và đánh giá từ đầu.

### Paper — TV1, TV5
- [x] Có bản thảo 01–05 và bản final DOCX/PDF.
- [x] Có file `references.bib`.
- [ ] Rà soát lần cuối mục lục, số mục, trích dẫn và các tuyên bố thống kê.

### Dashboard & tích hợp — TV6
- [x] Có mã nguồn dashboard, utils, config giao diện và README.
- [x] Có script pipeline và checklist tích hợp.
- [ ] Kiểm thử thực tế tất cả bộ lọc/biểu đồ, đặc biệt hệ số–KPI–q-value RQ3.
- [ ] Bổ sung/đồng bộ tab Kết luận nếu dùng phiên bản 8 tab.
- [ ] Bổ sung test thực sự vào `tests/test_pipeline.py` (file hiện rỗng).
- [ ] Xác minh chạy được từ bản clone sạch trên máy khác.

**Ý nghĩa dấu kiểm:** `[x]` = đã xác nhận **có file/đầu ra trong ZIP**, `[ ]` = còn cần kiểm tra hoặc hoàn thiện. Không dùng `[x]` để tuyên bố đã pass test khi chưa chạy.

---

## 8. Quy tắc làm việc trên GitHub

- Mỗi thành viên chịu trách nhiệm các file đã phân công; ưu tiên pull trước khi sửa.
- Commit theo nội dung cụ thể, ví dụ `docs: update task assignment`, `fix: align RQ3 chart and KPI`.
- Không commit `.venv/`, API key, secret, dữ liệu giả hoặc file tạm.
- Không `git push --force` lên nhánh chung.
- Khi thay đổi dữ liệu/schema, thông báo TV2, TV3, TV4 và TV6.
- TV6 chịu trách nhiệm tích hợp; TV1 và TV5 đối chiếu nội dung học thuật trước khi chốt báo cáo.
- Không sửa số liệu hoặc kết luận chỉ để làm dashboard đẹp hơn.

---

## 9. Tiêu chí chốt sản phẩm

Dự án sẵn sàng bàn giao khi: (1) các file nguồn và output hiện diện; (2) dashboard chạy được với dữ liệu thật; (3) các bộ lọc, hệ số, CI, p/q-value và biểu đồ thống nhất; (4) paper và dashboard diễn giải cùng kết quả; (5) README hướng dẫn đúng lệnh chạy; và (6) các hạn chế về nhận diện nhân quả, FDR và thời điểm thông tin vĩ mô được công bố rõ.

**Trạng thái tại lần đối chiếu ZIP:** Đã có phần lớn thành phần nghiên cứu và báo cáo; **chưa xác nhận toàn bộ kiểm thử runtime và tái lập từ đầu**.
