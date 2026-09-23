# QUY TRÌNH XỬ LÝ SỰ CỐ

Ba sự cố thường gặp nhất, kèm cách nhận biết, cách xử lý ngay, và cách xử lý tận gốc.

---

## SC-01 — Dịch vụ model không phản hồi

### Nhận biết

- `/health` trả `circuit_open: true`
- Nhật ký có `"step": "classify", "ok": false` lặp lại
- Toàn bộ ticket mới đều rơi vào trạng thái `escalated` với lý do `he_thong_suy_giam`

### Mức ảnh hưởng

**Trung bình.** Hệ thống không sập — ngắt mạch (ADR-0003) khiến mọi ticket chuyển giao dịch viên có kiểm soát. Giao dịch viên vẫn làm việc được, chỉ là mất phần hỗ trợ.

### Xử lý ngay — 5 phút

1. Kiểm tra dịch vụ model còn sống:
   ```bash
   curl -s $LLM_BASE_URL/models
   ```
2. Nếu chết, khởi động lại:
   ```bash
   ollama serve                    # cấu hình L
   # hoặc báo quản trị server      # cấu hình S
   ```
3. Nếu chưa khôi phục được ngay, **chuyển sang chế độ chỉ dùng cache**:
   ```bash
   docker compose exec api sh -c 'export CACHE_MODE=cache_only'
   docker compose restart api
   ```
   Ticket đã gặp trước đó vẫn xử lý được từ cache; ticket mới chuyển người.
4. Ngắt mạch tự đóng lại sau `CIRCUIT_BREAKER_COOLDOWN` giây (mặc định 60) khi dịch vụ model trở lại.

### Xử lý tận gốc

Nếu lặp lại nhiều lần: kiểm tra bộ nhớ máy chủ model, và cân nhắc chuyển sang cấu hình còn lại. Việc chuyển chỉ cần đổi `LLM_BASE_URL` và `LLM_MODEL`.

### Không được làm

Không tắt ngắt mạch để "thử lại cho bằng được". Ngắt mạch tồn tại để một dịch vụ model chậm không kéo theo toàn bộ hàng đợi treo.

---

## SC-02 — Hệ thống trả lời sai một khách hàng

### Nhận biết

Người duyệt báo cáo, hoặc khách hàng khiếu nại về nội dung phản hồi.

### Mức ảnh hưởng

**Cao.** Có thể phát sinh nghĩa vụ với khách hàng nếu dự thảo sai đã được duyệt và gửi đi.

### Xử lý ngay — 15 phút

1. Lấy mã ticket, tra mã truy vết trong `app.db` hoặc từ giao diện.
2. Dựng lại toàn bộ vòng đời:
   ```bash
   curl -s localhost:8000/trace/<trace_id> | jq
   ```
3. Đọc theo thứ tự và trả lời từng câu:

   | Bước | Câu hỏi |
   |---|---|
   | `classify` | Phân loại đúng nhóm không? Độ tin cậy bao nhiêu? |
   | `retrieve` | Truy hồi ra đoạn nào, điểm bao nhiêu? Đoạn đó có đúng chủ đề không? |
   | `retrieve` | Tài liệu được trích có `status: active` không, hay là bản đã bị thay thế? |
   | `tools` | Công cụ trả về dữ liệu đúng không? |
   | `generate` | Dự thảo có bám vào đoạn đã truy hồi không, hay model tự thêm thông tin? |
   | `guardrail_output` | Guardrail có bắt được gì không? Nếu không, vì sao lọt? |
   | thao tác duyệt | Người duyệt bấm gì? Có sửa không? |

4. Xác định lỗi thuộc mắt xích nào, ghi vào biên bản.

### Xử lý tận gốc

| Lỗi ở đâu | Việc phải làm |
|---|---|
| Truy hồi ra tài liệu đã hết hiệu lực | Kiểm tra `status` và `supersedes` trong front-matter; dựng lại chỉ mục |
| Truy hồi ra đoạn sai chủ đề với điểm cao | Nâng `RETRIEVE_MIN_SCORE`, đo lại Recall@5 trước khi chốt |
| Model tự thêm thông tin ngoài ngữ cảnh | Siết ràng buộc trong `generate.v1.md`, tạo phiên bản v2 |
| Guardrail để lọt | Bổ sung mẫu vào `output_rules.py`, thêm ca vào bộ đối kháng |
| Phân loại sai | Kiểm tra `LABEL_GUIDE.md` — có thể vấn đề ở định nghĩa nhãn |

**Bắt buộc:** mỗi sự cố loại này kết thúc bằng một ca mới thêm vào `tests/adversarial/cases.jsonl`. Sự cố không sinh ra ca kiểm thử là sự cố sẽ lặp lại.

### Không được làm

Không sửa dự thảo thủ công trong cơ sở dữ liệu rồi coi như xong. Nhật ký phải phản ánh đúng những gì đã xảy ra.

---

## SC-03 — Chất lượng suy giảm dần mà không có lỗi rõ ràng

### Nhận biết

- Tỉ lệ người duyệt phải sửa tăng trên 10 điểm phần trăm trong 7 ngày
- Tỉ lệ từ chối tăng trên 5 điểm phần trăm
- Tỉ lệ chuyển người vì `khong_du_can_cu` tăng đột biến

Xem tại trang Theo dõi trong giao diện, hoặc `GET /metrics`.

### Mức ảnh hưởng

**Trung bình, nhưng tích lũy.** Không có lỗi nào bật lên; hệ thống chỉ dần trở nên ít hữu ích.

### Xử lý ngay — 30 phút

1. Chạy đánh giá trên tập kiểm định, so với lần chạy gần nhất trên MLflow:
   ```bash
   uv run python eval/run_eval.py --background
   ```
2. Phân biệt ba nguyên nhân bằng bảng sau:

   | Dấu hiệu | Nguyên nhân nhiều khả năng |
   |---|---|
   | Chỉ số trên tập kiểm định **không đổi**, nhưng tỉ lệ sửa tăng | **Trôi dữ liệu** — phân bố ticket thật đã dịch chuyển, tập kiểm định không còn đại diện |
   | Chỉ số trên tập kiểm định **giảm** | Có thay đổi trong hệ thống: prompt, chỉ mục, hoặc phiên bản model |
   | Tỉ lệ `khong_du_can_cu` tăng, các chỉ số khác ổn | **Trôi khái niệm** — xuất hiện loại yêu cầu mới mà kho tri thức chưa bao phủ |

3. Đọc `top_reject_reasons` trong `/metrics` để biết người duyệt từ chối vì cái gì.

### Xử lý tận gốc

| Nguyên nhân | Việc phải làm |
|---|---|
| Trôi dữ liệu | Lấy mẫu 40 ticket gần đây, gán nhãn lại, cập nhật tập kiểm định |
| Thay đổi trong hệ thống | Đối chiếu manifest hai lần chạy, tìm trường khác nhau |
| Trôi khái niệm | Bổ sung tài liệu vào kho tri thức, dựng lại chỉ mục |
| Model đổi phiên bản | Ghim lại bằng `models/Modelfile`, sinh lại cache |

### Không được làm

Không sửa nhiều thứ cùng lúc rồi báo kết quả tốt lên. Không quy được kết quả cho nguyên nhân nào. **Mỗi lần chỉ thay đổi một biến và đo lại.**
