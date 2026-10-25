
# INTEGRATION & QUALITY ASSURANCE REPORT
## DỰ ÁN MACRO–CRYPTO SHOCK TRANSMISSION

**Dự án:** Global Financial Conditions and Cryptocurrency Markets  
**Giai đoạn nghiên cứu:** 2018–2025  
**Ngày tổng hợp:** 25/10/2026  
**Phụ trách tích hợp và QA:** TV6 – Ngọc Ly  
**Trạng thái dự án:** ĐÃ HOÀN THÀNH SẢN PHẨM NGHIÊN CỨU

---

## 1. TỔNG QUAN

Dự án nghiên cứu mối quan hệ giữa điều kiện tài chính toàn cầu và thị trường tiền mã hóa, tập trung vào phản ứng của Bitcoin (BTC) và Ethereum (ETH) trước những thay đổi của:

- Lợi suất trái phiếu Chính phủ Mỹ kỳ hạn 2 năm (US2Y).
- Chỉ số sức mạnh đồng USD (DXY proxy).
- Chỉ số biến động thị trường VIX.

Nghiên cứu được triển khai theo 5 câu hỏi nghiên cứu (RQ1–RQ5), kết hợp các phương pháp kinh tế lượng, phân tích trạng thái thị trường và mô hình học máy.

Nhóm đã hoàn thành các sản phẩm chính:

- Bộ dữ liệu nghiên cứu giai đoạn 2018–2025.
- Quy trình thu thập và tiền xử lý dữ liệu.
- Phân tích thống kê mô tả và tương quan.
- Các mô hình kinh tế lượng VAR/IRF và Local Projections.
- Phân tích trước/sau năm 2020.
- Phân tích trạng thái Calm/Stress.
- Kiểm định độ nhạy và điều chỉnh đa kiểm định.
- Mô hình dự báo Elastic Net và XGBoost.
- Dashboard trực quan hóa kết quả bằng Streamlit.
- Báo cáo nghiên cứu hoàn chỉnh.

Tài liệu này tổng hợp tình trạng bàn giao, kết quả kiểm thử kỹ thuật và các lưu ý khi đóng gói sản phẩm cuối cùng.

---

## 2. PHÂN CÔNG VÀ TÌNH TRẠNG HOÀN THÀNH

| Thành viên | Phụ trách | Tình trạng |
|---|---|---|
| TV1 – Yến Nhi | Research framework, literature review, research config, Chương 01 | Hoàn thành |
| TV2 – Hoài Nhi | Data engineering, preprocessing, descriptive statistics, Chương 02 | Hoàn thành |
| TV3 – Hải Bình | VAR/IRF, LP, Pre/Post, Calm/Stress, robustness, Chương 03 | Hoàn thành |
| TV4 – Mai Phương | ML features, Elastic Net, XGBoost, evaluation, Chương 04 | Hoàn thành |
| TV5 – Lam Kiều | Tổng hợp, thảo luận, kết luận, báo cáo final | Hoàn thành |
| TV6 – Ngọc Ly | Dashboard, GitHub, tích hợp hệ thống, tài liệu hướng dẫn và QA | Hoàn thành phần triển khai |

**Kết luận:** Các thành viên đã hoàn thành phần công việc và sản phẩm nghiên cứu theo phân công.

---

## 3. KIỂM TRA CẤU TRÚC REPOSITORY

### 3.1. Cấu hình nghiên cứu

- [x] Có `config/research_config.json`.
- [x] Có `src/research/01_research_config.py`.
- [x] Có cấu hình nghiên cứu phục vụ RQ1–RQ5.
- [x] Có cấu trúc thư mục phân tách dữ liệu, mô hình, dashboard và báo cáo.

**Kết quả:** ĐẠT – Kiểm tra cấu trúc.

### 3.2. Dữ liệu

Các file dữ liệu chính:

- [x] `data/raw/crypto_macro_raw.csv`
- [x] `data/raw/crypto_macro_raw.xlsx`
- [x] `data/processed/model_dataset.csv`
- [x] `data/processed/ml_dataset.csv`

Tài liệu dữ liệu:

- [x] `docs/data_dictionary.xlsx`
- [x] `docs/data_source_log.xlsx`
- [x] `docs/literature_matrix.xlsx`

Các bảng kết quả:

- [x] `outputs/tables/descriptive_stats.csv`
- [x] `outputs/tables/correlation_matrix.csv`
- [x] `outputs/tables/preprocessing_quality_report.csv`

**Kết quả:** ĐẠT – Các file dữ liệu và tài liệu hỗ trợ đã được bàn giao trong repository.

### 3.3. Mã nguồn kinh tế lượng

- [x] `src/econometrics/05_var_irf.py`
- [x] `src/econometrics/05_var_lag_diagnostics.py`
- [x] `src/econometrics/06_local_projection.py`
- [x] `src/econometrics/07_regime_analysis.py`
- [x] `src/econometrics/08_hac_sensitivity.py`
- [x] `src/econometrics/08_multiple_testing.py`
- [x] `src/econometrics/08_robustness.py`
- [x] `src/econometrics/08_rolling_sensitivity.py`
- [x] `src/econometrics/08_subperiod_difference.py`
- [x] `src/econometrics/08_var_sensitivity.py`

**Kết quả:** ĐẠT – Các module nghiên cứu RQ1–RQ4 đã được triển khai.

### 3.4. Mã nguồn học máy

- [x] `src/ml/09_ml_features.py`
- [x] `src/ml/10_ml_forecast.py`
- [x] `src/ml/11_model_evaluation.py`
- [x] `src/ml/ml_common.py`

**Kết quả:** ĐẠT – Các module nghiên cứu RQ5 đã được triển khai.

### 3.5. Dashboard và pipeline

- [x] `dashboard/12_dashboard_app.py`
- [x] `dashboard/13_dashboard_utils.py`
- [x] `.streamlit/config.toml`
- [x] `src/pipeline/14_run_pipeline.py`
- [x] `requirements.txt`
- [x] `README.md`

**Kết quả:** ĐẠT – Có đầy đủ cấu trúc mã nguồn để triển khai dashboard và kiểm tra đầu ra.

---

## 4. KIỂM TRA DỮ LIỆU NGHIÊN CỨU

### 4.1. Phạm vi dữ liệu

| Nội dung | Quy định |
|---|---|
| Thời gian nghiên cứu | 01/01/2018–31/12/2025 |
| Tài sản nghiên cứu | BTC, ETH |
| Biến vĩ mô | US2Y, DXY proxy, VIX |
| Tần suất crypto | Ngày lịch |
| Dữ liệu vĩ mô | Theo ngày có quan sát |
| Dữ liệu mô hình | `model_dataset.csv` |
| Dữ liệu học máy | `ml_dataset.csv` |

### 4.2. Các nội dung được kiểm tra tự động

- [x] Kiểm tra sự tồn tại của file dữ liệu.
- [x] Kiểm tra cấu trúc cột.
- [x] Kiểm tra ngày dữ liệu.
- [x] Kiểm tra tính liên tục của chuỗi ngày.
- [x] Kiểm tra giá BTC/ETH hợp lệ.
- [x] Kiểm tra biến lợi suất.
- [x] Kiểm tra cờ quan sát dữ liệu vĩ mô.
- [x] Kiểm tra cấu trúc target dự báo ngày tiếp theo.

**Kết quả:** PASS theo bộ kiểm thử tự động.

**Lưu ý:** Các kiểm thử này xác nhận những quy tắc dữ liệu được lập trình; không thay thế việc xác minh độc lập toàn bộ dữ liệu với nguồn công bố.

---

## 5. KIỂM TRA KẾT QUẢ KINH TẾ LƯỢNG

### 5.1. RQ1 – Phản ứng trước US2Y

Các kết quả được bàn giao:

- [x] Kết quả VAR/IRF.
- [x] Kết quả Local Projections.
- [x] Hệ số ước lượng và khoảng tin cậy.
- [x] Các kết quả kiểm định thống kê.

### 5.2. RQ2 – Vai trò của DXY và VIX

- [x] Kết quả phản ứng động.
- [x] Kết quả LP/IRF.
- [x] Kết quả điều chỉnh BH-FDR.
- [x] Biểu đồ phục vụ diễn giải.

### 5.3. RQ3 – So sánh trước/sau 2020

- [x] Có kết quả phân tích Pre-2020 và Post-2020.
- [x] Có kết quả kiểm định khác biệt.
- [x] Có điều chỉnh FDR.
- [x] Có kết quả rolling sensitivity.

### 5.4. RQ4 – Calm/Stress

- [x] Có kết quả phân tích trạng thái thị trường.
- [x] Có kiểm định khác biệt Calm/Stress.
- [x] Có kiểm định độ nhạy theo ngưỡng VIX.
- [x] Có kết quả robustness.

### 5.5. Kết quả QA tự động

Các kiểm thử bao gồm:

- Schema LP và horizon.
- Giá trị hệ số và khoảng tin cậy.
- P-value và FDR.
- Tính nhất quán giữa LP gốc và LP sau FDR.
- Đơn vị thời gian IRF.
- Kết quả Pre/Post.
- Kết quả kiểm định khác biệt.
- Cấu trúc trạng thái Calm/Stress.

**Kết quả:** PASS theo bộ kiểm thử tự động.

**Lưu ý học thuật:** Kết quả không có ý nghĩa thống kê không được diễn giải thành bằng chứng chắc chắn rằng không tồn tại mối quan hệ.

---

## 6. KIỂM TRA KẾT QUẢ HỌC MÁY – RQ5

### 6.1. Cấu trúc dự báo

**Biến mục tiêu:**

`|r(t+1)|` – Độ lớn tuyệt đối của lợi suất log ngày tiếp theo.

Các phương pháp:

- Historical30 benchmark.
- Elastic Net.
- XGBoost.

Các nhóm đặc trưng:

- Crypto-only.
- Crypto + Macro.

**Tập kiểm tra ngoài mẫu:** Năm 2025.

### 6.2. Kết quả bàn giao

- [x] `outputs/model_results/cv_tuning_results.csv`
- [x] `outputs/model_results/forecast_results.csv`
- [x] `outputs/model_results/forecast_significance.csv`
- [x] `outputs/model_results/model_comparison.csv`
- [x] `outputs/model_results/feature_importance.csv`

### 6.3. Kiểm tra tự động

- [x] Kiểm tra ngày dự báo.
- [x] Kiểm tra target không âm.
- [x] Kiểm tra dự báo ngoài mẫu năm 2025.
- [x] Kiểm tra cấu trúc dữ liệu dự báo.
- [x] Tính lại MAE/RMSE từ kết quả dự báo.
- [x] Đối chiếu MAE/RMSE với bảng tổng hợp.
- [x] Kiểm tra khoảng tin cậy bootstrap và kết luận thống kê.

**Kết quả:** PASS theo bộ kiểm thử tự động.

**Giới hạn kiểm thử:** Việc kiểm tra file kết quả chưa chứng minh toàn bộ quá trình tạo đặc trưng và tuning không có data leakage. Nội dung này cần được xác minh từ mã nguồn khi đánh giá khả năng tái lập.

---

## 7. KIỂM TRA DASHBOARD

### 7.1. Cấu trúc dashboard

Phiên bản repository được đối chiếu có 7 mục điều hướng:

| STT | Mục | Nội dung |
|---|---|---|
| 1 | Tổng quan | Thông tin thị trường và dữ liệu nghiên cứu |
| 2 | RQ1 | Phản ứng của BTC/ETH trước US2Y |
| 3 | RQ2 | Truyền dẫn từ DXY và VIX |
| 4 | RQ3 | So sánh trước/sau 2020 |
| 5 | RQ4 | Phân tích Calm/Stress |
| 6 | RQ5 | Dự báo bằng học máy |
| 7 | Dữ liệu & cách đọc | Giải thích dữ liệu, phương pháp và kết quả |

### 7.2. Kết quả kiểm tra

- [x] Có mã nguồn dashboard Streamlit.
- [x] Có module tiện ích hỗ trợ.
- [x] Có cấu hình Streamlit.
- [x] Có các file dữ liệu và kết quả phục vụ trực quan hóa.
- [x] Mã Python dashboard đã qua kiểm tra biên dịch cú pháp.
- [ ] Chưa có bằng chứng kiểm thử tương tác trực tiếp tất cả tab và bộ lọc trong môi trường kiểm tra hiện tại.

**Kết quả:** ĐÃ HOÀN THÀNH TRIỂN KHAI; kiểm thử giao diện tương tác chưa được xác nhận độc lập.

---

## 8. KIỂM TRA PIPELINE VÀ UNIT TEST

### 8.1. Pipeline

Lệnh kiểm tra:

```powershell
python .\src\pipeline\14_run_pipeline.py --check
```

**Kết quả đã ghi nhận:**

- [x] Pipeline chạy thành công.
- [x] Các file đầu ra bắt buộc được tìm thấy.
- [x] Header của 11 file đầu ra được kiểm tra thành công.

**Trạng thái:** PASS.

### 8.2. Automated tests

Lệnh kiểm tra:

```powershell
python -m pytest tests/test_pipeline.py -v
```

**Kết quả đã ghi nhận:**

| Chỉ tiêu | Kết quả |
|---|---|
| Tổng bài kiểm thử | 15 |
| Passed | 15 |
| Failed | 0 |
| Trạng thái | PASS |

**Kết luận:** Các kiểm thử tự động đã thực hiện đều đạt.

### 8.3. Phạm vi kiểm thử

Bộ kiểm thử bao gồm:

1. Sự tồn tại của các file quan trọng.
2. Ngày và tính liên tục của dữ liệu.
3. Schema dữ liệu nghiên cứu.
4. Quan sát vĩ mô và dữ liệu thiếu.
5. Target dự báo ngày tiếp theo.
6. Kết quả LP.
7. Tính nhất quán LP/FDR.
8. Đơn vị thời gian IRF.
9. Kết quả Pre/Post.
10. Kiểm định khác biệt Pre/Post.
11. Kết quả Calm/Stress.
12. Kiểm định khác biệt Calm/Stress.
13. Dự báo ngoài mẫu năm 2025.
14. MAE/RMSE và kết quả dự báo.
15. Khoảng tin cậy và kết quả kiểm định dự báo.

---

## 9. KIỂM TRA BÁO CÁO NGHIÊN CỨU

### 9.1. Tình trạng hoàn thành

Nhóm đã hoàn thành báo cáo nghiên cứu cuối cùng, bao gồm:

- [x] Chương 01 – Introduction & Literature Review.
- [x] Chương 02 – Data & Methodology.
- [x] Chương 03 – Econometric Results.
- [x] Chương 04 – Machine Learning Results.
- [x] Chương 05 – Discussion & Conclusion.
- [x] Tổng hợp báo cáo nghiên cứu final.
- [x] Hoàn thành sản phẩm báo cáo để bàn giao.

**Trạng thái:** ĐÃ HOÀN THÀNH.

### 9.2. Lưu ý đóng gói file trên GitHub

Trong ZIP được kiểm tra, hai đường dẫn:

- `paper/final/research_paper_final.docx`
- `paper/final/research_paper_final.pdf`

có file dung lượng 1 byte, không phải bản báo cáo đầy đủ.

Đây là vấn đề **đóng gói file trong repository**, không phản ánh tình trạng viết báo cáo của nhóm.

Báo cáo nghiên cứu đã được nhóm hoàn thành; cần bảo đảm phiên bản đầy đủ được lưu hoặc liên kết đúng khi bàn giao GitHub.

### 9.3. Phạm vi xác minh

Việc nhóm hoàn thành báo cáo được ghi nhận theo tình trạng bàn giao.

Chưa có bằng chứng đối chiếu độc lập từng bảng, hình và kết luận trong toàn bộ bản PDF với các CSV của repository. Do đó, không ghi nhận bước đối chiếu này là đã PASS.

---

## 10. TỔNG HỢP KẾT QUẢ QA

| Hạng mục | Tình trạng | Kết quả kiểm tra |
|---|---|---|
| Research framework | Hoàn thành | Có cấu hình và mã nguồn |
| Dữ liệu TV2 | Hoàn thành | Automated tests PASS |
| Kinh tế lượng TV3 | Hoàn thành | Automated tests PASS |
| Học máy TV4 | Hoàn thành | Automated tests PASS |
| Dashboard TV6 | Hoàn thành triển khai | Cú pháp hợp lệ; chưa kiểm thử UI trực tiếp |
| Báo cáo nghiên cứu | Hoàn thành | Đã ghi nhận bàn giao |
| Pipeline | Hoàn thành | PASS |
| Unit tests | Hoàn thành | 15/15 PASS |
| Tài liệu repository | Hoàn thành | Có README và tài liệu hỗ trợ |
| Đóng gói báo cáo final trong ZIP | Cần đồng bộ | File DOCX/PDF trong ZIP chưa hợp lệ |

### Đánh giá chung

**Sản phẩm nghiên cứu đã hoàn thành.**

Các thành phần chính gồm dữ liệu, mô hình kinh tế lượng, mô hình học máy, dashboard và báo cáo nghiên cứu đã được triển khai.

Kết quả kiểm tra kỹ thuật ghi nhận:

- Pipeline: PASS.
- Automated tests: 15/15 PASS.
- Dashboard Python syntax: PASS.

Những kết quả trên xác nhận tính hợp lệ của các thành phần trong phạm vi kiểm thử, không thay thế việc đánh giá toàn bộ chất lượng học thuật hoặc kiểm thử giao diện thực tế.

---

## 11. KẾT LUẬN NGHIỆM THU

Dự án **Global Financial Conditions and Cryptocurrency Markets** đã hoàn thành các sản phẩm nghiên cứu theo phân công của sáu thành viên.

Nhóm đã xây dựng được quy trình xử lý dữ liệu, triển khai các mô hình kinh tế lượng và học máy, trực quan hóa kết quả trên dashboard Streamlit và hoàn thành báo cáo nghiên cứu cuối cùng.

Bộ kiểm thử tự động đạt **15/15 bài kiểm thử**, trong khi pipeline kiểm tra các đầu ra bắt buộc đã chạy thành công.

### Trạng thái cuối cùng

**PROJECT STATUS: COMPLETED**

**AUTOMATED TEST STATUS: PASSED (15/15)**

**PIPELINE STATUS: PASSED**

**RESEARCH PAPER STATUS: COMPLETED**

**DASHBOARD IMPLEMENTATION STATUS: COMPLETED**

**FULL END-TO-END QA STATUS: NOT FULLY VERIFIED**

Các công việc còn lại liên quan đến việc đồng bộ file báo cáo final trên GitHub và xác minh giao diện trực tiếp, không phải viết lại nội dung nghiên cứu.

---

**Tài liệu tổng hợp bởi:** TV6 – Ngọc Ly  
**Ngày:** 25/10/2026  
**Mục đích:** Tài liệu tích hợp, kiểm tra chất lượng và bàn giao dự án.

