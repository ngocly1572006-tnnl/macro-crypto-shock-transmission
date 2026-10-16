
# PHÂN CÔNG CÔNG VIỆC – MACRO CRYPTO PROJECT

**Tên đề tài:** Global Financial Conditions and Cryptocurrency Markets: Nonlinear Transmission of Monetary, Dollar and Risk Shocks to Bitcoin and Ethereum

**Thời gian:** 16/10/2026 – 25/10/2026  
**Số thành viên:** 06  
**Nhánh làm việc:** main

## 1. Sản phẩm đầu ra

1. Bài nghiên cứu khoa học theo chuẩn tạp chí (DOCX/PDF).
2. Dashboard Streamlit trực quan hóa kết quả nghiên cứu.

## 2. Phân công thành viên

| TV | Phụ trách | Công việc chính | Deadline cuối |
|---|---|---|---|
| TV1 | Research & Academic Review | Tổng quan nghiên cứu, giả thuyết, tài liệu tham khảo; hỗ trợ TV6 kiểm tra học thuật | 23/10 |
| TV2 | Data & Statistics | Thu thập, làm sạch dữ liệu; thống kê mô tả; viết Data & Methodology | 19/10 |
| TV3 | Econometrics | VAR, IRF, Local Projection, Regime Analysis, Robustness | 21/10 |
| TV4 | Machine Learning | Feature Engineering, Elastic Net, benchmark, đánh giá dự báo | 21/10 |
| TV5 | Paper & Research Synthesis | Viết Discussion, Conclusion; tổng hợp và hoàn thiện paper | 24/10 |
| TV6 | Dashboard & Quality Control | Xây dựng dashboard, pipeline, kiểm thử và kiểm tra toàn bộ bài | 24/10 |

## 3. File cần bàn giao

### TV1 – Research & Academic Review
- `config/research_config.json`
- `src/research/01_research_config.py`
- `paper/references/references.bib`
- `docs/literature_matrix.xlsx`
- `paper/drafts/01_introduction_literature.docx`
- `docs/academic_review_checklist.md`

### TV2 – Data & Statistics
- `src/data/02_download_data.py`
- `src/data/03_preprocess_data.py`
- `src/data/04_descriptive_stats.py`
- `data/raw/crypto_macro_raw.csv`
- `data/processed/model_dataset.csv`
- `outputs/tables/descriptive_stats.csv`
- `outputs/tables/correlation_matrix.csv`
- `outputs/figures/crypto_price_trends.png`
- `outputs/figures/correlation_heatmap.png`
- `docs/data_dictionary.xlsx`
- `docs/data_source_log.xlsx`
- `paper/drafts/02_data_methodology.docx`

### TV3 – Econometrics
- `src/econometrics/05_var_irf.py`
- `src/econometrics/06_local_projection.py`
- `src/econometrics/07_regime_analysis.py`
- `src/econometrics/08_robustness.py`
- `outputs/model_results/var_results.csv`
- `outputs/model_results/irf_results.csv`
- `outputs/model_results/lp_results.csv`
- `outputs/model_results/regime_results.csv`
- `outputs/model_results/robustness_results.csv`
- `outputs/figures/irf_btc.png`
- `outputs/figures/irf_eth.png`
- `outputs/figures/lp_responses.png`
- `outputs/figures/regime_comparison.png`
- `paper/drafts/03_econometric_results.docx`

### TV4 – Machine Learning
- `src/ml/09_ml_features.py`
- `src/ml/10_ml_forecast.py`
- `src/ml/11_model_evaluation.py`
- `data/processed/ml_dataset.csv`
- `outputs/model_results/forecast_results.csv`
- `outputs/model_results/model_comparison.csv`
- `outputs/model_results/feature_importance.csv`
- `outputs/figures/forecast_comparison.png`
- `paper/drafts/04_ml_results.docx`

### TV5 – Paper & Research Synthesis
- `paper/drafts/05_discussion_conclusion.docx`
- `paper/final/research_paper_final.docx`
- `paper/final/research_paper_final.pdf`

### TV6 – Dashboard & Quality Control
- `README.md`
- `requirements.txt`
- `.gitignore`
- `docs/task_assignment.md`
- `dashboard/12_dashboard_app.py`
- `dashboard/13_dashboard_utils.py`
- `src/pipeline/14_run_pipeline.py`
- `tests/test_pipeline.py`
- `docs/integration_qa_checklist.md`

## 4. Mốc tiến độ chung

| Ngày | Công việc |
|---|---|
| 16–18/10 | Chốt nghiên cứu, cấu trúc GitHub, dữ liệu đầu vào |
| 19/10 | Hoàn thành Literature, Data, VAR/IRF V1 và ML dataset |
| 20/10 | Hoàn thành LP, Regime và dự báo ML V1 |
| 21/10 | Khóa kết quả mô hình V1 |
| 22/10 | Dashboard và pipeline V1 |
| 23/10 | Kiểm tra học thuật, kỹ thuật và tổng hợp paper |
| 24/10 | Hoàn thiện paper, dashboard và nghiệm thu |
| 25/10 | Chốt repository và nộp sản phẩm |

## 5. Quy trình làm việc trên GitHub

1. Tất cả thành viên làm việc trực tiếp trên nhánh `main`.
2. Mỗi thành viên chỉ chỉnh sửa các file thuộc phần mình phụ trách.
3. Trước khi làm việc, chạy `git pull origin main`.
4. Sau khi hoàn thành, commit với nội dung rõ ràng và push lên `main`.
5. Không sử dụng `git push --force`.
6. Không push file giả, API key, môi trường `.venv` hoặc dữ liệu nhạy cảm.
7. TV6 kiểm tra toàn bộ file, code, kết quả và dashboard.
8. TV1 hỗ trợ TV6 kiểm tra nội dung học thuật và tài liệu tham khảo.
9. Khi có lỗi, thành viên phụ trách phải tự sửa và cập nhật lại file.

## 6. Tiêu chí hoàn thành

Một công việc được xem là hoàn thành khi:

- File đã được push lên GitHub đúng đường dẫn.
- Nội dung file đúng yêu cầu được phân công.
- Code chạy được và kết quả được tạo từ dữ liệu thật.
- Bảng biểu, kết quả và nội dung paper nhất quán.
- TV6 đã kiểm tra và xác nhận; TV1 hỗ trợ phần học thuật.

**Lưu ý:** File có trên GitHub chưa đồng nghĩa với đã hoàn thành nếu chưa được kiểm tra.

