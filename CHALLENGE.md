# CHALLENGE — Tầng thử thách

**Không chấm điểm.** Dành cho nhóm hoàn thành sớm tầng lõi và tầng nâng cao.

Nguyên tắc chung: **mọi thử thách đều phải kèm phép đo.** Làm xong mà không đo được là chưa xong.

---

## Sau Lab 1 — Phân tích độ nhạy của bài toán kinh tế

Điểm hòa vốn thay đổi thế nào khi:

- Độ chính xác chỉ đạt 70% thay vì 85%
- Khối lượng ticket giảm còn 600/ngày
- Chi phí vận hành tăng gấp đôi

Vẽ đồ thị điểm hòa vốn theo hai biến. **Ở mức nào thì dự án không còn đáng làm?**

---

## Sau Lab 2 — Sơ đồ tuần tự cho luồng có gọi công cụ

Vẽ trước cấu trúc sẽ xây ở Session 4, rồi cuối Session 4 so lại: chỗ nào bạn dự đoán đúng, chỗ nào không, và vì sao.

---

## Sau Lab 3

### 3.1 Tìm kiếm lai có trọng số hiệu chỉnh

Hệ thống hiện dùng `0.75 × vector + 0.25 × từ khóa`. Con số đó chọn theo cảm tính.

Quét trọng số từ 0.0 tới 1.0, đo Recall@5 tại mỗi mức, vẽ đường cong. **Trọng số tối ưu là bao nhiêu, và nó có ổn định giữa các nhóm câu hỏi không?**

### 3.2 Chia đoạn theo ngữ nghĩa

Thay vì cắt theo mục và ký tự, thử cắt theo điểm gãy ngữ nghĩa: nhúng từng câu, tìm chỗ độ tương đồng giữa hai câu liền nhau tụt mạnh, cắt tại đó.

So sánh Recall@5 với chiến lược hiện tại. **Đo cả thời gian dựng chỉ mục** — nếu nó tăng gấp ba thì cải tiến có đáng không?

### 3.3 Truy hồi nhận biết ngày hiệu lực

Hiện hệ thống lọc `status: superseded` một cách tuyệt đối. Nhưng vụ việc phát sinh trước ngày hiệu lực của bản mới **phải** tham chiếu bản cũ.

Cài truy hồi nhận tham số `as_of_date` và chọn đúng phiên bản chính sách có hiệu lực tại ngày đó. Kiểm chứng bằng hai cặp tài liệu mâu thuẫn có sẵn.

---

## Sau Lab 4

### 4.1 Vòng lặp agent thực thụ

Cho nhánh xử lý phức tạp: model tự lập kế hoạch, chọn công cụ, quan sát kết quả, quyết định bước tiếp theo. **Giới hạn số vòng lặp.**

Đo ba thứ so với quy trình cố định: độ chính xác, số lời gọi model trung bình, độ trễ p95. **Agent có đáng không, và với loại ticket nào?**

### 4.2 Học từ thao tác duyệt

Khi người duyệt sửa dự thảo, phần bị sửa mang thông tin. Thu thập các cặp (bản gốc, bản đã sửa) và phân tích: model hay sai ở đâu nhất — trích dẫn, giọng điệu, hay nội dung?

Từ đó đề xuất một sửa đổi prompt, và đo lại.

### 4.3 Định tuyến theo độ khó

Ticket dễ dùng model nhỏ, ticket khó mới dùng model lớn. Cài bộ định tuyến dựa trên độ tin cậy phân loại.

Đo: tiết kiệm được bao nhiêu lời gọi tới model lớn, đổi lại mất bao nhiêu điểm accuracy?

---

## Sau Lab 5

### 5.1 Kiểm định ý nghĩa thống kê

Với n=40, chênh lệch 3 điểm phần trăm giữa hai phiên bản prompt có thể chỉ là nhiễu.

Cài kiểm định McNemar cho hai bộ phân loại trên cùng tập. **Chênh lệch của bạn có ý nghĩa thống kê không?** Cần bao nhiêu mẫu để phát hiện chênh lệch 5 điểm phần trăm?

### 5.2 Guardrail thích ứng

Bộ mẫu phát hiện chèn lệnh hiện là danh sách cố định. Viết 20 biến thể mới của các ca đối kháng có sẵn, đo tỉ lệ bị chặn.

**Bộ mẫu bắt được bao nhiêu phần trăm? Cần thêm mẫu nào?**

### 5.3 Tìm điểm gãy thật của hệ thống

`bench_server.py` đo tới mức đồng thời 20. Đẩy tiếp cho tới khi hệ thống thực sự gãy.

Vẽ đường cong độ trễ theo mức đồng thời. **Điểm gãy nằm ở đâu, và nút thắt là gì — dịch vụ model, hàng đợi, hay SQLite?**

### 5.4 Triển khai vLLM thật trên GPU của nhóm — chỉ khi phòng Lab có GPU workstation

Mặc định cả khóa chạy Ollama trên chính GPU của workstation (cấu hình L, ví dụ RTX 5080 16GB) — nhưng `qwen3:8b` + `bge-m3` lượng tử hóa mặc định của Ollama chỉ dùng khoảng 5-6 GB trong 16 GB, còn dư nhiều VRAM.

Dựng vLLM chạy trên chính GPU của nhóm, phơi API tương thích OpenAI y hệt Ollama, cùng một model để phép so sánh chỉ còn khác biến số hạ tầng:

```bash
python3 -m venv .venv-vllm && source .venv-vllm/bin/activate && pip install vllm
./scripts/run_vllm_local.sh                          # mặc định Qwen/Qwen3-8B-AWQ, cổng 8001
```

Sửa `.env` trỏ sang vLLM, rồi đo lại đúng bộ chỉ số cũ:

```bash
LLM_BASE_URL=http://localhost:8001/v1
LLM_MODEL=Qwen/Qwen3-8B-AWQ
```

```bash
CACHE_MODE=off uv run python scripts/bench_server.py --out eval/results/bench-vllm-gpu.json
uv run python eval/run_eval.py --set train --limit 20 --skip-adversarial
```

| So sánh | Ollama · GPU · Qwen3-8B | vLLM · GPU · Qwen3-8B |
|---|---|---|
| p50 / p95 độ trễ | `______` | `______` |
| Accuracy | `______` | `______` |
| VRAM đã dùng (`nvidia-smi`) | `______` | `______` |

**Câu hỏi cần trả lời, không chỉ số đo:**

- Với chỉ **một nhóm** dùng một GPU (đồng thời ~1-2), lợi ích của vLLM tới từ đâu — gộp lô liên tục (vốn cần nhiều người gọi cùng lúc mới phát huy), hay từ tốc độ suy luận thô của bản thân engine?
- Cùng một model, accuracy giữa hai hàng có thực sự bằng nhau không? Nếu lệch, lệch vì lượng tử hóa (AWQ so với bản Ollama pull mặc định) hay vì sai khác template/tham số sinh — không phải vì "model khác nhau" nữa.
- Chênh lệch độ trễ có đủ lớn để bù chi phí vận hành thêm một dịch vụ (vLLM cần môi trường Python riêng, khởi động chậm hơn Ollama)?
- Đây có nên là cấu hình *mặc định* của lớp không, hay chỉ nên là lựa chọn nâng cao? Lập luận bằng số đo, không bằng cảm tính — đúng tinh thần Session 2 bước 2.

> Đây là bài tập **không bắt buộc và không phải cấu hình mặc định của lớp** (xem `PROJECT-SPEC.md` Mục 17, mục v1.5 và v1.6). Đổi mặc định thật sự đòi hỏi hiệu chuẩn lại toàn bộ `SPEC-SCOPE-03` và sinh lại `.cache/llm_cache.db` — việc đó không làm tùy hứng giữa buổi.

---

## Sau Lab 6

### 6.1 Phát hiện trôi dữ liệu tự động

Cài cơ chế so sánh phân bố ticket 7 ngày gần nhất với phân bố của tập kiểm định. Cảnh báo khi lệch quá ngưỡng.

Kiểm chứng bằng cách bơm vào một loạt ticket lệch phân bố có chủ ý.

### 6.2 Đánh giá chất lượng dự thảo bằng model

Dùng chính model làm giám khảo chấm dự thảo theo ba tiêu chí: bám căn cứ, đúng giọng điệu, đầy đủ.

**Rồi kiểm chứng giám khảo:** cho nó chấm 20 dự thảo mà người đã đánh giá, đo mức đồng thuận. Giám khảo không đáng tin thì điểm nó chấm cũng vậy.

### 6.3 Ước lượng chi phí thật

Tính chi phí mỗi ticket ở cả hai cấu hình: điện năng, khấu hao phần cứng, chi phí cơ hội của GPU dùng chung.

So với ước lượng trong Canvas ở Session 1. **Con số nào sai, và sai bao nhiêu?**
