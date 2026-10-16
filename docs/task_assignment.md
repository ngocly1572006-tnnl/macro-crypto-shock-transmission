
# KẾ HOẠCH TRIỂN KHAI & PHÂN CÔNG CÔNG VIỆC

**Dự án:** Global Financial Conditions and Cryptocurrency Markets: Nonlinear Transmission of Monetary, Dollar and Risk Shocks to Bitcoin and Ethereum

**Tên tiếng Việt:** Điều kiện tài chính toàn cầu và thị trường tiền mã hóa: Sự truyền dẫn phi tuyến của các cú sốc tiền tệ, đồng đô la Mỹ và rủi ro đến Bitcoin và Ethereum.

**Thời gian:** 16/10/2026 – 25/10/2026  
**Số thành viên:** 06  
**Repository:** https://github.com/ngocly1572006-tnnl/macro-crypto-shock-transmission

---

## 1. MỤC TIÊU VÀ THIẾT KẾ NGHIÊN CỨU

### 1.1. Mục tiêu

Nghiên cứu tác động và sự truyền dẫn động của các biến tài chính toàn cầu đến Bitcoin (BTC) và Ethereum (ETH), tập trung vào ba nhóm biến:

- **Lãi suất:** Lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm (US2Y).
- **Đồng USD:** Chỉ số DXY hoặc chỉ số USD thay thế có nguồn rõ ràng.
- **Rủi ro thị trường:** Chỉ số biến động VIX.

Nghiên cứu sử dụng các mô hình kinh tế lượng để đánh giá mức độ, thời gian và tính phi tuyến của phản ứng BTC/ETH. Đồng thời, Machine Learning được sử dụng để kiểm tra khả năng cải thiện dự báo biến động của thị trường tiền mã hóa.

Dự án có hai sản phẩm cuối cùng:

1. **Research Paper:** Bài nghiên cứu khoa học theo chuẩn tạp chí, định dạng DOCX/PDF.
2. **Macro–Crypto Shock Transmission Dashboard:** Dashboard Streamlit tương tác, hiển thị kết quả nghiên cứu thực tế.

### 1.2. Câu hỏi nghiên cứu

- **RQ1:** Biến động lợi suất TPCP Mỹ 2 năm có liên hệ với phản ứng lợi suất BTC/ETH như thế nào?
- **RQ2:** Biến động USD và VIX truyền sang BTC/ETH với mức độ và thời gian phản ứng ra sao?
- **RQ3:** Mức độ nhạy cảm của BTC/ETH có thay đổi giữa giai đoạn trước năm 2020 và từ năm 2020 trở đi không?
- **RQ4:** Phản ứng của BTC/ETH có khác biệt giữa trạng thái thị trường Calm và Stress không?
- **RQ5:** Các biến tài chính toàn cầu có cải thiện khả năng dự báo biến động BTC/ETH ngoài mẫu so với benchmark lịch sử không?

### 1.3. Phương pháp nghiên cứu

| Thành phần | Phương pháp |
|---|---|
| Tài sản nghiên cứu | BTC, ETH |
| Tần suất dữ liệu | Daily |
| Biến tài chính | VIX, DXY/proxy, US2Y |
| Tiền xử lý | Log returns, biến đổi chuỗi, đồng bộ lịch giao dịch, xử lý NA |
| Kinh tế lượng | VAR, IRF, Local Projection |
| Phi tuyến | Calm/Stress Regime Analysis |
| Thay đổi theo thời gian | Pre-2020/Post-2020, Rolling Regression |
| Kiểm định | Robustness/Sensitivity Analysis |
| Machine Learning | Elastic Net và historical benchmark |
| Mục tiêu ML | Dự báo biến động BTC/ETH ngày tiếp theo |
| Đánh giá ML | Chronological out-of-sample, MAE, RMSE |
| Dashboard | Python, Streamlit |
| Báo cáo | Research Paper DOCX/PDF |

**Lưu ý học thuật:** Biến động US2Y không tự động được xem là cú sốc chính sách tiền tệ có quan hệ nhân quả. Nếu không có phương pháp nhận diện phù hợp, chỉ diễn giải là biến động lợi suất hoặc điều kiện tài chính. Không đồng nhất tương quan, dự báo và quan hệ nhân quả.

---

## 2. PHÂN CÔNG CÔNG VIỆC CHO 6 THÀNH VIÊN

### TV1 – YẾN NHI
**Phụ trách:** Nghiên cứu & cơ sở lý thuyết

**Công việc chính:**
- Tìm kiếm, tổng hợp và đánh giá tài liệu nghiên cứu khoa học.
- Xây dựng khung lý thuyết về điều kiện tài chính toàn cầu và thị trường crypto.
- Xác định RQ1–RQ5, giả thuyết và biến nghiên cứu.
- Xây dựng cấu hình nghiên cứu và thống nhất định nghĩa biến với TV2.
- Viết Introduction & Literature Review.
- Theo dõi deadline và tiến độ các thành viên.
- Hỗ trợ TV6 kiểm tra nguồn, trích dẫn, lập luận và tính nhất quán học thuật.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 1 | `config/research_config.json` | 17/10 |
| 2 | `src/research/01_research_config.py` | 17/10 |
| 3 | `paper/references/references.bib` | 17/10 |
| 4 | `docs/literature_matrix.xlsx` | 19/10 |
| 5 | `paper/drafts/01_introduction_literature.docx` | 19/10 |
| 6 | `docs/academic_review_checklist.md` | 23/10 |

**Tổng:** 6 file.

**Tiêu chí nghiệm thu:** Câu hỏi và giả thuyết rõ ràng, nguồn học thuật xác thực, biến nghiên cứu thống nhất với dữ liệu và mô hình; hoàn thành checklist rà soát học thuật.

---

### TV2 – DỮ LIỆU & THỐNG KÊ
**Phụ trách:** Data Engineering & Descriptive Statistics

**Công việc chính:**
- Thu thập dữ liệu BTC, ETH, VIX, DXY/proxy và US2Y.
- Ưu tiên giai đoạn dữ liệu đủ dài để so sánh trước và sau năm 2020.
- Ghi lại nguồn, tần suất và thời điểm dữ liệu sẵn có.
- Đồng bộ lịch crypto 24/7 với ngày giao dịch tài chính.
- Xử lý dữ liệu thiếu, trùng lặp và sai định dạng.
- Tính toán log returns và các biến cần thiết.
- Thực hiện thống kê mô tả, ma trận tương quan và biểu đồ.
- Viết phần Data & Methodology.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 7 | `src/data/02_download_data.py` | 17/10 |
| 8 | `data/raw/crypto_macro_raw.csv` | 17/10 |
| 9 | `docs/data_source_log.xlsx` | 17/10 |
| 10 | `src/data/03_preprocess_data.py` | 18/10 |
| 11 | `data/processed/model_dataset.csv` | 18/10 |
| 12 | `docs/data_dictionary.xlsx` | 18/10 |
| 13 | `src/data/04_descriptive_stats.py` | 19/10 |
| 14 | `outputs/tables/descriptive_stats.csv` | 19/10 |
| 15 | `outputs/tables/correlation_matrix.csv` | 19/10 |
| 16 | `outputs/figures/crypto_price_trends.png` | 19/10 |
| 17 | `outputs/figures/correlation_heatmap.png` | 19/10 |
| 18 | `paper/drafts/02_data_methodology.docx` | 19/10 |

**Tổng:** 12 file.

**Tiêu chí nghiệm thu:** Dữ liệu có nguồn kiểm chứng, định nghĩa biến rõ ràng, không sử dụng thông tin tương lai; code có thể tạo lại các dataset, bảng và biểu đồ.

---

### TV3 – HẢI BÌNH
**Phụ trách:** Econometric Modeling

**Công việc chính:**
- Ước lượng VAR và Impulse Response Functions.
- Xây dựng Local Projections theo từng horizon.
- Phân tích Calm/Stress Regime.
- So sánh độ nhạy BTC/ETH trước và sau năm 2020.
- Thực hiện Rolling Regression để đo độ nhạy thay đổi theo thời gian.
- Kiểm định độ vững của kết quả.
- Trình bày ý nghĩa kinh tế và giới hạn nhận diện cú sốc.
- Viết phần Econometric Results.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 19 | `src/econometrics/05_var_irf.py` | 19/10 |
| 20 | `outputs/model_results/var_results.csv` | 19/10 |
| 21 | `outputs/model_results/irf_results.csv` | 19/10 |
| 22 | `outputs/figures/irf_btc.png` | 19/10 |
| 23 | `outputs/figures/irf_eth.png` | 19/10 |
| 24 | `src/econometrics/06_local_projection.py` | 20/10 |
| 25 | `src/econometrics/07_regime_analysis.py` | 20/10 |
| 26 | `outputs/model_results/lp_results.csv` | 20/10 |
| 27 | `outputs/model_results/regime_results.csv` | 20/10 |
| 28 | `outputs/figures/lp_responses.png` | 20/10 |
| 29 | `outputs/figures/regime_comparison.png` | 20/10 |
| 30 | `src/econometrics/08_robustness.py` | 21/10 |
| 31 | `src/econometrics/09_rolling_sensitivity.py` | 21/10 |
| 32 | `outputs/model_results/subperiod_results.csv` | 21/10 |
| 33 | `outputs/model_results/rolling_sensitivity.csv` | 21/10 |
| 34 | `outputs/model_results/robustness_results.csv` | 21/10 |
| 35 | `paper/drafts/03_econometric_results.docx` | 21/10 |

**Tổng:** 17 file.

**Tiêu chí nghiệm thu:** Kết quả VAR/IRF/LP có thể tái lập; có phân tích Regime, Sub-period, Rolling Sensitivity và Robustness; bảng/hình thống nhất; có khoảng tin cậy khi phương pháp cho phép và diễn giải đúng giới hạn nhận diện.

---

### TV4 – MACHINE LEARNING
**Phụ trách:** ML & Forecasting

**Công việc chính:**
- Tạo các biến dự báo có độ trễ.
- Xây dựng biến mục tiêu dự báo biến động BTC/ETH ngày tiếp theo.
- Huấn luyện Elastic Net.
- Xây dựng benchmark dự báo lịch sử.
- Chia train/test theo thời gian.
- Tránh data leakage và look-ahead bias.
- Đánh giá hiệu quả ngoài mẫu bằng MAE/RMSE.
- Trực quan hóa dự báo và viết ML Results.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 36 | `src/ml/09_ml_features.py` | 19/10 |
| 37 | `data/processed/ml_dataset.csv` | 19/10 |
| 38 | `src/ml/10_ml_forecast.py` | 20/10 |
| 39 | `outputs/model_results/forecast_results.csv` | 20/10 |
| 40 | `src/ml/11_model_evaluation.py` | 21/10 |
| 41 | `outputs/model_results/model_comparison.csv` | 21/10 |
| 42 | `outputs/model_results/feature_importance.csv` | 21/10 |
| 43 | `outputs/figures/forecast_comparison.png` | 21/10 |
| 44 | `paper/drafts/04_ml_results.docx` | 21/10 |

**Tổng:** 9 file.

**Tiêu chí nghiệm thu:** Target được định nghĩa rõ ràng; train/test theo thứ tự thời gian; Elastic Net và benchmark được đánh giá trên cùng tập test; kết quả không bị leakage.

---

### TV5 – HOÀI NHI
**Phụ trách:** Paper & Research Synthesis

**Công việc chính:**
- Viết Discussion, Conclusion và Limitations.
- Tổng hợp kết quả để trả lời RQ1–RQ5.
- Tích hợp các bản thảo của TV1–TV4.
- Chuẩn hóa thuật ngữ, bảng biểu, hình ảnh và tài liệu tham khảo.
- Biên tập bài theo cấu trúc nghiên cứu khoa học chuẩn tạp chí.
- Tiếp nhận phản hồi từ TV1 và TV6.
- Chịu trách nhiệm chính sản phẩm đầu ra 1: Research Paper.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 45 | `paper/drafts/05_discussion_conclusion.docx` | 23/10 |
| 46 | `paper/final/research_paper_final.docx` | 24/10 |
| 47 | `paper/final/research_paper_final.pdf` | 24/10 |

**Tổng:** 3 file.

**Tiêu chí nghiệm thu:** Paper hoàn chỉnh, trả lời RQ1–RQ5, số liệu khớp kết quả thực tế, trích dẫn có nguồn, định dạng thống nhất và được TV1/TV6 rà soát.

---

### TV6 – DASHBOARD, TÍCH HỢP & KIỂM TRA CHẤT LƯỢNG
**Phụ trách:** Dashboard, Pipeline & Quality Control

**Công việc chính:**
- Xây dựng cấu trúc GitHub repository.
- Chuẩn bị README, requirements và cấu hình Git.
- Xây dựng pipeline chạy các bước nghiên cứu.
- Tích hợp kết quả dữ liệu, kinh tế lượng và ML.
- Xây dựng Streamlit Dashboard gồm 4 tab:
  - Overview
  - Econometrics
  - Regime
  - Forecast
- Tạo bộ lọc Shock, Asset, Horizon và Regime.
- Hiển thị estimated responses, confidence intervals và kết quả dự báo thực tế.
- Viết tests và kiểm tra khả năng tái lập.
- Kiểm tra toàn bộ sản phẩm của 5 thành viên.
- Phối hợp TV1 kiểm tra học thuật.
- Chịu trách nhiệm chính sản phẩm đầu ra 2: Dashboard.

**File bàn giao:**

| STT | File | Deadline |
|---|---|---|
| 48 | `README.md` | 18/10 |
| 49 | `requirements.txt` | 18/10 |
| 50 | `.gitignore` | 18/10 |
| 51 | `docs/task_assignment.md` | 18/10 |
| 52 | `dashboard/12_dashboard_app.py` | 22/10 |
| 53 | `dashboard/13_dashboard_utils.py` | 22/10 |
| 54 | `src/pipeline/14_run_pipeline.py` | 22/10 |
| 55 | `tests/test_pipeline.py` | 22/10 |
| 56 | `docs/integration_qa_checklist.md` | 24/10 |

**Tổng:** 9 file.

**Tiêu chí nghiệm thu:** Pipeline, tests và dashboard chạy được trên máy sạch; bộ lọc hoạt động với kết quả thật; không lỗi thiếu file/cột; kết quả paper khớp CSV/PNG; TV6 duyệt cuối trước ngày nộp.

---

## 3. TỔNG HỢP SỐ LƯỢNG FILE

| Thành viên | Số file | Vai trò |
|---|---:|---|
| TV1 – Yến Nhi | 6 | Research & Academic Review |
| TV2 | 12 | Data Engineering |
| TV3 – Hải Bình | 17 | Econometric Modeling |
| TV4 | 9 | Machine Learning |
| TV5 – Hoài Nhi | 3 | Paper & Research Synthesis |
| TV6 | 9 | Dashboard & Quality Control |
| **TỔNG** | **56** | **06 thành viên** |

**Lưu ý:** Số lượng file không phản ánh hoàn toàn khối lượng công việc. TV5 chịu trách nhiệm tổng hợp Research Paper, TV6 chịu trách nhiệm tích hợp và nghiệm thu hệ thống.

---

## 4. TIẾN ĐỘ TRIỂN KHAI 16–25/10/2026

| Ngày | Công việc | Phụ trách |
|---|---|---|
| 16/10 | Kickoff, thống nhất phạm vi, cấu trúc repo và schema | Cả nhóm |
| 17/10 | Chốt research config, dữ liệu thô và nguồn; dựng khung mô hình | TV1, TV2, TV3, TV4 |
| 18/10 | Khóa dataset V1, data dictionary, hoàn thiện repo cơ bản | TV2, TV6 |
| 19/10 | Literature/Data drafts, VAR/IRF V1, ML features | TV1–TV4 |
| 20/10 | Local Projection, Regime/Sub-period, ML forecast | TV3, TV4 |
| 21/10 | Hoàn thiện Rolling Regression, Robustness, kết quả ML; khóa output V1 | TV3, TV4 |
| 22/10 | Hoàn thiện Dashboard/Pipeline V1 và kiểm thử | TV6 |
| 23/10 | Academic Review, Integration QA, tổng hợp paper | TV1, TV5, TV6 |
| 24/10 | Kiểm tra toàn bộ hệ thống, hoàn thiện paper DOCX/PDF | Cả nhóm |
| 25/10 | Dự phòng, xử lý lỗi cuối và nộp sản phẩm | Cả nhóm |

**Các mốc quan trọng:**

- **18/10:** Khóa cấu trúc dataset và tên biến.
- **21/10:** Khóa kết quả mô hình phiên bản V1.
- **22/10:** Dashboard và pipeline phiên bản V1.
- **24/10:** Nghiệm thu Research Paper và Dashboard.
- **25/10:** Hoàn tất bàn giao.

---

## 5. QUY TRÌNH LÀM VIỆC TRÊN GITHUB

### 5.1. Nguyên tắc chung

- Cả 6 thành viên làm việc trực tiếp trên nhánh `main`.
- Mỗi thành viên chỉ chỉnh sửa các file thuộc phần việc được giao.
- Trước khi bắt đầu sửa hoặc push phải cập nhật code mới nhất từ repository.
- Không sử dụng `git push --force`.
- Không ghi đè file của thành viên khác khi chưa thống nhất.
- TV6 kiểm tra kết quả sau mỗi đợt bàn giao.
- Nếu có lỗi, thành viên phụ trách phải tự sửa phần của mình.
- TV1 hỗ trợ kiểm tra học thuật; TV6 kiểm tra kỹ thuật và nghiệm thu cuối.

### 5.2. Các lệnh Git cơ bản

Cập nhật repository:

```bash
git pull origin main
```

Kiểm tra thay đổi:

```bash
git status
```

Thêm file đã chỉnh sửa:

```bash
git add <duong-dan-file>
```

Commit:

```bash
git commit -m "Update assigned research files"
```

Push lên GitHub:

```bash
git push origin main
```

### 5.3. Quy định dữ liệu và bảo mật

- Không push `.venv/`, `.env`, API keys, mật khẩu hoặc thông tin bí mật.
- Không tạo CSV, PNG, DOCX hoặc PDF giả để đủ số lượng file.
- Các file dữ liệu và kết quả phải được tạo từ dữ liệu thật hoặc nội dung nghiên cứu thật.
- Thư mục chưa có file sử dụng `.gitkeep` nếu cần.
- Tên file và đường dẫn phải đúng theo phân công.
- Khi thay đổi schema, phải thông báo TV2, TV3, TV4 và TV6.

---

## 6. HỢP ĐỒNG DỮ LIỆU VÀ ĐẦU RA

Để dashboard tích hợp được với các mô hình, các thành viên phải thống nhất định dạng dữ liệu.

| File | Các trường thông tin tối thiểu |
|---|---|
| `model_dataset.csv` | date, BTC/ETH prices/returns, VIX, DXY/proxy, US2Y |
| `irf_results.csv` | response, shock, horizon, estimate, ci_lower, ci_upper, specification |
| `lp_results.csv` | response, shock, horizon, estimate, ci_lower, ci_upper, specification |
| `regime_results.csv` | response, shock, regime, horizon, estimate, ci_lower, ci_upper |
| `subperiod_results.csv` | response, shock, period, horizon, estimate, ci_lower, ci_upper |
| `rolling_sensitivity.csv` | date, asset, shock, rolling_beta, window, specification |
| `forecast_results.csv` | date, asset, target, actual, predicted, benchmark, split, model |
| `model_comparison.csv` | asset, model, metric, value, sample_period |
| `figures/*.png` | Hình xuất từ code với tên file thống nhất |

**Quy định:**

- TV1 và TV2 thống nhất tên biến, định nghĩa và cách biến đổi dữ liệu trước 18/10.
- TV3 và TV4 sử dụng dataset đã được chuẩn hóa.
- TV6 đọc kết quả từ CSV/PNG thật, không tự tạo kết quả nghiên cứu.
- Định nghĩa mục tiêu dự báo biến động phải được ghi rõ trong `research_config.json` và `data_dictionary.xlsx`.
- Dữ liệu dùng cho dự báo phải tuân thủ nguyên tắc point-in-time, tránh look-ahead bias.

---

## 7. CHECKLIST NGHIỆM THU CUỐI CÙNG

### 7.1. Research Paper

- [ ] Có đủ 5 bản thảo của TV1–TV5.
- [ ] Có file DOCX/PDF cuối cùng.
- [ ] Bài nghiên cứu trả lời RQ1–RQ5.
- [ ] Nguồn và tài liệu tham khảo được kiểm chứng.
- [ ] Bảng, hình và số liệu thống nhất với kết quả code.
- [ ] Có giải thích ý nghĩa kinh tế và giới hạn nghiên cứu.
- [ ] Không đưa ra kết luận nhân quả khi chưa có phương pháp nhận diện phù hợp.
- [ ] TV1 hoàn thành Academic Review.
- [ ] TV5 hoàn thành biên tập và định dạng chuẩn tạp chí.

### 7.2. Dashboard & Code

- [ ] Repository có đầy đủ các file theo phân công.
- [ ] Cài đặt thành công từ `requirements.txt`.
- [ ] Pipeline có thể chạy lại.
- [ ] Dataset và kết quả được tạo từ dữ liệu thật.
- [ ] Dashboard mở đủ 4 tab.
- [ ] Bộ lọc Shock/Asset/Horizon/Regime hoạt động.
- [ ] Biểu đồ IRF/LP hiển thị kết quả và khoảng tin cậy khi có.
- [ ] Dashboard hiển thị Regime, Sub-period và Rolling Sensitivity.
- [ ] ML có benchmark và kiểm định ngoài mẫu.
- [ ] Không có data leakage hoặc look-ahead bias.
- [ ] Tests chạy thành công.
- [ ] README hướng dẫn chạy đúng thực tế.
- [ ] Không có API key hoặc thông tin bí mật trong repository.
- [ ] TV6 hoàn thành Integration QA và nghiệm thu cuối.

---

## 8. NGUYÊN TẮC BÀN GIAO

1. Thành viên hoàn thành file đúng deadline và push lên GitHub.
2. TV1 theo dõi tiến độ, nhắc deadline và rà soát nội dung học thuật.
3. TV6 kiểm tra kỹ thuật, schema, code và tính tái lập.
4. Nếu phát hiện lỗi, người phụ trách phải sửa và cập nhật lại file.
5. TV5 tổng hợp các kết quả đã kiểm tra để hoàn thiện Research Paper.
6. TV6 tích hợp kết quả vào Dashboard và chạy kiểm thử cuối.
7. Cả nhóm nghiệm thu hai sản phẩm trước ngày 25/10/2026.

**Nguyên tắc cuối cùng:** Ưu tiên mô hình có kết quả đáng tin cậy, không leakage, có benchmark và có thể tái lập hơn mô hình phức tạp nhưng không kiểm chứng được.

**Các mô hình mở rộng nếu còn thời gian:** Structural VAR, FOMC Event Study, TVP-VAR, Markov-switching, Quantile Regression, XGBoost và LightGBM. Không xem đây là điều kiện bắt buộc trong thời hạn 10 ngày.
