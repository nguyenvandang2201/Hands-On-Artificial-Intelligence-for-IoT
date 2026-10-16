# HƯỚNG DẪN THUYẾT TRÌNH – CHẠY CODE CHƯƠNG 11
### Phân loại tội phạm San Francisco bằng PySpark

| | |
|---|---|
| **Thời lượng dự kiến** | 8–10 phút (trong đó chạy code khoảng 1 phút) |
| **File cần mở** | `Chapter11/SF_crime_category_detection_spark4.ipynb` trong VS Code |
| **Kernel** | Python 3.12 (Spark - Chuong 11) |
| **Tài liệu chi tiết** | [Báo cáo chạy code](Bao_cao_chay_code_Chuong_11.md), [Báo cáo nội dung](Bao_cao_noi_dung_Chuong_11.md) |

---

## Chuẩn bị trước buổi thuyết trình

- [ ] Có file `sf_crime_dataset.csv` trong thư mục `Chapter11` (bản sao của `train.csv`).
- [ ] Mở notebook, chọn kernel, rồi **chạy thử một lần** (Run All, khoảng 30 giây) để chắc chắn mọi thứ hoạt động.
- [ ] Trước khi lên trình bày, bấm **Clear All Outputs** để chạy lại từng ô trước lớp. Bản đã có sẵn kết quả vẫn còn trên GitHub để dự phòng.
- [ ] Mở sẵn một cửa sổ terminal trong VS Code.
- [ ] Đóng bớt ứng dụng nặng: Spark dùng toàn bộ 16 luồng CPU.

> Chạy lại trên cùng máy **luôn ra đúng cùng kết quả**; nhóm đã chạy nhiều lần để kiểm tra. Các con số trong kịch bản dưới đây vì vậy là con số sẽ hiện trên màn hình.

---

## Tổng quan kịch bản

| Bước | Nội dung | Thời gian |
|---|---|---|
| 1 | Giới thiệu bài toán | 1 phút |
| 2 | Môi trường và dữ liệu | 1 phút |
| 3 | Tạo phiên Spark, đọc dữ liệu | 1 phút |
| 4 | Khám phá dữ liệu | 1 phút |
| 5 | Pipeline xử lý văn bản | 1,5 phút |
| 6 | Chia dữ liệu, huấn luyện, đánh giá | 1,5 phút |
| 7 | Đối chiếu với sách | 1 phút |
| 8 | Nhận xét và kết luận | 1–2 phút |

---

## Bước 1 – Giới thiệu bài toán

**Màn hình:** tiêu đề notebook, hoặc trang 332 của sách.

> "Phần thực hành duy nhất có code của Chương 11 là phát hiện loại tội phạm từ dữ liệu của thành phố San Francisco. Dữ liệu gồm gần **880 nghìn** báo cáo tội phạm trong **12 năm, từ 2003 đến 2015**. Nhiệm vụ là đọc **đoạn mô tả vụ việc** do cảnh sát ghi lại, rồi dự đoán vụ việc đó thuộc loại nào trong **39 loại tội phạm**. Đây là bài toán phân loại văn bản nhiều lớp. Sách dùng Apache Spark vì Spark xử lý được dữ liệu lớn và có sẵn công cụ xử lý văn bản."

---

## Bước 2 – Môi trường và dữ liệu

**Thao tác:** trong terminal, chạy lệnh kiểm tra phiên bản Java:

```powershell
java -version
```

> "Nhóm chạy code trên Windows 11, dùng **Python 3.12, PySpark 4.2.0 và Java 21**. Sách viết năm 2019 nên dùng Spark 2.4 với Java 8. Nhóm chọn phiên bản hiện hành để không phải cài phần mềm đã hết hỗ trợ, và **giữ nguyên code của sách, không sửa dòng nào**.
>
> Dữ liệu là bộ *San Francisco Crime Classification* trên Kaggle. Notebook đọc file tên `sf_crime_dataset.csv`, còn file tải về tên `train.csv`, nên nhóm chỉ cần sao chép và đổi tên."

---

## Bước 3 – Tạo phiên Spark và đọc dữ liệu (ô [0] → [2])

**Thao tác:** chạy ô [0], [1], [2].

**Màn hình hiện:** danh sách 9 cột `['Dates', 'Category', 'Descript', 'DayOfWeek', 'PdDistrict', 'Resolution', 'Address', 'X', 'Y']`.

> "Ô đầu tiên nạp thư viện và tạo một **phiên Spark**, tức điểm khởi đầu của mọi chương trình Spark. Sách đặt bộ nhớ tới 50–70 GB. Đây chỉ là **mức trần** được phép dùng, nên vẫn chạy được trên máy 30 GB của nhóm.
>
> Ô tiếp theo đọc file CSV. Dữ liệu có 9 cột: thời gian, loại tội phạm, mô tả, thứ trong tuần, quận cảnh sát, cách giải quyết, địa chỉ và tọa độ. Ta chỉ cần hai cột: **`Descript` làm đầu vào** và **`Category` là nhãn cần dự đoán**."

---

## Bước 4 – Khám phá dữ liệu (ô [3] → [7])

**Thao tác:** chạy ô [3] → [7].

**Màn hình hiện:** bảng 20 loại tội phạm nhiều nhất, đứng đầu là LARCENY/THEFT với 174.900 vụ.

> "Sau khi chỉ giữ hai cột, ta thống kê số vụ theo từng loại. Nhiều nhất là **trộm cắp tài sản với gần 175 nghìn vụ**, chiếm khoảng 20%. Tiếp theo là vi phạm khác, sự việc không phạm tội và hành hung. Còn những loại hiếm nhất, không hiện trong bảng này, chỉ có vài chục vụ, thậm chí chỉ **6 vụ**.
>
> Như vậy dữ liệu **mất cân bằng mạnh**. Đặc điểm này sẽ ảnh hưởng tới kết quả mà lát nữa nhóm phân tích."

---

## Bước 5 – Pipeline xử lý văn bản (ô [8] → [11])

**Thao tác:** chạy ô [8] → [11]. Ô [10] chạy mất vài giây.

**Màn hình hiện:** bảng có các cột `words`, `filtered`, `features` (vector 809 chiều), `label`.

> "Máy tính không hiểu chữ, nên phải chuyển mô tả thành số. Spark làm việc này bằng một **pipeline**, tức chuỗi 4 bước nối tiếp:
>
> 1. **Tách từ**: 'WARRANT ARREST' thành hai từ 'warrant' và 'arrest'.
> 2. **Bỏ từ dừng**: loại các từ không mang nghĩa như 'the'.
> 3. **Đếm từ**: mỗi mô tả thành một vector đếm số lần xuất hiện của từng từ. Bộ từ vựng có **809 từ**, nên mỗi mô tả là một vector 809 chiều.
> 4. **Đánh số nhãn**: tên loại tội phạm thành số theo độ phổ biến; trộm cắp là 0, vi phạm khác là 1, và cứ thế.
>
> Lưu ý: sách gọi bước 4 là 'one-hot', nhưng thực ra nó chỉ **đánh số thứ tự** cho nhãn."

---

## Bước 6 – Chia dữ liệu, huấn luyện, đánh giá (ô [12] → [15])

**Thao tác:** chạy ô [12] → [15]. Ô [13] huấn luyện mất khoảng 7–9 giây.

**Màn hình hiện:**
- Ô [12]: `Training Dataset Count: 614578`, `Test Dataset Count: 263471`.
- Ô [14]: các dự đoán "trộm cắp" có xác suất cao nhất, khoảng 0,87.
- Ô [15]: `0.9726191534310812`.

> "Dữ liệu được chia ngẫu nhiên: **70% để huấn luyện**, khoảng 615 nghìn bản ghi, và **30% để kiểm tra**, khoảng 263 nghìn bản ghi.
>
> Mô hình là **hồi quy logistic** nhiều lớp. Huấn luyện trên hơn 600 nghìn bản ghi chỉ mất vài giây nhờ Spark xử lý song song.
>
> Ô cuối đánh giá trên tập kiểm tra và cho kết quả **0,9726, tức khoảng 97%**, đúng như sách công bố."

---

## Bước 7 – Đối chiếu với sách

**Màn hình:** bảng sau (lấy từ mục 5.4 và 6.3 của báo cáo chạy code).

| | Sách | Nhóm (Spark 4.2) | Nhóm (Spark 2.4, 8 luồng) |
|---|---|---|---|
| Dữ liệu, thống kê, pipeline | – | Trùng | Trùng |
| Train / Test | 614.666 / 263.383 | 614.578 / 263.471 | 614.666 / 263.383 |
| Kết quả đánh giá | 0,972528… | 0,972619… | **0,9725282146509521 (trùng tuyệt đối)** |

> "Mọi bước xử lý dữ liệu đều **trùng sách từng ký tự**. Chỉ phần chia dữ liệu ngẫu nhiên lệch 88 dòng, nên kết quả cuối lệch ở **chữ số thập phân thứ tư**.
>
> Nhóm đã tìm ra nguyên nhân. Spark chia dữ liệu theo **số luồng CPU**: máy nhóm có 16 luồng, máy tác giả có 8. Thêm nữa, phiên bản Spark cũng khác. Để kiểm chứng, nhóm dựng lại đúng **Spark 2.4 và giới hạn 8 luồng**. Kết quả **trùng sách đến 16 chữ số thập phân**. Nghĩa là code của sách hoàn toàn tái hiện được."

---

## Bước 8 – Nhận xét và kết luận

**Màn hình:** mục 7 của báo cáo chạy code.

> "Khi phân tích sâu hơn, nhóm có ba phát hiện:
>
> **Thứ nhất**, con số 97% sách gọi là 'accuracy' thực chất là **chỉ số F1**. Accuracy thật là **97,8%**.
>
> **Thứ hai**, mô hình làm tốt với các loại phổ biến, nhưng có **6 trong 39 loại hiếm không bao giờ được dự đoán**. Nguyên nhân là dữ liệu mất cân bằng cộng với tham số điều chuẩn `regParam = 0.3` quá mạnh. Khi giảm tham số này về 0, mô hình nhận đủ 39 loại và accuracy tăng lên **99,7%**.
>
> **Thứ ba**, bài toán này **khá dễ**: gần như mỗi mô tả chỉ thuộc đúng một loại tội phạm. Chỉ cần tra bảng đã đạt 99,7%.
>
> **Kết luận**: nhóm đã chạy thành công code Chương 11 trên máy của mình, giải thích được mọi sai khác, và tái hiện tuyệt đối kết quả của sách. Hướng phát triển là dự đoán tội phạm theo **thời gian và địa điểm** để tìm điểm nóng, và làm **demo phần cứng**: ESP32 kết hợp Raspberry Pi 5 thành một trạm báo cáo sự cố cho thành phố thông minh."

---

## Câu hỏi có thể gặp

| Câu hỏi | Gợi ý trả lời |
|---|---|
| Vì sao dùng Spark mà không dùng scikit-learn? | Sách chọn Spark để minh họa xử lý dữ liệu lớn, phân tán, đúng chủ đề thành phố thông minh với dữ liệu từ rất nhiều nguồn. Với 880 nghìn dòng, scikit-learn cũng chạy được. |
| Vì sao kết quả không giống hệt sách? | Spark chia dữ liệu theo số luồng CPU (16 so với 8), và khác phiên bản (4.2 so với 2.4). Với Spark 2.4 và 8 luồng thì trùng tuyệt đối. |
| F1 khác accuracy thế nào? | Accuracy là tỷ lệ đoán đúng. F1 cân bằng giữa độ chính xác (precision) và độ phủ (recall) của từng lớp, rồi lấy trung bình theo số mẫu. Với dữ liệu mất cân bằng, F1 phản ánh tốt hơn. |
| Kết quả 97% có dùng được ngoài thực tế không? | Chưa. Mô tả vụ việc được cảnh sát ghi cùng lúc với loại tội phạm, như một mã phân loại con, nên bài toán gần như tra bảng. Bài toán có giá trị hơn là dự đoán từ thời gian và địa điểm. |
| Phần IoT nằm ở đâu? | Đây là khâu "thuật toán AI" trong kiến trúc IoT 9 thành phần của chương. Demo phần cứng sẽ nối thêm thiết bị (ESP32), cổng kết nối (MQTT trên Raspberry Pi) và cơ cấu chấp hành (đèn, còi). |

---

## Phương án dự phòng

| Tình huống | Cách xử lý |
|---|---|
| Spark không khởi động hoặc chạy quá lâu | Mở notebook `SF_crime_category_detection_spark4.ipynb` trên GitHub (đã có sẵn kết quả) và trình bày trên đó |
| Báo lỗi không tìm thấy `sf_crime_dataset.csv` | Kiểm tra lại file trong `Chapter11`; sao chép `train.csv` thành `sf_crime_dataset.csv` |
| VS Code không thấy kernel | Bấm Select Kernel → Jupyter Kernel → "Python 3.12 (Spark - Chuong 11)" |
| Máy chiếu chữ nhỏ | Phóng to VS Code bằng `Ctrl` + `+` trước khi chạy |
