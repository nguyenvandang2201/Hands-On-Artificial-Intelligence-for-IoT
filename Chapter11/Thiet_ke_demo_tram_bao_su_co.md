# THIẾT KẾ DEMO PHẦN CỨNG – ĐÈN BÁO MỨC ĐỘ SỰ CỐ
### Chương 11 – AI for Smart Cities IoT (bản đơn giản)

| | |
|---|---|
| **Mục tiêu** | Laptop chạy code phân loại tội phạm của sách; ESP32 nhận kết quả qua cáp USB và bật đèn đỏ / vàng / xanh theo mức độ của từng báo cáo |
| **Code của sách** | `SF_crime_category_detection.ipynb`, chạy nguyên văn, chỉ thêm **1 ô** ở cuối |
| **Phần cứng** | ESP32, 3 LED, 3 điện trở – chỉ cần nối 3 đèn |
| **Không cần** | Wi-Fi, Raspberry Pi, màn hình, sửa code của sách |

---

## 1. Ý tưởng

```
[Laptop]                                                [ESP32]
notebook Chương 11 (code sách)  ──USB, gửi 1 ký tự──▶   R → đèn đỏ
  + 1 ô "phát lại báo cáo"         R / Y / G             Y → đèn vàng
                                                         G → đèn xanh
```

1. Chạy hết notebook của sách. Sách đã tạo sẵn biến `predictions`, chứa dự đoán cho **263 nghìn báo cáo** của tập kiểm tra.
2. Ô thêm ở cuối lấy khoảng 50 báo cáo trong số đó. Cứ mỗi 3 giây, ô này:
   - In mô tả, loại tội phạm thật và loại mô hình dự đoán lên màn hình.
   - Gửi mức độ (`R` / `Y` / `G`) sang ESP32.
3. ESP32 bật đèn tương ứng. Cả lớp nhìn thấy một **luồng báo cáo sự cố** được AI phân loại và cảnh báo theo thời gian thực.

**Mức độ:**

| Ký tự | Đèn | Loại tội phạm |
|---|---|---|
| `R` | Đỏ | ASSAULT, ROBBERY, KIDNAPPING, SEX OFFENSES FORCIBLE, WEAPON LAWS, ARSON |
| `Y` | Vàng | LARCENY/THEFT, VEHICLE THEFT, BURGLARY, VANDALISM, STOLEN PROPERTY, FRAUD, DRUG/NARCOTIC, DRIVING UNDER THE INFLUENCE |
| `G` | Xanh | Các loại còn lại |

---

## 2. Linh kiện và nối dây

| Linh kiện | Nối với ESP32 |
|---|---|
| LED đỏ, qua điện trở 220 Ω | GPIO25 → LED → GND |
| LED vàng, qua điện trở 220 Ω | GPIO26 → LED → GND |
| LED xanh, qua điện trở 220 Ω | GPIO27 → LED → GND |
| Cáp USB | ESP32 ↔ laptop (cấp nguồn và truyền dữ liệu) |

Thêm breadboard và dây cắm. *(Tùy chọn: một module còi nối GPIO32, kêu khi gặp mức đỏ.)*

---

## 3. Phần mềm

### 3.1. ESP32 (Arduino IDE)

```cpp
const int RED = 25, YEL = 26, GRN = 27;

void setup() {
  Serial.begin(115200);
  pinMode(RED, OUTPUT); pinMode(YEL, OUTPUT); pinMode(GRN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'R' || c == 'Y' || c == 'G') {
      digitalWrite(RED, c == 'R');
      digitalWrite(YEL, c == 'Y');
      digitalWrite(GRN, c == 'G');
    }
  }
}
```

### 3.2. Laptop – ô thêm vào cuối notebook

Cần cài thư viện giao tiếp cổng USB một lần: `pip install pyserial` (trong môi trường `spark-ch11`).

```python
import serial, time

esp = serial.Serial("COM3", 115200)      # đổi COM3 theo cổng của ESP32 trên máy
time.sleep(2)                            # ESP32 tự khởi động lại khi mở cổng

labels = pipelineFit.stages[3].labels    # tên 39 loại, lấy từ StringIndexer của sách
RED = {"ASSAULT", "ROBBERY", "KIDNAPPING", "SEX OFFENSES FORCIBLE", "WEAPON LAWS", "ARSON"}
YELLOW = {"LARCENY/THEFT", "VEHICLE THEFT", "BURGLARY", "VANDALISM", "STOLEN PROPERTY",
          "FRAUD", "DRUG/NARCOTIC", "DRIVING UNDER THE INFLUENCE"}

rows = predictions.sample(False, 0.0002, seed=11) \
                  .select("Descript", "Category", "prediction").collect()
for r in rows:
    pred = labels[int(r["prediction"])]
    level = "R" if pred in RED else "Y" if pred in YELLOW else "G"
    print(f"{r['Descript'][:40]:40} | thật: {r['Category']:15} | dự đoán: {pred}")
    esp.write(level.encode())
    time.sleep(3)
esp.close()
```

Ô này **chỉ dùng lại các biến của sách** (`pipelineFit`, `predictions`), không huấn luyện lại hay tính lại gì.

---

## 4. Kiểm chứng đã làm trên máy của nhóm

| Nội dung | Kết quả |
|---|---|
| Thời gian lấy báo cáo từ `predictions` | **51 báo cáo trong 1,1 giây** |
| Số dự đoán đúng trong 51 báo cáo | **51/51** |
| Phân bố mức độ | Đỏ 8, vàng 23, xanh 20 (đèn đổi màu đa dạng) |

*Chưa thử: phần gửi qua cáp USB và code ESP32, vì chưa kết nối ESP32 thật.*

---

## 5. Kịch bản demo (khoảng 2 phút)

1. Mở notebook và chạy hết (khoảng 30 giây).
   > "Đây là code của sách: đọc dữ liệu, xử lý văn bản, huấn luyện mô hình, đánh giá được 97%."
2. Chạy ô cuối. Mỗi 3 giây, màn hình hiện một báo cáo và ESP32 bật đèn.
   > "Hệ thống giả lập luồng báo cáo sự cố đổ về trung tâm. AI phân loại từng báo cáo và gửi lệnh cảnh báo xuống thiết bị ngoài hiện trường."
3. Chỉ vào cột "thật" và "dự đoán" để cả lớp thấy mô hình đoán đúng.

---

## 6. Lưu ý

- **Đóng Serial Monitor** của Arduino IDE trước khi chạy ô cuối, vì một cổng USB chỉ một chương trình dùng được.
- **Tìm cổng COM**: trong Arduino IDE (Tools → Port) hoặc Device Manager.
- **Vì sao phát lại báo cáo có sẵn mà không gõ câu mới**: nếu gõ câu mới, Spark mất khoảng **11 giây** cho mỗi lần dự đoán trên máy của nhóm. Còn phát lại thì tất cả dự đoán đã được code của sách tính sẵn trong một lần.

---

## 7. Liên hệ với kiến trúc IoT của chương (trang 328–329)

| Thành phần trong sách | Trong demo |
|---|---|
| Thuật toán AI | Mô hình hồi quy logistic của sách chạy trên laptop |
| Ứng dụng điều khiển | Ô cuối: quyết định mức độ và gửi lệnh |
| Cơ cấu chấp hành | 3 đèn trên ESP32 |

---

## 8. Hướng mở rộng

1. **Thêm cảm biến**: nối nút nhấn hoặc cảm biến chuyển động PIR vào ESP32. Mỗi lần có người đi qua, ESP32 gửi yêu cầu, laptop trả về báo cáo kế tiếp.
2. **Bỏ dây USB**: ESP32 nhận lệnh qua Wi-Fi.
3. **AI chạy ngay trên ESP32**: xuất mô hình của sách ra file khoảng 130 KB rồi nạp vào ESP32 để thiết bị tự phân loại. Nhóm đã kiểm chứng: cách tính trên ESP32 cho kết quả trùng Spark trên toàn bộ 879 mô tả.
4. **Đèn đường thông minh** (trang 327): cảm biến ánh sáng và PIR điều khiển độ sáng LED như hệ thống CitySense.
