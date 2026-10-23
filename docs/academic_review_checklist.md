
# ACADEMIC REVIEW CHECKLIST
## Điều kiện tài chính toàn cầu và thị trường tiền mã hóa

**Tên đề tài:** Điều kiện tài chính toàn cầu và thị trường tiền mã hóa: Phân tích mối liên hệ động và sự khác biệt theo trạng thái thị trường của Bitcoin và Ethereum.

**Giai đoạn nghiên cứu:** 01/01/2018–31/12/2025  
**Tần suất dữ liệu:** Hàng ngày, theo lịch UTC  
**Tài sản nghiên cứu:** Bitcoin (BTC) và Ethereum (ETH)  
**Biến tài chính toàn cầu:** Lợi suất Kho bạc Mỹ kỳ hạn 2 năm (US2Y), chỉ số USD (DXY) và chỉ số biến động thị trường (VIX).

---

## 1. Mục đích rà soát học thuật

Checklist này được sử dụng để rà soát tính nhất quán giữa câu hỏi nghiên cứu, cơ sở lý thuyết, dữ liệu, phương pháp kinh tế lượng, mô hình học máy và cách diễn giải kết quả.

Việc hoàn thành checklist không đồng nghĩa với việc nghiên cứu đã đạt chất lượng học thuật. Các nội dung cần được xác nhận bằng dữ liệu thực tế, mã nguồn, kết quả ước lượng và tài liệu tham khảo có thể kiểm chứng.

### Trạng thái rà soát

- [ ] Chưa kiểm tra
- [ ] Đã kiểm tra, cần chỉnh sửa
- [ ] Đã hoàn thành và có bằng chứng xác nhận
- [ ] Không áp dụng, kèm giải thích

Không đánh dấu hoàn thành chỉ vì nội dung đã được khai báo trong file cấu hình. Cần kiểm tra việc thực thi trong mã nguồn và kết quả nghiên cứu.

---

## 2. Câu hỏi nghiên cứu và giả thuyết

### RQ1 — US2Y và lợi suất BTC, ETH

**Câu hỏi:** Sự thay đổi lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 2 năm có liên hệ như thế nào với lợi suất BTC và ETH?

- [ ] Xác định rõ US2Y được đo bằng mức lợi suất hay sai phân bậc một.
- [ ] Thống nhất đơn vị đo US2Y giữa dữ liệu gốc, mô hình và báo cáo.
- [ ] Giải thích cơ sở lý thuyết liên hệ giữa điều kiện lãi suất Mỹ và tài sản tiền mã hóa.
- [ ] Kiểm tra dấu, độ lớn, mức ý nghĩa và khoảng tin cậy của hệ số.
- [ ] Phân biệt mối liên hệ thống kê với quan hệ nhân quả.
- [ ] Không gọi sai phân US2Y là cú sốc chính sách tiền tệ thuần túy khi chưa có chiến lược nhận diện phù hợp.

### RQ2 — DXY, VIX và thời gian truyền dẫn

**Câu hỏi:** Sự thay đổi DXY và VIX truyền sang thị trường tiền mã hóa trong bao lâu?

- [ ] Xác định rõ biến phụ thuộc, biến giải thích và chân trời phân tích.
- [ ] Phân biệt biến đổi DXY, biến đổi VIX và mức chỉ số gốc.
- [ ] Quy định rõ ý nghĩa của từng chân trời h trong Local Projections.
- [ ] Kiểm tra hệ số tại các chân trời h = 0 đến h = 30 ngày.
- [ ] Báo cáo khoảng tin cậy và phương pháp tính sai số chuẩn.
- [ ] Kiểm soát việc thực hiện nhiều phép kiểm định trên nhiều biến, tài sản và chân trời.
- [ ] Không kết luận tác động kéo dài nếu chỉ một số chân trời có ý nghĩa thống kê.
- [ ] Không diễn giải tương quan động hoặc phản ứng trong VAR thành tác động nhân quả nếu chưa đáp ứng giả định nhận diện.

### RQ3 — Khác biệt trước và sau năm 2020

**Câu hỏi:** Mức độ nhạy cảm của BTC và ETH với điều kiện tài chính toàn cầu có thay đổi sau năm 2020 không?

- [ ] Xác định trước mốc phân chia là ngày 01/01/2020.
- [ ] Phân chia mẫu trước năm 2020 (2018–2019) và từ năm 2020 trở đi (2020–2025).
- [ ] Giải thích lý do lựa chọn mốc phân chia.
- [ ] So sánh hệ số giữa hai giai đoạn bằng kiểm định phù hợp.
- [ ] Phân biệt việc một hệ số có ý nghĩa ở giai đoạn này nhưng không có ý nghĩa ở giai đoạn khác với việc hai hệ số thực sự khác nhau.
- [ ] Kiểm tra số quan sát và độ ổn định của kết quả trong từng giai đoạn.
- [ ] Báo cáo kết quả sau điều chỉnh kiểm định nhiều giả thuyết.
- [ ] Không mặc nhiên quy mọi khác biệt sau năm 2020 cho sự chấp nhận của nhà đầu tư tổ chức nếu chưa có thiết kế kiểm định riêng.

### RQ4 — Trạng thái căng thẳng thị trường

**Câu hỏi:** Tác động truyền dẫn có mạnh hơn trong giai đoạn căng thẳng hoặc biến động cao không?

- [ ] Định nghĩa Stress bằng VIX theo ngưỡng cố định.
- [ ] Sử dụng ngưỡng cơ sở 30 điểm VIX.
- [ ] Kiểm tra độ nhạy bằng ngưỡng 25 và 35 điểm.
- [ ] Xác định trạng thái bằng dữ liệu đã có sẵn tại thời điểm phân loại.
- [ ] Lưu ngày quan sát VIX được sử dụng để phân loại từng ngày crypto.
- [ ] Phân biệt ngày quan sát VIX mới với giá trị được giữ nguyên từ lần quan sát trước.
- [ ] Kiểm tra số quan sát trong nhóm Calm và Stress.
- [ ] Kiểm định trực tiếp sự khác biệt giữa hai trạng thái.
- [ ] Không kết luận có khác biệt chỉ dựa trên việc hệ số có ý nghĩa ở một nhóm nhưng không có ý nghĩa ở nhóm còn lại.
- [ ] Phân biệt trạng thái căng thẳng theo VIX với trạng thái biến động cao của chính BTC hoặc ETH.

### RQ5 — Khả năng dự báo rủi ro ngoài mẫu

**Câu hỏi:** Các biến tài chính toàn cầu có cải thiện khả năng dự báo rủi ro BTC và ETH ngoài mẫu không?

- [ ] Định nghĩa biến mục tiêu trước khi huấn luyện.
- [ ] Sử dụng mục tiêu hiện tại: giá trị tuyệt đối của lợi suất log ngày kế tiếp.
- [ ] Không mô tả mục tiêu này như VaR, Expected Shortfall hoặc xác suất thua lỗ.
- [ ] So sánh mô hình chỉ dùng đặc trưng crypto với mô hình bổ sung biến tài chính toàn cầu.
- [ ] Sử dụng cùng định nghĩa mục tiêu, cùng ngày đánh giá và cùng chân trời dự báo.
- [ ] Đánh giá riêng BTC và ETH.
- [ ] Báo cáo MAE và RMSE.
- [ ] Đánh giá liệu mức cải thiện có ổn định và có ý nghĩa thực tiễn hay không.
- [ ] Không khẳng định biến vĩ mô cải thiện dự báo nếu kết quả không hỗ trợ kết luận đó.

---

## 3. Rà soát dữ liệu và nguồn dữ liệu

### 3.1. Dữ liệu giá BTC và ETH

- [ ] Xác nhận nguồn dữ liệu giá và mã BTC-USD, ETH-USD.
- [ ] Xác nhận giá đóng cửa được sử dụng nhất quán.
- [ ] Chuẩn hóa ngày tháng theo UTC.
- [ ] Sắp xếp dữ liệu theo thời gian tăng dần.
- [ ] Kiểm tra ngày trùng lặp, giá thiếu, giá không dương và giá trị bất thường.
- [ ] Giữ lịch crypto liên tục, bao gồm cuối tuần và ngày lễ.
- [ ] Tính lợi suất log trên chuỗi ngày crypto liên tiếp trước khi lọc mẫu.
- [ ] Kiểm tra công thức:

  `r_t = 100 * ln(P_t / P_(t-1))`

- [ ] Ghi nhận số quan sát bị loại và lý do loại.

### 3.2. Dữ liệu vĩ mô

- [ ] Xác nhận nguồn và mã của US2Y, DXY và VIX.
- [ ] Ghi lại ngày quan sát, thời điểm công bố hoặc thời điểm dữ liệu thực sự sẵn có khi xác định được.
- [ ] Kiểm tra khác biệt lịch giao dịch giữa thị trường vĩ mô và thị trường crypto.
- [ ] Không coi giá trị vĩ mô được giữ nguyên vào cuối tuần là một quan sát mới.
- [ ] Không dùng dữ liệu tương lai để điền dữ liệu thiếu.
- [ ] Không nội suy hai chiều.
- [ ] Ghi nhận số lượng và tỷ lệ dữ liệu thiếu của từng biến.
- [ ] Đánh giá tác động của các phương án xử lý dữ liệu thiếu đến kết quả.

### 3.3. Quy tắc biến đổi

Các phép biến đổi phải được thống nhất giữa cấu hình, mã nguồn và báo cáo.

| Biến | Phép biến đổi | Công thức |
|---|---|---|
| BTC, ETH | Lợi suất log, tính theo % | `100 * ln(P_t / P_(t-1))` |
| US2Y | Sai phân bậc một | `US2Y_t - US2Y_(t-1)` |
| DXY | Sai phân log, tính theo % | `100 * ln(DXY_t / DXY_(t-1))` |
| VIX | Sai phân bậc một | `VIX_t - VIX_(t-1)` |

- [ ] Xác nhận US2Y được lưu theo đơn vị phần trăm, ví dụ 4.25 biểu thị 4,25%.
- [ ] Xác nhận sai phân US2Y được diễn giải theo điểm phần trăm.
- [ ] Xác nhận DXY và VIX có giá trị dương, hợp lệ trước khi biến đổi.
- [ ] Xác nhận cách xử lý quan sát đầu tiên và các khoảng thời gian thiếu.
- [ ] Không tính sai phân qua khoảng trống dữ liệu như thể hai quan sát cách nhau đúng một phiên.

---

## 4. Rà soát bộ dữ liệu dùng chung

### 4.1. model_dataset.csv

Đường dẫn chuẩn: `data/processed/model_dataset.csv`

- [ ] Chỉ có một bộ dữ liệu chuẩn dùng chung.
- [ ] Giữ lịch UTC liên tục của BTC và ETH.
- [ ] Có đủ dữ liệu giá và các biến nghiên cứu được quy định.
- [ ] Giữ lại dòng có BTC và ETH hợp lệ ngay cả khi biến vĩ mô bị thiếu.
- [ ] Có thông tin giúp nhận biết ngày quan sát vĩ mô và giá trị được giữ nguyên.
- [ ] Không lọc mẫu riêng cho từng mô hình ở bước tạo bộ dữ liệu chuẩn.
- [ ] Có báo cáo kiểm tra dữ liệu sau khi tạo file.
- [ ] TV3 và TV4 đọc file chuẩn, không ghi đè file gốc.
- [ ] Kiểm tra tính tái lập của quy trình tạo dữ liệu.

### 4.2. ml_dataset.csv

Đường dẫn chuẩn: `data/processed/ml_dataset.csv`

- [ ] Được tạo từ `model_dataset.csv`.
- [ ] Giữ lịch crypto bảy ngày mỗi tuần.
- [ ] Đặc trưng chỉ sử dụng thông tin có sẵn tại thời điểm dự báo.
- [ ] Biến mục tiêu được căn chỉnh với ngày dự báo.
- [ ] Không đưa giá, lợi suất hoặc thông tin ngày kế tiếp vào đặc trưng tại thời điểm t.
- [ ] Không sử dụng dữ liệu kiểm tra để lựa chọn đặc trưng hoặc siêu tham số.
- [ ] Có thể truy ngược mỗi dòng dự báo về dữ liệu đầu vào và ngày dự báo.
- [ ] Ghi rõ số quan sát bị loại do thiếu đặc trưng hoặc thiếu nhãn.

---

## 5. Rà soát phương pháp kinh tế lượng

### 5.1. VAR

- [ ] Xác định rõ các biến được đưa vào hệ VAR.
- [ ] Kiểm tra tính dừng của các chuỗi.
- [ ] Lựa chọn độ trễ theo tiêu chí và chẩn đoán phù hợp.
- [ ] Kiểm tra tính ổn định của hệ VAR.
- [ ] Kiểm tra tự tương quan phần dư và các vấn đề chẩn đoán liên quan.
- [ ] Giải thích thứ tự biến nếu sử dụng phân rã Cholesky.
- [ ] Kiểm tra độ nhạy của IRF với thứ tự biến.
- [ ] Báo cáo khoảng tin cậy của IRF và cách tính khoảng tin cậy.
- [ ] Không diễn giải IRF là quan hệ nhân quả nếu giả định nhận diện chưa được bảo vệ.
- [ ] Ghi rõ hạn chế của dữ liệu và giả định mô hình.

### 5.2. Local Projections

- [ ] Xác định biến phụ thuộc cho từng chân trời h.
- [ ] Xác định rõ biến giải thích và các biến kiểm soát.
- [ ] Quy định chân trời từ h = 0 đến h = 30 ngày.
- [ ] Mô tả cách tính hệ số, sai số chuẩn và khoảng tin cậy.
- [ ] Xem xét sự phụ thuộc theo thời gian và lựa chọn sai số chuẩn phù hợp.
- [ ] Kiểm tra số quan sát sử dụng ở từng chân trời.
- [ ] Xử lý việc kiểm định nhiều hệ số trên nhiều chân trời.
- [ ] Báo cáo hệ số, khoảng tin cậy và giá trị p hoặc q-value.
- [ ] Phân biệt thay đổi quan sát được của chỉ báo với cú sốc ngoại sinh đã được nhận diện.
- [ ] Không khẳng định quan hệ nhân quả vượt quá những gì thiết kế nghiên cứu hỗ trợ.

### 5.3. Kiểm định nhiều giả thuyết

- [ ] Liệt kê rõ nhóm kiểm định được điều chỉnh.
- [ ] Mô tả phương pháp điều chỉnh, ví dụ Benjamini–Hochberg nếu được sử dụng.
- [ ] Báo cáo cả kết quả chưa điều chỉnh và sau điều chỉnh.
- [ ] Xác định tiêu chí ý nghĩa thống kê trước khi diễn giải.
- [ ] Không chỉ lựa chọn những hệ số có ý nghĩa để báo cáo.
- [ ] Lưu kết quả đầy đủ để có thể tái lập.

---

## 6. Rà soát phân tích trước và sau năm 2020

- [ ] Xác định mốc 01/01/2020 trước khi ước lượng.
- [ ] Ghi rõ số quan sát trong mỗi giai đoạn.
- [ ] So sánh hệ số bằng kiểm định chênh lệch phù hợp.
- [ ] Không chỉ so sánh các giá trị p riêng lẻ giữa hai giai đoạn.
- [ ] Xem xét độ nhạy với đặc điểm mẫu và biến động thị trường.
- [ ] Điều chỉnh kiểm định nhiều giả thuyết nếu thực hiện nhiều phép kiểm định.
- [ ] Trình bày kết quả không có ý nghĩa thống kê một cách minh bạch.
- [ ] Phân biệt kết quả thực nghiệm với lời giải thích kinh tế được đề xuất.

Nếu thực hiện hồi quy cuốn chiếu 252 phiên, cần xác nhận rằng mã nguồn thực sự thực hiện phân tích này và báo cáo có trình bày kết quả tương ứng. Không mô tả phương pháp như đã được thực hiện nếu chưa có bằng chứng.

---

## 7. Rà soát trạng thái Calm và Stress

- [ ] Xác định Stress theo ngưỡng VIX cơ sở 30 điểm.
- [ ] Thực hiện kiểm tra độ nhạy với ngưỡng 25 và 35 điểm nếu đã cam kết trong thiết kế.
- [ ] Lưu ngày quan sát VIX dùng để phân loại từng ngày crypto.
- [ ] Không sử dụng dữ liệu VIX chưa có sẵn tại thời điểm phân loại.
- [ ] Báo cáo số quan sát của từng trạng thái.
- [ ] Kiểm tra liệu kết quả có bị chi phối bởi một số giai đoạn đặc biệt hay không.
- [ ] Kiểm định trực tiếp chênh lệch hệ số giữa Calm và Stress.
- [ ] Không suy diễn rằng VIX cao đồng nghĩa với BTC hoặc ETH chắc chắn có biến động cao.
- [ ] Nếu dùng thêm trạng thái biến động crypto, phải định nghĩa và kiểm định riêng.

---

## 8. Rà soát mô hình học máy

### 8.1. Mục tiêu và đặc trưng

- [ ] Mục tiêu là `abs(100 * ln(P_(t+1) / P_t))`.
- [ ] Đơn vị mục tiêu là phần trăm.
- [ ] Mục tiêu đại diện cho độ lớn lợi suất ngày kế tiếp, không phải trực tiếp là VaR hoặc Expected Shortfall.
- [ ] Xác định rõ đặc trưng crypto và đặc trưng vĩ mô.
- [ ] Đảm bảo các đặc trưng có thể quan sát tại thời điểm dự báo.
- [ ] Kiểm tra việc sử dụng giá trị vĩ mô được giữ nguyên.
- [ ] Không đưa biến mục tiêu hoặc biến được tính từ tương lai vào tập đặc trưng.

### 8.2. Chia dữ liệu và lựa chọn mô hình

- [ ] Chia dữ liệu theo thời gian, không xáo trộn ngẫu nhiên.
- [ ] Sử dụng giai đoạn 2018–2024 để huấn luyện và xác thực.
- [ ] Giữ năm 2025 làm tập kiểm tra cuối cùng.
- [ ] Sử dụng rolling-origin trong giai đoạn huấn luyện và xác thực nếu được triển khai.
- [ ] Thực hiện chuẩn hóa bên trong từng tập huấn luyện, không trên toàn bộ dữ liệu.
- [ ] Lựa chọn đặc trưng và siêu tham số mà không sử dụng tập kiểm tra cuối cùng.
- [ ] Dùng cùng ngày đánh giá cho các mô hình so sánh.
- [ ] Báo cáo kết quả riêng cho BTC và ETH.

### 8.3. So sánh mô hình

- [ ] Mô hình cơ sở chỉ sử dụng đặc trưng thị trường crypto.
- [ ] Mô hình bổ sung sử dụng đặc trưng crypto và biến tài chính toàn cầu.
- [ ] Cả hai mô hình dùng cùng định nghĩa mục tiêu.
- [ ] Báo cáo MAE và RMSE.
- [ ] Báo cáo chênh lệch sai số giữa mô hình bổ sung và mô hình cơ sở.
- [ ] Khi có thể, tính khoảng tin cậy cho chênh lệch sai số bằng phương pháp phù hợp với dữ liệu chuỗi thời gian.
- [ ] Không tuyên bố mô hình tốt hơn chỉ dựa trên một chỉ số hoặc một tài sản.
- [ ] Phân biệt cải thiện dự báo về mặt thống kê với cải thiện có ý nghĩa thực tiễn.
- [ ] Báo cáo kết quả bất lợi hoặc không có cải thiện.

---

## 9. Rà soát diễn giải kết quả

- [ ] Mỗi kết luận chính đều có bảng, hình hoặc kết quả định lượng hỗ trợ.
- [ ] Báo cáo dấu, độ lớn, khoảng tin cậy và ý nghĩa thống kê.
- [ ] Phân biệt ý nghĩa thống kê và ý nghĩa kinh tế.
- [ ] Không khái quát kết quả của BTC thành kết quả của ETH hoặc ngược lại.
- [ ] Không khẳng định mọi tác động đều âm hoặc dương nếu hệ số thay đổi theo chân trời.
- [ ] Không gọi quan hệ dự báo là quan hệ nhân quả.
- [ ] Nêu rõ kết quả không có ý nghĩa thống kê.
- [ ] Đối chiếu kết quả với nghiên cứu trước đó mà không ép kết quả phải phù hợp với kỳ vọng.
- [ ] Nêu các giải thích thay thế có thể có.
- [ ] Không đưa ra khuyến nghị đầu tư trực tiếp vượt quá phạm vi nghiên cứu.

---

## 10. Rà soát tài liệu tham khảo

- [ ] Mỗi trích dẫn trong bài đều có mục tương ứng trong danh mục tài liệu tham khảo.
- [ ] Mỗi mục trong danh mục tài liệu tham khảo đều được sử dụng trong nội dung hoặc có lý do giữ lại.
- [ ] Xác minh tên tác giả, năm, tiêu đề, tạp chí hoặc nhà xuất bản.
- [ ] Xác minh DOI hoặc đường dẫn khi có.
- [ ] Ưu tiên nguồn học thuật gốc cho lý thuyết và phương pháp.
- [ ] Phân biệt bài nghiên cứu đã xuất bản, bản thảo làm việc và tài liệu trực tuyến.
- [ ] Không trích dẫn tài liệu chưa đọc hoặc chưa xác minh.
- [ ] Không dùng một nguồn để hỗ trợ kết luận vượt quá nội dung nguồn đó.
- [ ] Dùng một chuẩn trích dẫn thống nhất trong toàn bài.

---

## 11. Khả năng tái lập nghiên cứu

- [ ] Lưu file cấu hình nghiên cứu.
- [ ] Lưu mã nguồn tạo dữ liệu và mã nguồn ước lượng.
- [ ] Ghi nhận nguồn dữ liệu, ngày tải và giai đoạn dữ liệu.
- [ ] Ghi nhận phiên bản thư viện và môi trường chạy.
- [ ] Lưu các tham số mô hình và tiêu chí lựa chọn mô hình.
- [ ] Lưu kết quả ước lượng, bảng và hình đầu ra.
- [ ] Có thể chạy lại quy trình từ dữ liệu đầu vào đến kết quả cuối.
- [ ] Kiểm tra các đường dẫn file hoạt động trên môi trường dự án.
- [ ] Không ghi đè dữ liệu chuẩn trong quá trình phân tích.
- [ ] Ghi lại mọi thay đổi quan trọng trong thiết kế sau khi đã bắt đầu phân tích.

---

## 12. Những giới hạn cần công khai

- [ ] Dữ liệu giá crypto và dữ liệu vĩ mô có lịch quan sát khác nhau.
- [ ] Thời điểm quan sát không nhất thiết trùng với thời điểm dữ liệu được công bố hoặc có sẵn.
- [ ] Sai phân US2Y không phải thước đo cú sốc chính sách tiền tệ đã được nhận diện.
- [ ] Thay đổi DXY và VIX không mặc nhiên là cú sốc ngoại sinh.
- [ ] Kết quả VAR/IRF phụ thuộc vào đặc tả mô hình và giả định nhận diện.
- [ ] Giai đoạn trước năm 2020 chỉ gồm 2018–2019 nên có thể hạn chế độ mạnh thống kê.
- [ ] Kết quả học máy phụ thuộc vào cách xây dựng đặc trưng, chia mẫu và lựa chọn siêu tham số.
- [ ] Giá trị tuyệt đối của lợi suất một ngày chỉ là thước đo đại diện cho độ lớn biến động trong ngày kế tiếp.
- [ ] Kết quả thực nghiệm trong giai đoạn 2018–2025 không tự động bảo đảm khả năng khái quát cho các giai đoạn khác.

Chỉ giữ những giới hạn thực sự liên quan đến thiết kế và kết quả cuối cùng; bổ sung các giới hạn khác nếu được phát hiện trong quá trình nghiên cứu.

---

## 13. Bảng tổng hợp phê duyệt cuối cùng

| Hạng mục | Trạng thái | Bằng chứng hoặc ghi chú |
|---|---|---|
| Câu hỏi và giả thuyết | Chưa kiểm tra | |
| Nguồn dữ liệu và thời điểm quan sát | Chưa kiểm tra | |
| Biến đổi và đơn vị đo | Chưa kiểm tra | |
| Chất lượng `model_dataset.csv` | Chưa kiểm tra | |
| Chất lượng `ml_dataset.csv` | Chưa kiểm tra | |
| Mô hình VAR và IRF | Chưa kiểm tra | |
| Local Projections | Chưa kiểm tra | |
| Phân tích trước/sau năm 2020 | Chưa kiểm tra | |
| Phân tích Calm/Stress | Chưa kiểm tra | |
| Mô hình Elastic Net và XGBoost | Chưa kiểm tra | |
| Đánh giá ngoài mẫu | Chưa kiểm tra | |
| Kiểm định nhiều giả thuyết | Chưa kiểm tra | |
| Tài liệu tham khảo | Chưa kiểm tra | |
| Khả năng tái lập | Chưa kiểm tra | |
| Diễn giải và giới hạn | Chưa kiểm tra | |

### Điều kiện hoàn tất

Nghiên cứu chỉ được đánh dấu hoàn tất sau khi:

1. Các kiểm tra trọng yếu có bằng chứng xác nhận.
2. Mã nguồn chạy được trên cấu hình đã công bố.
3. Kết quả trong báo cáo khớp với kết quả thực thi.
4. Các kết luận được giới hạn trong phạm vi mà dữ liệu và phương pháp hỗ trợ.
5. Các hạn chế và kết quả không thuận lợi được trình bày minh bạch.

**Ngày rà soát:** YYYY-MM-DD  
**Người rà soát:** ____________________  
**Phiên bản nghiên cứu:** ____________________  
**Kết luận rà soát:** Chưa phê duyệt / Cần chỉnh sửa / Đủ điều kiện hoàn tất
