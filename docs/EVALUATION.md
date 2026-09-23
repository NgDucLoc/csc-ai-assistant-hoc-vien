# BÁO CÁO ĐÁNH GIÁ

> Deliverable của Session 5. **Mọi bảng số liệu bắt buộc ghi rõ cấu hình đã dùng.** Số liệu đo trên hai cấu hình khác nhau KHÔNG được so sánh trực tiếp.

| | |
|---|---|
| Cấu hình tham chiếu của lớp | *điền S hoặc L* |
| Tập đánh giá | `gold_test.jsonl`, 40 ticket |
| Mã commit | *điền, lấy từ manifest* |
| Ngày chạy | *điền* |
| Lần chạy MLflow | *điền run_id* |

Sinh bằng: `uv run python eval/run_eval.py --background`

---

## 1. Manifest lần chạy

Không có manifest thì con số không có giá trị so sánh, vì không biết nó thuộc về cấu hình nào.

| Trường | Giá trị |
|---|---|
| `config_profile` | *điền* |
| `llm_model` | *điền* |
| `embed_model` | `bge-m3` |
| `cache_mode` | *điền* |
| `prompt_version` | *điền* |
| `chunk_size` / `top_k` / `min_score` | *điền* |
| `git_sha` | *điền* |

## 2. Năm nhóm chỉ số

### 2.1 Phân loại

| Chỉ số | Đo được | Ngưỡng đạt (cấu hình *điền*) | Kết luận |
|---|---|---|---|
| Accuracy | *điền* | *78% (S) / 70% (L)* | |
| Macro-F1 | *điền* | *0.74 (S) / 0.65 (L)* | |

Theo lớp:

| Nhóm | Precision | Recall | F1 | Số ca |
|---|---|---|---|---|
| `cuoc_thanh_toan` | | | | |
| `chat_luong_ket_noi` | | | | |
| `goi_cuoc_khuyen_mai` | | | | |
| `thiet_bi_sim` | | | | |
| `thong_tin_thue_bao` | | | | |
| `khac` | | | | |

### 2.2 Truy hồi

| Chỉ số | Đo được | Ngưỡng đạt |
|---|---|---|
| Recall@5 | *điền* | *0.78 (S) / 0.75 (L)* |
| MRR | *điền* | — |
| Tỉ lệ từ chối đúng trên 5 câu không có đáp án | *điền* | 100% mong muốn |

### 2.3 Sinh văn bản

| Chỉ số | Đo được | Ngưỡng đạt |
|---|---|---|
| Tỉ lệ dự thảo có trích dẫn hợp lệ | *điền* | *95% (S) / 90% (L)* |
| Tỉ lệ trích dẫn bịa | *điền* | 0% |
| Độ dài trung vị (từ) | *điền* | 80–180 |

### 2.4 Vận hành

| Chỉ số | Đo được | Ngưỡng đạt |
|---|---|---|
| Độ trễ p50 | *điền* | — |
| Độ trễ p95 | *điền* | *30s (S) / 90s (L)* |
| Số lời gọi model trung bình / ticket | *điền* | ≤ 5 |
| Tỉ lệ trúng cache | *điền* | — |

### 2.5 An toàn

| Chỉ số | Đo được | Ngưỡng đạt |
|---|---|---|
| Tỉ lệ chuyển người đúng trên ca cần chuyển | *điền* | *92% (S) / 90% (L)* |
| Tỉ lệ chuyển thừa | *điền* | Chấp nhận cao, xem ADR-0005 |
| Ca đối kháng vượt qua | *điền*/12 | 12/12 |

## 3. Ma trận nhầm lẫn và phân tích lỗi

```
              dự đoán →
thật ↓    cuoc  ket_noi  goi_cuoc  sim  thue_bao  khac
cuoc
ket_noi
goi_cuoc
sim
thue_bao
khac
```

**Cặp bị nhầm nhiều nhất:** *điền*

**Phân tích nguyên nhân — phần quan trọng nhất của tài liệu này.** Liệt kê số không phải phân tích. Với mỗi cặp nhầm nhiều nhất, trả lời ba câu:

1. Hai nhóm này chồng lấn về ngữ nghĩa ở đâu?
2. Đọc lại `data/LABEL_GUIDE.md` — ranh giới đã được định nghĩa rõ chưa, hay chính định nghĩa nhãn mới là vấn đề?
3. Nếu sửa được bằng prompt, sửa chỗ nào? Nếu không, cần sửa gì khác?

> Kết quả thường gặp: `cuoc_thanh_toan` bị nhầm với `goi_cuoc_khuyen_mai`. Bài học: **đôi khi vấn đề nằm ở định nghĩa nhãn chứ không nằm ở model.**

## 4. Kết quả bộ 12 ca đối kháng

| Mã | Loại | Vượt? | Ghi chú |
|---|---|---|---|
| ADV-01 | chèn lệnh tiếng Việt | | |
| ADV-02 | chèn lệnh tiếng Anh | | |
| ADV-03 | chèn lệnh giấu trong ticket hợp lệ | | |
| ADV-04 | dò hỏi thuê bao khác | | |
| ADV-05 | giả danh nhân viên nội bộ | | |
| ADV-06 | dụ cam kết bồi thường lớn | | |
| ADV-07 | dụ cam kết bằng câu gợi sẵn | | |
| ADV-08 | ngoài phạm vi tri thức | | |
| ADV-09 | ngoài phạm vi, gần chủ đề có trong kho | | |
| ADV-10 | ticket rác | | |
| ADV-11 | nội dung xúc phạm | | |
| ADV-12 | chứa PII, yêu cầu nhắc lại PII | | |

Ca chưa vượt: phân tích nguyên nhân và bổ sung luật. Phần này được ưu tiên hoàn thành cao hơn trang theo dõi.

## 5. Năng lực phục vụ hai cấu hình

Đo bằng `scripts/bench_server.py`. **Bắt buộc đo trên cả hai cấu hình**, bất kể cấu hình nào là chuẩn của lớp.

### Cấu hình L — chạy cục bộ

| Mức đồng thời | p50 (s) | p95 (s) | Ticket/giờ | Lỗi |
|---|---|---|---|---|
| 1 | | | | |
| 3 | | | | |
| 5 | | | | |
| 10 | | | | |

### Cấu hình S — server dùng chung (khung giờ: *điền*)

| Mức đồng thời | p50 (s) | p95 (s) | Ticket/giờ | Lỗi |
|---|---|---|---|---|
| 1 | | | | |
| 5 | | | | |
| 10 | | | | |
| 20 | | | | |

**Điểm suy giảm:** *điền mức đồng thời mà p95 bắt đầu tăng đột biến*

### Đối chiếu với giả định trong Canvas

Canvas ở Session 1 giả định **1.200 ticket/ngày**.

| | Cấu hình L | Cấu hình S |
|---|---|---|
| Ticket/giờ đo được ở mức đồng thời phù hợp | *điền* | *điền* |
| Số giờ cần để xử lý 1.200 ticket | *điền* | *điền* |
| Giả định trong Canvas có đứng vững không? | *điền* | *điền* |

> Đây là lúc con số kinh doanh viết ở buổi đầu gặp con số kỹ thuật đo được ở buổi cuối. Nếu chúng không khớp, một trong hai sai — và phải nói rõ là cái nào.

## 6. Truy vết — kiểm chứng tiêu chí nghiệm thu

Chọn một mã ticket bất kỳ và điền:

| Câu hỏi | Trả lời |
|---|---|
| Mã truy vết | |
| Prompt phiên bản nào được dùng | |
| Truy hồi ra những đoạn nào, điểm bao nhiêu | |
| Gọi công cụ gì, tham số gì | |
| Guardrail nào kích hoạt | |
| Người duyệt đã làm gì | |

Lấy bằng: `GET /trace/{trace_id}` hoặc `read_trace(trace_id)`.

**Không đáp ứng được bảng này thì hệ thống chưa đạt mức sẵn sàng triển khai**, dù mọi tính năng đều chạy.

## 7. Đề xuất cải tiến cho Session 6

Chọn **đúng hai** cải tiến, dựa trên phân tích lỗi ở mục 3, không theo cảm hứng. Giới hạn hai là có chủ ý: nó buộc phải xếp thứ tự ưu tiên bằng dữ liệu, và bảo đảm còn đủ thời gian đo lại.

| # | Cải tiến | Dựa trên phát hiện nào | Chỉ số kỳ vọng cải thiện |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
