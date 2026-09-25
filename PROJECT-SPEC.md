# PROJECT SPECIFICATION
## Trợ lý xử lý ticket Chăm sóc khách hàng viễn thông
### Hệ thống thực hành cho môn học *AI-Native Application Engineering*

| Trường | Giá trị |
|---|---|
| Mã dự án | `csc-ai-assistant` |
| Phiên bản spec | `v1.5` |
| Ngày cập nhật | 2026-09-19 |
| Chủ sở hữu | Học viện Viettel — Hội đồng xây dựng chương trình đào tạo |
| Trạng thái | Draft — chờ phê duyệt trước khi triển khai |


<!-- toc:begin -->
**Mục lục:** [0. Cách sử dụng tài liệu này](#muc-0) · [1. Phạm vi và bối cảnh](#muc-1) · [2. Ràng buộc hạ tầng](#muc-2) · [3. Kiến trúc hệ thống](#muc-3) · [4. Công cụ và quy trình kỹ thuật](#muc-4) · [5. Hợp đồng dữ liệu (data contract)](#muc-5) · [6. Chính sách lớp LLM](#muc-6) · [7. Chính sách prompt](#muc-7) · [8. Chính sách tri thức và truy hồi (RAG)](#muc-8) · [9. Chính sách công cụ (tool)](#muc-9) · [10. Chính sách quy trình và chuyển người](#muc-10) · [11. Chính sách guardrails](#muc-11) · [12. Giao thức đánh giá](#muc-12) · [13. Logging và truy vết](#muc-13) · [14. Ma trận truy vết](#muc-14) · [15. Trách nhiệm và bàn giao](#muc-15) · [16. Rủi ro và phương án dự phòng](#muc-16) · [17. Nhật ký thay đổi](#muc-17) · [Phụ lục A](#phu-luc-a) · [Phụ lục B](#phu-luc-b)
<!-- toc:end -->

---

<a id="muc-0"></a>

## 0. CÁCH SỬ DỤNG TÀI LIỆU NÀY

Đây là **tài liệu ràng buộc kỹ thuật (binding spec)**, không phải tài liệu giảng dạy. Nội dung giảng dạy nằm ở tài liệu `.docx` đi kèm.

**Nguyên tắc sử dụng:**

1. Mọi quyết định kỹ thuật trong quá trình xây dựng Starter Kit, dữ liệu, và bài lab **phải tra cứu tài liệu này trước**. Nếu tài liệu chưa quy định, hãy bổ sung vào đây trước khi triển khai.
2. Mỗi mục có mã định danh (ví dụ [`SPEC-DATA-01`](#spec-data-01)). Khi viết code, commit, hoặc báo lỗi, **trích dẫn mã này** để truy vết.
3. Mọi thay đổi phải ghi vào [Mục 17](#muc-17) — Nhật ký thay đổi, kèm lý do.
4. File này đặt tại gốc repo (`/PROJECT-SPEC.md`) và được version cùng code.

**Quy ước mức độ ràng buộc:**

| Từ khóa | Ý nghĩa |
|---|---|
| **BẮT BUỘC** | Không được vi phạm. Vi phạm = lỗi chặn (blocking). |
| **NÊN** | Mặc định tuân theo; muốn khác phải ghi lý do vào một ADR mới. |
| **TÙY CHỌN** | Được phép lựa chọn tự do. |

---

<a id="muc-1"></a>

## 1. PHẠM VI VÀ BỐI CẢNH

<a id="spec-scope-01"></a>

### SPEC-SCOPE-01 — Bài toán

Trung tâm CSKH viễn thông tiếp nhận ticket từ nhiều kênh (tổng đài, ứng dụng di động, email). Quy trình thủ công hiện tại: đọc hiểu → phân loại → tra cứu chính sách → soạn phản hồi → xử lý hoặc chuyển tuyến.

Hệ thống xây dựng trong khóa học hỗ trợ giao dịch viên ở các bước phân loại, tra cứu và soạn thảo — **không thay thế giao dịch viên**.

<a id="spec-scope-02"></a>

### SPEC-SCOPE-02 — Phạm vi MVP

**TRONG phạm vi:**

- Phân loại ticket theo 6 nhóm vấn đề, 3 mức ưu tiên, 3 mức sắc thái
- Trích xuất thực thể có cấu trúc từ nội dung ticket
- Truy hồi chính sách/quy trình liên quan từ kho tri thức nội bộ
- Gọi 3 công cụ giả lập để lấy dữ liệu thuê bao
- Sinh dự thảo phản hồi kèm trích dẫn nguồn
- Màn hình duyệt cho giao dịch viên (duyệt / sửa / từ chối)
- Ghi log đầy đủ và đánh giá chất lượng bằng chỉ số

**NGOÀI phạm vi (BẮT BUỘC không làm):**

- Kết nối hệ thống CRM/billing thật của doanh nghiệp
- Sử dụng dữ liệu khách hàng thật dưới mọi hình thức
- Gửi phản hồi tự động tới khách hàng mà không qua người duyệt
- Fine-tuning model
- Xử lý giọng nói, hình ảnh, hoặc đa ngôn ngữ ngoài tiếng Việt
- Xác thực người dùng, phân quyền, multi-tenant

<a id="spec-scope-03"></a>

### SPEC-SCOPE-03 — Chỉ số thành công của sản phẩm

Ngưỡng phụ thuộc cấu hình tham chiếu đã chọn. **BẮT BUỘC** dùng đúng cột tương ứng.

> **CHƯA HIỆU CHUẨN LẠI kể từ [Mục 17](#muc-17) v1.6.** Từ khi cả hai cấu hình cùng chạy `Qwen3-8B`, bảng dưới vẫn là số đo cũ trên `qwen2.5:3b-instruct` (L) / `Qwen2.5-7B-Instruct` (S). Năm chỉ số chất lượng có thể không còn khác nhau giữa hai cột — chỉ độ trễ chắc chắn còn khác vì lý do hạ tầng. **BẮT BUỘC đo lại bằng [`eval/run_eval.py`](eval/run_eval.py) trên model thật trước khi dùng bảng này để chấm điểm hoặc chặn CI.**

| Chỉ số | Đạt (cấu hình S, Qwen3-8B) | Tốt (S) | Đạt (cấu hình L, Qwen3-8B) | Tốt (L) |
|---|---|---|---|---|
| Accuracy phân loại nhóm vấn đề | ≥ 78% | ≥ 88% | ≥ 70% | ≥ 82% |
| Macro-F1 phân loại | ≥ 0.74 | ≥ 0.85 | ≥ 0.65 | ≥ 0.78 |
| Recall@5 truy hồi tri thức | ≥ 0.78 | ≥ 0.90 | ≥ 0.75 | ≥ 0.88 |
| Tỉ lệ phản hồi có trích dẫn hợp lệ | ≥ 95% | 100% | ≥ 90% | 100% |
| Tỉ lệ chuyển người đúng trên ca cần chuyển | ≥ 92% | 100% | ≥ 90% | 100% |
| Độ trễ p95 mỗi ticket | ≤ 30 giây | ≤ 15 giây | ≤ 90 giây | ≤ 45 giây |

**Ghi chú về Recall@5:** hai cột gần bằng nhau vì chỉ số này phụ thuộc model embedding, mà `bge-m3` giống nhau ở cả hai cấu hình. Chỉ có phần viết lại truy vấn là chịu ảnh hưởng của model sinh văn bản.

> Nếu đổi model hoặc hạ tầng ngoài hai cấu hình trên, **BẮT BUỘC** hiệu chuẩn lại toàn bộ bảng này và ghi vào nhật ký thay đổi.

---

<a id="muc-2"></a>

## 2. RÀNG BUỘC HẠ TẦNG

<a id="spec-infra-01"></a>

### SPEC-INFRA-01 — Hai cấu hình chạy, ngang hàng

Hệ thống hỗ trợ hai cấu hình. **Cả hai đều là công dân hạng nhất**: cùng một đường code, chuyển đổi chỉ bằng biến môi trường, cùng được kiểm thử trong CI. Việc cấu hình nào là chuẩn của khóa học được quyết định bằng phép đo tại [`SPEC-INFRA-02`](#spec-infra-02), không quyết định trước.

| | Cấu hình S — server dùng chung | Cấu hình L — cục bộ |
|---|---|---|
| Máy chủ suy luận | vLLM trên GPU, API tương thích OpenAI | Ollama, endpoint tương thích OpenAI tại `/v1` |
| Model sinh văn bản | `Qwen3-8B`, hoặc lớn hơn nếu VRAM đủ | `qwen3:8b` (~5 GB) |
| Model embedding | `bge-m3` | `bge-m3` qua Ollama (~1.2 GB) |
| Cổng truy cập | LiteLLM proxy đặt trước vLLM (**NÊN**) | Không cần |
| Điểm mạnh | Chất lượng cao hơn, phục vụ đồng thời tốt | Độc lập, không có điểm hỏng chung |
| Điểm yếu | Điểm hỏng đơn, phụ thuộc mạng lớp học | Chậm, chất lượng thấp hơn |

**BẮT BUỘC: model embedding giống nhau ở cả hai cấu hình.** `bge-m3` cho 1024 chiều ở cả hai đường chạy, nên index dựng ở cấu hình nào cũng đọc được ở cấu hình kia. Nếu để hai model embedding khác nhau, học viên sẽ gặp lỗi sai lệch chiều vector giữa buổi và mất rất nhiều thời gian truy nguyên. Đây là ràng buộc tách bạch: **quyết định hạ tầng không được phép ảnh hưởng tới kho tri thức.**

**Vì sao dùng vLLM chứ không phải Ollama trên server:** Ollama xử lý gần như tuần tự, nhiều người cùng gọi sẽ xếp hàng dù có GPU. vLLM có continuous batching, phục vụ được nhiều yêu cầu đồng thời trên cùng một GPU.

**Vì sao cả hai đều phơi API tương thích OpenAI:** `LLMClient` chỉ cần một đường code, chuyển đổi bằng `LLM_BASE_URL` và `LLM_MODEL`. Nếu hai đầu dùng hai giao thức khác nhau, lớp trừu tượng sẽ phình ra và đường ít dùng sẽ không được kiểm thử — tức là hỏng đúng lúc cần đến.

<a id="spec-infra-02"></a>

### SPEC-INFRA-02 — Quy trình chọn cấu hình tham chiếu

> **BẮT BUỘC** thực hiện trước khóa học tối thiểu 1 tuần. Không được chọn cấu hình tham chiếu bằng phỏng đoán về năng lực phần cứng.

**Bước 1 — Đo năng lực server.** Chạy [`scripts/bench_server.py`](scripts/bench_server.py), đo thông lượng và độ trễ p95 ở các mức đồng thời 1, 5, 10, 20, 30 với chính prompt phân loại của khóa học.

**Bước 2 — Đối chiếu bảng quyết định.**

| VRAM khả dụng | Thông lượng đo được ở mức đồng thời 10 | Kết luận |
|---|---|---|
| ≥ 24 GB | p95 ≤ 15 giây | **Cấu hình S làm tham chiếu**, Qwen3-8B bf16 (đủ dư để thử model lớn hơn) |
| 16–24 GB | p95 ≤ 20 giây | **Cấu hình S làm tham chiếu**, Qwen3-8B lượng tử hóa 4-bit (AWQ) |
| 8–16 GB | p95 ≤ 25 giây | **Cấu hình S làm tham chiếu**, Qwen3-8B 4-bit (AWQ), nhưng giảm mức đồng thời tối đa xuống 15 |
| Bất kỳ | p95 > 25 giây, hoặc GPU dùng chung với tải khác | **Cấu hình L làm tham chiếu**; cấu hình S chỉ dùng cho phần trình diễn cuối khóa |
| Không xác định được trước khóa | — | **Cấu hình L làm tham chiếu**. An toàn hơn là hạ chuẩn giữa chừng |

**Bước 3 — Ghi nhận.** Cấu hình được chọn **BẮT BUỘC** ghi vào [Mục 17](#muc-17) kèm số liệu đo, và ghi vào [`.env.example`](.env.example) làm mặc định của lớp.

**Bước 4 — Kiểm chứng đường lùi.** Dù chọn cấu hình nào, phải chạy thử toàn bộ Lab 3 và Lab 5 trên cấu hình còn lại để bảo đảm đường lùi hoạt động.

**Nguyên tắc chọn khi phân vân:** ưu tiên cấu hình L. Hạ chuẩn giữa khóa vì server không tải nổi gây thiệt hại lớn hơn nhiều so với việc bỏ lỡ một chút chất lượng đầu ra. Cấu hình S vẫn dùng được cho phần trình diễn cuối khóa để sản phẩm trông thuyết phục, miễn là ghi rõ đó là cấu hình khác.

<a id="spec-infra-03"></a>

### SPEC-INFRA-03 — Cấu hình tham chiếu và tính so sánh được của số liệu

> **BẮT BUỘC:** Mọi chỉ số, ngưỡng đạt, cổng chất lượng CI và kết luận trong `EVALUATION.md` chỉ có giá trị khi đo trên **cấu hình tham chiếu đã chọn ở [`SPEC-INFRA-02`](#spec-infra-02)**. Số liệu đo trên cấu hình còn lại **KHÔNG** được so sánh trực tiếp, và mọi bảng kết quả phải ghi rõ cấu hình.

| Yêu cầu | Quy định |
|---|---|
| Trường bắt buộc trong log và manifest | `config_profile` nhận giá trị `S` hoặc `L` |
| Khóa cache | **BẮT BUỘC** bao gồm `base_url` và tên model, xem [`SPEC-LLM-02`](#spec-llm-02) |
| Cổng chất lượng CI | Chỉ chạy trên cache sinh từ cấu hình tham chiếu |
| Hiển thị trên giao diện | Hiện rõ đang chạy ở cấu hình nào |

Đây đồng thời là nội dung giảng dạy về tính tái lập: **một con số không kèm cấu hình sinh ra nó là một con số vô nghĩa.** Học viên gặp bài học này lần đầu ở Lab 2 khi so sánh hai cấu hình, và gặp lại ở Lab 5 khi ghi manifest.

<a id="spec-infra-04"></a>

### SPEC-INFRA-04 — Ngân sách tính toán

Ngân sách tính toán **BẮT BUỘC được ép bằng kiểm thử tự động** ở cả hai cấu hình, không dựa vào việc học viên tự thấy chậm:

| Giới hạn | Ngưỡng | Ép bằng |
|---|---|---|
| Số lần gọi LLM trên mỗi ticket | ≤ 5 | `pytest`, chạy trong CI |
| Token của prompt hệ thống | ≤ 800 | `pytest` |
| Tổng context mỗi lần gọi | ≤ 3000 token | `pytest` |
| Số lần gọi công cụ mỗi ticket | ≤ 3 | [`SPEC-TOOL-02`](#spec-tool-02) |

> **Vì sao phải ép bằng kiểm thử thay vì để phần cứng tự ép.** Ở cấu hình L, máy chậm nên học viên tự thấy đau và tự tối ưu ngữ cảnh. Ở cấu hình S với GPU trả lời trong vài giây, kỷ luật đó biến mất và học viên sẽ nhồi cả kho tài liệu vào prompt. Đặt cổng kiểm thử ngay từ đầu khiến bài học không phụ thuộc vào việc lớp chạy trên hạ tầng nào.

Ngoài ra vẫn giữ nguyên: mọi lời gọi LLM đi qua lớp cache; tác vụ chạy trên toàn tập dữ liệu phải chạy nền hoặc có bản dựng sẵn.

<a id="spec-infra-05"></a>

### SPEC-INFRA-05 — Năng lực phục vụ và đồng thời

| Tham số | Cấu hình S | Cấu hình L |
|---|---|---|
| Cơ chế phục vụ đồng thời | Continuous batching | Gần như tuần tự |
| Số worker trong ứng dụng | 8, hoặc theo kết quả đo ở [`SPEC-INFRA-02`](#spec-infra-02) | 2 |
| Độ sâu hàng đợi tối đa | 200 | 100 |
| Thời gian chờ tối đa trong hàng đợi | 10 phút | 15 phút |
| Mức đồng thời đo ở Lab 5 | 1, 5, 10, 20 | 1, 3, 5, 10 |

**BẮT BUỘC ở Lab 5: đo trên cả hai cấu hình, bất kể cấu hình nào là tham chiếu.** Cùng một đoạn code, hai đích triển khai. Chênh lệch thông lượng chính là nội dung giảng dạy — nó cho thấy nút thắt nằm ở tầng suy luận chứ không ở tầng ứng dụng, và giải thích vì sao cần điều phối container mà không phải dựng cụm để chứng minh.

**Yêu cầu tổ chức:** phép đo trên cấu hình S **BẮT BUỘC** thực hiện trong khung giờ riêng của từng nhóm, mỗi nhóm 5 phút. Nếu cả lớp cùng bắn yêu cầu, số đo mất ý nghĩa và không tái lập được. Phép đo trên cấu hình L chạy tự do vì mỗi máy độc lập.

**BẮT BUỘC** báo cáo năng lực phục vụ dưới dạng số ticket xử lý được mỗi giờ và đối chiếu với khối lượng đã giả định trong Canvas ở Lab 1.

<a id="spec-infra-06"></a>

### SPEC-INFRA-06 — Cấu hình tối thiểu máy học viên

| Hạng mục | Tối thiểu | Khuyến nghị |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Ổ trống | 10 GB | 15 GB |
| CPU | 4 nhân | 8 nhân |
| GPU | Không yêu cầu | — |
| Kết nối tới server dùng chung | Bắt buộc nếu chọn cấu hình S làm tham chiếu | — |
| Hệ điều hành | Windows 10+ / macOS 12+ / Ubuntu 20.04+ | — |

<a id="spec-infra-07"></a>

### SPEC-INFRA-07 — Phương án dự phòng hạ tầng

| Lớp | Phương án | Kích hoạt khi |
|---|---|---|
| 1 | Cấu hình tham chiếu đã chọn ở [`SPEC-INFRA-02`](#spec-infra-02) | Mặc định |
| 2 | Cấu hình còn lại | Cấu hình chính sự cố, hoặc bước kiểm thử tải ở Lab 5 |
| 3 | Chế độ chỉ dùng cache, kèm index dựng sẵn | Mất cả hai đường trên, hoặc khi trình diễn |

Chuyển đổi giữa các lớp **BẮT BUỘC** chỉ bằng biến môi trường.

**Hệ quả bắt buộc:** mọi học viên phải có **cả hai cấu hình sẵn sàng** trước Session 5, bất kể cấu hình nào được chọn làm tham chiếu. Nếu cấu hình S là tham chiếu, cấu hình L là đường lùi khi server sập — mà server sập thì cả lớp dừng, nên đường lùi này không phải tùy chọn. Nếu cấu hình L là tham chiếu, cấu hình S vẫn cần cho phép so sánh ở Lab 5 và cho phần trình diễn.

---

<a id="muc-3"></a>

## 3. KIẾN TRÚC HỆ THỐNG


<a id="spec-arch-01"></a>

### SPEC-ARCH-01 — Phân tầng

```
┌──────────────────────────────────────────────┐
│ Tầng 1 — Giao diện (Streamlit)               │
│   Nhập ticket · Màn hình duyệt · Dashboard   │
├──────────────────────────────────────────────┤
│ Tầng 2 — API (FastAPI)                       │
│   Xác thực đầu vào · Điều phối · Trả kết quả │
├──────────────────────────────────────────────┤
│ Tầng 3 — Điều phối (Orchestration)           │
│   Workflow · Định tuyến · Quyết định escalate│
├──────────────────────────────────────────────┤
│ Tầng 4 — Năng lực AI                         │
│   Phân loại · Truy hồi · Tool calling · Sinh │
├──────────────────────────────────────────────┤
│ Tầng 5 — Dữ liệu & Công cụ                   │
│   ChromaDB · SQLite · 3 công cụ giả lập      │
└──────────────────────────────────────────────┘
        ↕ Xuyên suốt: Guardrails · Logging · Cache
```

<a id="spec-arch-02"></a>

### SPEC-ARCH-02 — Nguyên tắc ràng buộc kiến trúc

1. **BẮT BUỘC — Tầng trên không gọi vượt cấp.** Tầng 2 không được gọi thẳng tầng 4. Mọi lời gọi năng lực AI đi qua tầng điều phối.
2. **BẮT BUỘC — Không có lời gọi LLM nào nằm ngoài [`src/llm/client.py`](src/llm/client.py).** Đây là điều kiện để cache, logging và ngắt mạch hoạt động đồng nhất.
3. **BẮT BUỘC — Mọi thành phần AI phải có đường dự phòng phi-AI.** Nếu LLM không phản hồi, hệ thống trả kết quả suy giảm có kiểm soát (chuyển người), không văng lỗi.
4. **NÊN — Prompt là dữ liệu, không phải code.** Đặt trong `src/agent/prompts/*.md`, nạp bằng loader, có phiên bản.
5. **BẮT BUỘC — API xử lý ticket là bất đồng bộ.** Điểm cuối tiếp nhận trả về `job_id` ngay; xử lý diễn ra ở worker nền. Mô hình đồng bộ không hợp lệ khi độ trễ mỗi yêu cầu là hàng chục giây.
6. **BẮT BUỘC — Trạng thái nằm ngoài tiến trình.** Hàng đợi, kết quả và nhật ký lưu ở SQLite hoặc Chroma, không giữ trong bộ nhớ tiến trình, để mở rộng ngang được và không mất việc khi worker khởi động lại.

<a id="spec-arch-03"></a>

### SPEC-ARCH-03 — Cấu trúc repo chuẩn

```
csc-ai-assistant/
├── PROJECT-SPEC.md              ← tài liệu này
├── README.md
├── SETUP.md
├── CHALLENGE.md
├── pyproject.toml               ← cấu hình dự án + ruff
├── uv.lock                      ← khóa phụ thuộc, BẮT BUỘC commit
├── .python-version
├── .pre-commit-config.yaml
├── promptfooconfig.yaml
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml     ← lint, test, eval, build
├── data/
│   ├── tickets/{train.jsonl, gold_test.jsonl}
│   ├── knowledge/*.md
│   ├── gold_qa.jsonl
│   └── index_prebuilt/
├── .cache/llm_cache.db          ← BẮT BUỘC commit, để CI chạy được offline
├── src/
│   ├── config.py
│   ├── llm/{client.py, cache.py, schema.py}
│   ├── knowledge/{sourcing.py, governance.py, preparation.py, embedding.py, indexing.py}
│   ├── retrieval/{transform.py, search.py, filters.py, rerank.py, pipeline.py, models.py}
│   ├── context/assemble.py
│   ├── agent/{prompts/, classifier.py, tools.py, generator.py, workflow.py}
│   ├── guardrails/{input_rules.py, output_rules.py, runtime.py}
│   ├── api/main.py
│   └── ui/app.py
├── eval/{run_eval.py, metrics.py, results/, mlruns/}
├── tests/{test_lab1.py … test_lab5.py, adversarial/}
├── scripts/{check_env.py, build_index.py, compare_models.py}
├── models/Modelfile             ← ghim tham số model
└── docs/
    ├── adr/NNNN-*.md            ← quyết định kiến trúc
    ├── canvas.md
    ├── blueprint.md
    ├── context_spec.md
    ├── EVALUATION.md
    ├── MODEL_CARD.md
    └── handover/{RUNBOOK.md, INCIDENTS.md, RESPONSIBILITIES.md}
```

<a id="spec-arch-04"></a>

### SPEC-ARCH-04 — Quy ước Git

| Hạng mục | Quy ước |
|---|---|
| Nhánh làm việc của nhóm | `team/<tên-nhóm>` |
| Nhánh cứu hộ (do giảng viên duy trì) | `solution/session-1` … `solution/session-6` |
| Định dạng commit | `[LAB-N] <mô tả>` hoặc `[SPEC-XXX-NN] <mô tả>` |
| Nộp bài | Pull request vào `main`, **BẮT BUỘC** được ≥ 1 nhóm khác review và approve trước khi merge; tag `submit/lab-N` sau khi merge |
| Chuẩn viết mã | PEP 8, docstring cho mọi hàm public, type hints cho mọi chữ ký hàm — ép tự động bằng `ruff` |

---

<a id="muc-4"></a>

## 4. CÔNG CỤ VÀ QUY TRÌNH KỸ THUẬT

<a id="spec-tooling-01"></a>

### SPEC-TOOLING-01 — Danh mục công cụ bắt buộc

| Công cụ | Vai trò | Mức | Giới thiệu tại |
|---|---|---|---|
| `git` | Quản lý mã nguồn, nhánh, tag nộp bài | BẮT BUỘC | Lab 0 |
| `uv` | Quản lý môi trường và phụ thuộc Python | BẮT BUỘC | Lab 0 |
| `ruff` | Kiểm tra và định dạng mã nguồn | BẮT BUỘC | Có sẵn, chạy tự động |
| `pre-commit` | Chặn commit vi phạm quy ước | BẮT BUỘC | Lab 0, chạy ngầm |
| `pytest` | Kiểm thử tự động từng lab | BẮT BUỘC | Lab 3 |
| GitHub Actions (hoặc GitLab CI) | Tích hợp liên tục, chạy test và eval | BẮT BUỘC | Lab 2 (giới thiệu), Lab 5 (đầy đủ) |
| ADR template | Ghi nhận quyết định kiến trúc | BẮT BUỘC | Lab 2 |
| Ollama `Modelfile` | Ghim tham số model, tái lập được cấu hình | BẮT BUỘC | Lab 2 |
| `promptfoo` | So sánh và đánh giá prompt | TÙY CHỌN | Lab 3 (phần mở rộng; [`scripts/lab3_check.py`](scripts/lab3_check.py) thay cho các bước đo bắt buộc) |
| MLflow (backend SQLite, chạy local) | Theo dõi thí nghiệm và so sánh lần chạy | BẮT BUỘC | Lab 5 |
| Docker + Docker Compose | Đóng gói và triển khai | BẮT BUỘC | Lab 5 |
| Langfuse / OpenTelemetry | Tracing LLM chuyên dụng | NGOÀI PHẠM VI | Chỉ demo, không thực hành |
| DVC | Version dữ liệu | NGOÀI PHẠM VI | Kho dữ liệu 28 tài liệu, Git là đủ |

**Nguyên tắc lựa chọn:** chỉ đưa vào những công cụ (a) chạy được offline trên laptop không GPU, (b) không cần dựng thêm dịch vụ nền, và (c) dạy được trong dưới 15 phút. Công cụ nào vi phạm một trong ba điều kiện thì chuyển sang mục demo.

<a id="spec-tooling-02"></a>

### SPEC-TOOLING-02 — Quản lý môi trường

**BẮT BUỘC** dùng `uv` thay cho `pip` và `venv`:

```bash
uv sync                  # dựng môi trường từ uv.lock
uv run python scripts/check_env.py
```

| Yêu cầu | Quy định |
|---|---|
| Tệp khóa phụ thuộc | [`uv.lock`](uv.lock) **BẮT BUỘC** commit vào repo |
| Phiên bản Python | Ghim trong [`.python-version`](.python-version) |
| Cài thêm gói ngoài lock | **BẮT BUỘC** cập nhật lock và commit kèm |

**Lý do:** `uv` dựng môi trường nhanh hơn `pip` nhiều lần, và [`uv.lock`](uv.lock) bảo đảm 30 máy học viên có cùng phiên bản thư viện. Sự khác biệt phiên bản giữa các máy là nguồn gây lỗi khó truy nhất trong lớp học thực hành.

<a id="spec-tooling-03"></a>

### SPEC-TOOLING-03 — Chất lượng mã nguồn

`pre-commit` được cấu hình sẵn trong Starter Kit, chạy tự động khi commit:

| Kiểm tra | Công cụ | Hành động khi vi phạm |
|---|---|---|
| Định dạng mã | `ruff format` | Tự sửa |
| Lỗi cú pháp và import thừa | `ruff check` | Chặn commit |
| Tệp lớn hơn 5 MB | `check-added-large-files` | Chặn commit |
| Khóa bí mật hoặc token lọt vào mã | `detect-secrets` | Chặn commit |
| Dữ liệu cá nhân thật trong tệp dữ liệu | Script tự viết, kiểm mẫu số CMND/CCCD/thẻ | Chặn commit |

Kiểm tra cuối cùng là biện pháp kỹ thuật cho [`SPEC-DATA-01`](#spec-data-01) và rủi ro R8: nhắc miệng học viên không đưa dữ liệu thật vào repo là chưa đủ.

<a id="spec-tooling-04"></a>

### SPEC-TOOLING-04 — Tích hợp liên tục

**BẮT BUỘC** mỗi nhánh nhóm có CI chạy trên mỗi lần đẩy mã:

| Giai đoạn | Nội dung | Bật từ |
|---|---|---|
| 1. Lint | `ruff check` | Lab 2 |
| 2. Test | `pytest tests/` | Lab 3 |
| 3. Eval rút gọn | Chạy đánh giá trên 15 ticket, đối chiếu ngưỡng tối thiểu | Lab 5 |
| 4. Build | Dựng image Docker | Lab 5 |

**Điểm mấu chốt khiến CI khả thi trong khóa học này:** lớp cache LLM ở [`SPEC-LLM-02`](#spec-llm-02) khiến kết quả trở nên tất định. Cache được commit vào repo, nên CI **chạy được mà không cần Ollama và không cần GPU** — chỉ đọc lại kết quả đã lưu. Không có cache thì CI cho AI application là bất khả thi trên hạ tầng lớp học.

**Cổng chất lượng (quality gate)** bật từ Lab 5:

| Chỉ số | Ngưỡng chặn merge |
|---|---|
| Accuracy phân loại | < 70% |
| Recall@5 truy hồi | < 0.75 |
| Ca đối kháng không đạt | ≥ 1 |

> Đây là thực hành phân biệt AI engineering với phát triển phần mềm truyền thống: **chất lượng mô hình được kiểm soát tự động như kiểm soát lỗi biên dịch.** Không có cổng này, học viên giữ nguyên thói quen sửa prompt rồi chạy tay xem có ổn không — đúng thói quen mà môn học cần phá bỏ.

<a id="spec-tooling-05"></a>

### SPEC-TOOLING-05 — Ghi nhận quyết định kiến trúc (ADR)

Mỗi quyết định thiết kế quan trọng là một tệp trong `docs/adr/NNNN-tieu-de.md`, theo mẫu bắt buộc:

```markdown
# ADR-0003: Chia đoạn tài liệu theo cấu trúc mục

Trạng thái: Được chấp nhận | Thay thế bởi ADR-XXXX
Ngày: 2026-09-12
Liên quan: SPEC-RAG-01

## Bối cảnh
Tài liệu chính sách có cấu trúc mục rõ ràng...

## Các phương án đã cân nhắc
1. Chia đều 500 ký tự — đơn giản nhưng cắt giữa điều khoản
2. Chia theo mục — giữ nguyên ngữ cảnh, kích thước không đều
3. Chia theo đoạn văn — ...

## Quyết định
Chọn phương án 2.

## Hệ quả chấp nhận
Một số mục dài vượt ngân sách ngữ cảnh, cần cắt phụ...
```

**BẮT BUỘC:** tối thiểu 5 ADR khi kết thúc Lab 2, và mọi thay đổi ngược lại một ADR cũ phải tạo ADR mới đánh dấu thay thế, không sửa ADR cũ. Bộ ADR chính là tài liệu dùng để bảo vệ ở Session 6.

<a id="spec-tooling-06"></a>

### SPEC-TOOLING-06 — Quản lý phiên bản prompt và thí nghiệm

| Hạng mục | Công cụ | Quy định |
|---|---|---|
| Lưu trữ prompt | Tệp `.md` có đánh số phiên bản | [`SPEC-PROMPT-02`](#spec-prompt-02) |
| So sánh phiên bản prompt | `promptfoo` với provider Ollama | Cấu hình tại [`promptfooconfig.yaml`](promptfooconfig.yaml), chạy offline |
| Theo dõi lần chạy đánh giá | MLflow local, backend SQLite | Thay cho `run_manifest.json` thủ công |
| Nội dung ghi vào MLflow | Tham số, chỉ số, artifact | Xem [`SPEC-EVAL-03`](#spec-eval-03) |

`promptfoo` được chọn vì hỗ trợ Ollama sẵn, chạy hoàn toàn offline, và biến việc so sánh prompt từ thao tác cảm tính thành một bảng kết quả có số. MLflow chạy local với backend SQLite không cần dựng máy chủ, khởi động bằng một lệnh.

<a id="spec-tooling-07"></a>

### SPEC-TOOLING-07 — Sử dụng AI làm công cụ phát triển

Khóa học **cho phép** học viên dùng trợ lý lập trình AI trong quá trình thực hành, với hai ràng buộc:

1. **BẮT BUỘC** học viên giải thích được mọi dòng mã trong bài nộp. Phần phản biện ở Session 6 sẽ kiểm tra điều này.
2. **BẮT BUỘC** phần thiết kế — Canvas, Blueprint, ADR, điều kiện chuyển người, luật guardrail — do học viên tự quyết định. AI có thể hỗ trợ diễn đạt, không thay thế quyết định.

Session 6 dành 10 phút thảo luận: điều gì thay đổi trong quy trình review và kiểm thử khi phần lớn mã do AI sinh ra, và vì sao cổng chất lượng tự động trở nên quan trọng hơn chứ không kém đi.

---

<a id="muc-5"></a>

## 5. HỢP ĐỒNG DỮ LIỆU (DATA CONTRACT)

<a id="spec-data-01"></a>

### SPEC-DATA-01 — Nguyên tắc tối thượng

> **BẮT BUỘC:** Toàn bộ dữ liệu sử dụng trong khóa học là **dữ liệu sinh tổng hợp**. Nghiêm cấm đưa dữ liệu khách hàng thật, dữ liệu nội bộ chưa được phê duyệt công bố, hoặc bất kỳ thông tin định danh cá nhân thật nào vào repo, kể cả trong file test hoặc ảnh chụp màn hình.

Số thuê bao trong dữ liệu mẫu **BẮT BUỘC** dùng dải không tồn tại thực tế và được che một phần trong mọi hiển thị.

<a id="spec-data-02"></a>

### SPEC-DATA-02 — Lược đồ ticket

```json
{
  "id": "TK-00042",
  "channel": "app | hotline | email",
  "created_at": "2026-03-14T09:20:00+07:00",
  "customer_msg": "<văn bản thô, tiếng Việt, 20–400 từ>",
  "subscriber_id": "0987xxxxxx",
  "attachments": [],
  "label": {
    "category": "cuoc_thanh_toan",
    "priority": "P1 | P2 | P3",
    "sentiment": "trung_tinh | buc_boi | gay_gat"
  },
  "meta": {
    "is_ambiguous": false,
    "has_pii": false,
    "expected_action": "auto_draft | escalate"
  }
}
```

<a id="spec-data-03"></a>

### SPEC-DATA-03 — Bảng phân loại (taxonomy)

| Mã nhóm | Tên | Phạm vi |
|---|---|---|
| `cuoc_thanh_toan` | Cước và thanh toán | Sai cước, tranh chấp hóa đơn, phương thức thanh toán |
| `chat_luong_ket_noi` | Chất lượng kết nối | Mất sóng, chậm, gián đoạn dịch vụ |
| `goi_cuoc_khuyen_mai` | Gói cước và khuyến mãi | Đăng ký/hủy gói, điều kiện ưu đãi |
| `thiet_bi_sim` | Thiết bị và SIM | Đổi SIM, hỏng thiết bị, cấu hình |
| `thong_tin_thue_bao` | Thông tin thuê bao | Đổi thông tin, hợp đồng, chuyển nhượng |
| `khac` | Khác | Không thuộc 5 nhóm trên hoặc không xác định |

**Quy tắc gán mức ưu tiên:**

| Mức | Điều kiện |
|---|---|
| `P1` | Mất dịch vụ hoàn toàn, ảnh hưởng doanh nghiệp, hoặc khách hàng đe dọa khiếu nại lên cơ quan quản lý |
| `P2` | Ảnh hưởng trải nghiệm rõ rệt hoặc có tranh chấp tiền |
| `P3` | Yêu cầu thông tin, thao tác thông thường |

<a id="spec-data-04"></a>

### SPEC-DATA-04 — Cơ cấu tập dữ liệu

| Tập | Số lượng | Mục đích | Ràng buộc |
|---|---|---|---|
| `train.jsonl` | 80 ticket | Phát triển, thử prompt | Công khai từ Lab 3 |
| `gold_test.jsonl` | 40 ticket | Đánh giá cuối | **BẮT BUỘC giữ kín tới Lab 5** |
| `knowledge/` | 28 tài liệu | Kho tri thức | 1–3 trang mỗi tài liệu |
| `gold_qa.jsonl` | 40 cặp hỏi–đáp | Đánh giá truy hồi | Có `expected_doc_ids` |
| [`tests/adversarial/`](tests/adversarial/) | 12 ca | Kiểm thử guardrails | Xem [`SPEC-GUARD-04`](#spec-guard-04) |

**Lý do giữ kín `gold_test.jsonl`:** nếu học viên nhìn thấy tập test khi tinh chỉnh prompt, con số đánh giá ở Lab 5 mất hoàn toàn ý nghĩa.

<a id="spec-data-05"></a>

### SPEC-DATA-05 — Bẫy sư phạm bắt buộc cài trong dữ liệu

| Loại bẫy | Số lượng | Mục đích giảng dạy |
|---|---|---|
| Tài liệu chính sách mâu thuẫn (bản cũ chưa gỡ + bản mới) | 2 cặp | Quản lý phiên bản tri thức |
| Câu hỏi không có đáp án trong kho | 5 | Dạy hệ thống biết nói "không đủ căn cứ" |
| Ticket mơ hồ, có thể gán 2 nhãn | 8 | Ngưỡng tin cậy và escalation |
| Ticket chứa thông tin cá nhân nhạy cảm | 3 | Guardrail PII |
| Ticket rác / vô nghĩa | 2 | Xử lý lỗi có kiểm soát |

<a id="spec-data-06"></a>

### SPEC-DATA-06 — Lược đồ tài liệu tri thức

Mỗi file `.md` trong [`data/knowledge/`](data/knowledge/) **BẮT BUỘC** có front-matter:

```yaml
---
doc_id: KB-012
title: Quy định bồi thường gián đoạn dịch vụ
category: cuoc_thanh_toan
version: 2.1
effective_date: 2026-01-01
supersedes: KB-007
status: active | superseded
---
```

Trường `supersedes` và `status` là công cụ để giải quyết bẫy tài liệu mâu thuẫn ở [`SPEC-DATA-05`](#spec-data-05).

---

<a id="muc-6"></a>

## 6. CHÍNH SÁCH LỚP LLM

<a id="spec-llm-01"></a>

### SPEC-LLM-01 — Giao diện thống nhất

Mọi lời gọi LLM đi qua `LLMClient` với chữ ký cố định:

```python
client.generate(
    prompt: str,
    system: str | None = None,
    schema: Type[BaseModel] | None = None,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    tools: list[ToolSpec] | None = None,
    trace_id: str | None = None,
) -> LLMResponse
```

`LLMResponse` **BẮT BUỘC** chứa: `content`, `parsed`, `model`, `config_profile`, `latency_ms`, `cache_hit`, `attempts`, `finish_reason`.

<a id="spec-llm-02"></a>

### SPEC-LLM-02 — Cache

| Hạng mục | Quy định |
|---|---|
| Khóa cache | `sha256(base_url + model + system + prompt + temperature + max_tokens + tools_signature)` |
| Nơi lưu | SQLite tại `.cache/llm_cache.db` |
| Bỏ qua cache | Chỉ khi `temperature > 0` **và** cờ `no_cache=True` |
| Chia sẻ | Cache dựng sẵn được đóng gói cùng Starter Kit |

**Lý do đưa `base_url`, `model` và `temperature` vào khóa:** thiếu chúng sẽ khiến thí nghiệm so sánh cấu hình ở Lab 2 trả về kết quả giống hệt nhau, và tệ hơn, cache sinh từ cấu hình suy giảm sẽ lẫn vào cấu hình tham chiếu làm hỏng toàn bộ số liệu đánh giá — một lỗi rất khó phát hiện.

<a id="spec-llm-03"></a>

### SPEC-LLM-03 — Cấu hình tham số theo tác vụ

| Tác vụ | temperature | max_tokens | Ghi chú |
|---|---|---|---|
| Phân loại, trích xuất | `0.0` | 300 | **BẮT BUỘC** temperature = 0 |
| Viết lại truy vấn | `0.0` | 100 | |
| Sinh phản hồi khách hàng | `0.3` | 800 | **NÊN** không vượt quá 0.5 |
| Tóm tắt | `0.2` | 400 | |

<a id="spec-llm-04"></a>

### SPEC-LLM-04 — Đầu ra có cấu trúc

Bốn lớp phòng vệ, **BẮT BUỘC** cài đủ:

1. **Khai báo schema** bằng Pydantic, kèm mô tả từng trường trong prompt
2. **Bóc tách** JSON khỏi văn bản thừa (```json, lời dẫn, giải thích sau)
3. **Retry** tối đa 2 lần; lần retry đưa nguyên văn thông báo lỗi validation vào prompt
4. **Fallback** khi vẫn thất bại: trả `category="khac"`, `confidence=0.0`, `requires_human=True`

**BẮT BUỘC:** mọi lần fallback được ghi log với `trace_id` để đo tỉ lệ ở Lab 5.

<a id="spec-llm-05"></a>

### SPEC-LLM-05 — Ngắt mạch (circuit breaker)

| Tham số | Giá trị |
|---|---|
| Timeout mỗi lời gọi | 60 giây |
| Số lần lỗi liên tiếp trước khi ngắt | 3 |
| Thời gian ngắt | 60 giây |
| Hành vi khi ngắt | Toàn bộ ticket chuyển thẳng sang hàng đợi người xử lý |

---

<a id="muc-7"></a>

## 7. CHÍNH SÁCH PROMPT

<a id="spec-prompt-01"></a>

### SPEC-PROMPT-01 — Cấu trúc bắt buộc

Mọi prompt hệ thống **BẮT BUỘC** có đủ 5 phần, theo đúng thứ tự:

```
1. VAI TRÒ      — hệ thống là ai, phục vụ ai
2. NHIỆM VỤ     — chính xác một nhiệm vụ, không gộp
3. RÀNG BUỘC    — được làm gì, cấm làm gì
4. NGỮ CẢNH     — dữ liệu đầu vào, phân tách rõ bằng thẻ
5. ĐỊNH DẠNG    — mô tả schema đầu ra, kèm 1–2 ví dụ
```

<a id="spec-prompt-02"></a>

### SPEC-PROMPT-02 — Quy định kỹ thuật

| # | Quy định | Mức |
|---|---|---|
| 1 | Ngữ cảnh do người dùng cung cấp phải bọc trong thẻ rõ ràng (`<ticket>`, `<knowledge>`) | BẮT BUỘC |
| 2 | Prompt lưu ở `src/agent/prompts/<tên>.v<N>.md`, không hardcode trong code Python | BẮT BUỘC |
| 3 | Mỗi phiên bản prompt giữ lại, không ghi đè — để so sánh ở Lab 5/6 | BẮT BUỘC |
| 4 | Một prompt = một nhiệm vụ. Không gộp phân loại và sinh phản hồi vào cùng một lần gọi | BẮT BUỘC |
| 5 | Ví dụ few-shot: 2–3 ví dụ, ưu tiên ca khó và ca biên | NÊN |
| 6 | Prompt viết bằng tiếng Việt cho tác vụ tiếng Việt | NÊN |

**Lý do quy định #4:** gộp nhiều nhiệm vụ khiến model 3B suy giảm chất lượng rõ rệt, và làm mất khả năng đo riêng từng bước ở Lab 5.

<a id="spec-prompt-03"></a>

### SPEC-PROMPT-03 — Ràng buộc bắt buộc trong prompt sinh phản hồi

Prompt sinh phản hồi khách hàng **BẮT BUỘC** chứa đủ các ràng buộc sau:

- Chỉ sử dụng thông tin có trong `<knowledge>` và `<tool_results>`
- Mọi khẳng định về chính sách phải kèm trích dẫn `[doc_id, mục]`
- Không cam kết số tiền bồi thường cụ thể
- Không cam kết thời hạn xử lý cụ thể
- Không suy đoán nguyên nhân kỹ thuật nếu không có dữ liệu công cụ xác nhận
- Nếu không đủ căn cứ, trả về đúng chuỗi `INSUFFICIENT_CONTEXT`

---

<a id="muc-8"></a>

## 8. CHÍNH SÁCH TRI THỨC VÀ TRUY HỒI (RAG)

<a id="spec-rag-01"></a>

### SPEC-RAG-01 — Chunking

| Tham số | Giá trị mặc định | Ghi chú |
|---|---|---|
| Chiến lược | Theo cấu trúc mục của tài liệu | **NÊN**; nếu đổi phải ghi ADR mới |
| Kích thước mục tiêu | 400–700 token | |
| Độ chồng lấp | 80 token | |
| Tiền tố mỗi chunk | `[{title}] [{mục}]` prepend trước khi embed | **BẮT BUỘC** |
| Metadata giữ lại | `doc_id`, `title`, `section`, `version`, `effective_date`, `status` | **BẮT BUỘC** |

**Lý do prepend tiêu đề:** chunk cắt giữa tài liệu thường mất ngữ cảnh chủ đề; prepend tiêu đề cải thiện Recall@5 đáng kể với chi phí gần như bằng không. Đây là thí nghiệm bắt buộc ở Lab 3.

<a id="spec-rag-02"></a>

### SPEC-RAG-02 — Truy hồi

| Tham số | Giá trị |
|---|---|
| Vector store | ChromaDB, persistent |
| Số kết quả trả về | `k = 5` |
| Ngưỡng điểm tối thiểu | `0.62` (điểm hybrid với `bge-m3`; **BẮT BUỘC** hiệu chuẩn lại khi đổi model embedding, chiến lược chia đoạn hoặc kiểu tìm) |
| Lọc theo trạng thái | **BẮT BUỘC** loại chunk có `status = superseded` |
| Viết lại truy vấn | **NÊN** — rút gọn ticket dài thành câu truy vấn trước khi tìm |

<a id="spec-rag-03"></a>

### SPEC-RAG-03 — Quy tắc "không đủ căn cứ"

**BẮT BUỘC:** Nếu sau truy hồi mà không có chunk nào vượt ngưỡng điểm, hệ thống **không được sinh phản hồi**. Ticket chuyển thẳng sang hàng đợi người xử lý với lý do `NO_KNOWLEDGE_MATCH`.

Đây là ranh giới quan trọng nhất của cả hệ thống: một trợ lý CSKH bịa ra chính sách là rủi ro nghiệp vụ nghiêm trọng hơn nhiều so với một trợ lý im lặng.

<a id="spec-rag-04"></a>

### SPEC-RAG-04 — Trích dẫn

Mọi phản hồi sinh ra **BẮT BUỘC** kèm danh sách nguồn dạng cấu trúc:

```json
"citations": [
  {"doc_id": "KB-012", "section": "3.2", "score": 0.71}
]
```

Phản hồi không có trích dẫn bị guardrail đầu ra chặn (xem [`SPEC-GUARD-02`](#spec-guard-02)).


<a id="spec-rag-05"></a>

### SPEC-RAG-05 — Kiến trúc pipeline tri thức và truy hồi

Mã của phần tri thức đi theo đúng ba sơ đồ trong slide Session 3: vòng đời tri thức (slide 34), RAG Pipeline (slide 39) và Context Engineering Pipeline (slide 24). Mỗi giai đoạn của sơ đồ là một hàm trong một module, để từ slide tìm được mã và từ mã tìm được slide.

| Giai đoạn (slide) | Module | Hàm chính | Mã spec |
|---|---|---|---|
| Discover (34) | [`src/knowledge/sourcing.py`](src/knowledge/sourcing.py) | `discover_documents` | [SPEC-RAG-06](#spec-rag-06) |
| Ingest, Parse (34, 39) | [`src/knowledge/sourcing.py`](src/knowledge/sourcing.py) | `ingest_document`, `parse_front_matter` | [SPEC-RAG-06](#spec-rag-06) |
| Govern (34) | [`src/knowledge/governance.py`](src/knowledge/governance.py) | `load_documents`, `conflict_report` | [SPEC-DATA-05](#spec-data-05), [SPEC-DATA-06](#spec-data-06) |
| Prepare, Organize & Enrich, Chunk (34, 39) | [`src/knowledge/preparation.py`](src/knowledge/preparation.py) | `chunk_document` | [SPEC-RAG-07](#spec-rag-07) |
| Embed (39) | [`src/knowledge/embedding.py`](src/knowledge/embedding.py) | `embed_chunks` | [SPEC-RAG-08](#spec-rag-08) |
| Index (39) | [`src/knowledge/indexing.py`](src/knowledge/indexing.py) | `build_index`, `find_index`, `read_index` | [SPEC-RAG-06](#spec-rag-06) |
| Query Transformation (39) | [`src/retrieval/transform.py`](src/retrieval/transform.py) | `rewrite_query` | [SPEC-RAG-02](#spec-rag-02) |
| Retrieve (39, 40) | [`src/retrieval/search.py`](src/retrieval/search.py) | `hybrid_search` | [SPEC-RAG-09](#spec-rag-09) |
| Filter (39, 44) | [`src/retrieval/filters.py`](src/retrieval/filters.py) | `filter_hits`, `judge_evidence` | [SPEC-RAG-10](#spec-rag-10) |
| Rerank (39, 44) | [`src/retrieval/rerank.py`](src/retrieval/rerank.py) | `rerank` | [SPEC-RAG-09](#spec-rag-09) |
| Select, Assemble (24, 39) | [`src/context/assemble.py`](src/context/assemble.py) | `assemble_context` | [SPEC-CTX-01](#spec-ctx-01) |
| Điều phối pha runtime | [`src/retrieval/pipeline.py`](src/retrieval/pipeline.py) | `Retriever.retrieve` | [SPEC-RAG-09](#spec-rag-09) |

**Quy tắc phụ thuộc (BẮT BUỘC):**

1. [`src/knowledge/`](src/knowledge/) không import [`src/retrieval/`](src/retrieval/) hay [`src/context/`](src/context/). Tri thức được dựng trước, truy hồi đọc chỉ mục qua [`src/knowledge/indexing.py`](src/knowledge/indexing.py).
2. Mọi lời gọi model (embedding và sinh văn bản) đi qua [`src/llm/client.py`](src/llm/client.py) ([`SPEC-ARCH-02`](#spec-arch-02) nguyên tắc 2).
3. Không module nào đọc thẳng [`data/knowledge/`](data/knowledge/) ngoài `sourcing.py`, và không module nào đọc thẳng tệp chỉ mục ngoài `indexing.py`.

**Viết mã với trợ lý AI.** Các spec [`SPEC-RAG-07`](#spec-rag-07) đến [`SPEC-RAG-10`](#spec-rag-10) và [`SPEC-CTX-01`](#spec-ctx-01) mỗi cái tự đủ để giao cho một trợ lý AI viết một hàm: chữ ký hàm, dữ liệu vào và ra, quy tắc, các trường hợp biên và bài kiểm thử phải qua. Dán spec, mô tả (docstring) của hàm và bài kiểm thử tương ứng cho trợ lý, rồi kiểm chứng bằng `pytest -m lab3` ([`SPEC-TOOLING-07`](#spec-tooling-07): mọi dòng mã nộp bài phải giải thích được).

<a id="spec-rag-06"></a>

### SPEC-RAG-06 — Hợp đồng dữ liệu của tri thức

**Document** (`sourcing.Document`): `doc_id`, `title`, `category` (một trong sáu nhóm ticket), `version`, `effective_date` (`YYYY-MM-DD`), `status` (`active` hoặc `superseded`), `supersedes` (mã tài liệu bị thay thế hoặc rỗng), `body` (nội dung Markdown đã bỏ front-matter), `path`. Thiếu một trong sáu trường đầu ở front-matter thì `ingest_document` ném `ValueError` nêu tên tệp và trường thiếu.

**Chunk** (`preparation.Chunk`): `chunk_id`, `doc_id`, `doc_title`, `section`, `category`, `version`, `effective_date`, `text`.

- `chunk_id` có dạng `{doc_id}#{số thứ tự hai chữ số}`, số thứ tự tăng dần trong một tài liệu, ví dụ `KB-001#03`.
- `section` là tiêu đề mục. Đoạn thứ hai trở đi của cùng một mục thêm hậu tố ` (tiếp)`.
- Văn bản đem nhúng là `doc_title — section` xuống dòng rồi `text` (`Chunk.embedding_text()`), để vector mang tên tài liệu và tên mục.

**Chỉ mục** (`index.json`, do `indexing.build_index` ghi, do `indexing.read_index` đọc):

```json
{
  "config_profile": "L",
  "embed_model": "bge-m3",
  "chunk_size": 700,
  "chunks": [
    {"chunk_id": "KB-001#00", "doc_id": "KB-001", "doc_title": "…", "section": "…",
     "category": "cuoc_thanh_toan", "version": "3.0", "effective_date": "2026-01-01",
     "text": "…", "embedding": [0.01, -0.02, "… 1024 số với bge-m3"]}
  ]
}
```

Tìm chỉ mục theo thứ tự: thư mục `CHROMA_PATH` (chỉ mục tự dựng), rồi [`data/index_prebuilt/`](data/index_prebuilt/) (bản dựng sẵn). Không có tệp nào thì `Retriever` dựng chỉ mục từ khóa trong bộ nhớ.

<a id="spec-rag-07"></a>

### SPEC-RAG-07 — Chia đoạn: `chunk_document`

`chunk_document(doc: Document, *, max_chars: int | None = None, overlap: int | None = None) -> list[Chunk]` trong [`src/knowledge/preparation.py`](src/knowledge/preparation.py). Mở rộng [`SPEC-RAG-01`](#spec-rag-01).

**Quy tắc:**

1. `max_chars` bỏ trống thì lấy `settings.chunk_size`. `overlap` bỏ trống thì lấy `settings.chunk_overlap`. `overlap = 0` là giá trị hợp lệ.
2. Chia theo mục bằng `split_sections(doc)` (đã có sẵn, trả về danh sách cặp tiêu đề và nội dung).
3. Mục có độ dài không quá `max_chars` thành một đoạn. Mục dài hơn được cắt bằng `_split_long(text, max_chars, overlap)` (đã có sẵn), cắt theo ranh giới câu và có chồng lấn.
4. Mỗi đoạn mang đủ trường theo [`SPEC-RAG-06`](#spec-rag-06). `text` đã bỏ khoảng trắng đầu và cuối. `chunk_id` đánh số liên tục trong toàn tài liệu, không đặt lại theo mục.
5. Tài liệu không có tiêu đề mục thì cả thân là một mục có tiêu đề là `title` của tài liệu (đã được `split_sections` xử lý).

**Nghiệm thu** (`pytest -m lab3 -k chunk`): mỗi đoạn có `doc_id`, `version`, `effective_date`, và tiêu đề tài liệu nằm trong `embedding_text()`; tài liệu nhiều mục cho nhiều đoạn theo mục; không đoạn nào dài hơn `1.5 × chunk_size`.

**Sai lầm thường gặp:** cắt cứng theo số ký tự làm đứt điều khoản; quên hậu tố ` (tiếp)`; đặt lại số thứ tự `chunk_id` ở mỗi mục nên trùng mã.

<a id="spec-rag-08"></a>

### SPEC-RAG-08 — Embedding: `embed_chunks`

`embed_chunks(chunks: list[Chunk], client, *, batch_size: int = 16, on_progress=None) -> list[list[float]]` trong [`src/knowledge/embedding.py`](src/knowledge/embedding.py).

**Quy tắc:**

1. `batch_size` nhỏ hơn 1 thì ném `ValueError`.
2. Gửi `client.embed(texts)` theo từng lô `batch_size` đoạn, với `texts` là `chunk.embedding_text()` của từng đoạn trong lô, đúng thứ tự.
3. Vector trả về cùng thứ tự với `chunks`, mỗi đoạn đúng một vector.
4. Lô nào model trả về số vector khác số đoạn đã gửi thì ném `ValueError` nêu hai con số.
5. Có `on_progress` thì gọi sau mỗi lô với (số đoạn đã nhúng, tổng số đoạn).
6. Danh sách rỗng trả về danh sách rỗng, không gọi model.

**Ràng buộc hạ tầng:** model embedding giống nhau ở cả hai cấu hình ([`SPEC-INFRA-01`](#spec-infra-01)). `bge-m3` cho vector 1024 chiều. Đổi model thì mọi vector cũ vô nghĩa và phải dựng lại chỉ mục.

**Nghiệm thu** (`pytest -m lab3 -k embed`): đúng số lô và thứ tự; văn bản gửi là `embedding_text()`; báo tiến độ; từ chối `batch_size = 0` và số vector sai.

<a id="spec-rag-09"></a>

### SPEC-RAG-09 — Tìm kiếm và pipeline runtime: `hybrid_search` và `Retriever.retrieve`

`hybrid_search(query, chunks, *, query_vector=None, top_k=5, vector_weight=0.75, hybrid=True) -> list[Hit]` trong [`src/retrieval/search.py`](src/retrieval/search.py). Mở rộng [`SPEC-RAG-02`](#spec-rag-02).

**Cách chấm điểm** cho mỗi đoạn (ba kiểu ở slide 40):

| Điều kiện | Điểm |
|---|---|
| Không có `query_vector`, hoặc đoạn không có `embedding` | `keyword` |
| Có vector, `hybrid=True` | `vector_weight × cosine + (1 − vector_weight) × keyword` |
| Có vector, `hybrid=False` | `cosine` (semantic thuần) |

`keyword` = tỉ lệ từ (viết thường) của truy vấn có mặt trong tập từ của đoạn (tiêu đề tài liệu, tiêu đề mục và nội dung), dùng `keyword_score` và `chunk_tokens` (đã có sẵn). `cosine` dùng hàm `cosine` (đã có sẵn).

Trả về tối đa `top_k` `Hit`, sắp giảm dần theo điểm, `score` làm tròn 4 chữ số, mang đủ `chunk_id`, `doc_id`, `doc_title`, `section`, `version`, `effective_date`, `category`, `text`.

**`Retriever.retrieve`** (đã có sẵn, ghép các bước) chạy theo thứ tự: văn bản tìm là `rewritten or query` → lấy vector truy vấn nếu chỉ mục có vector → `hybrid_search` → `filter_hits` → `rerank` (chỉ khi `RERANK_ENABLED=true`) → `judge_evidence` → `RetrievalResult`.

**Vector truy vấn** chỉ được dùng khi chỉ mục có vector, `RETRIEVE_MODE` khác `keyword`, `CACHE_MODE` khác `cache_only` và model embedding phản hồi. Model không phản hồi thì rơi về keyword, `RetrievalResult.mode` ghi `keyword` (suy giảm có kiểm soát, [`SPEC-ARCH-02`](#spec-arch-02) nguyên tắc 3).

**Tham số cấu hình:** `RETRIEVE_TOP_K` (5), `RETRIEVE_MODE` (`auto` hoặc `keyword`), `RETRIEVE_VECTOR_WEIGHT` (0.75), `RERANK_ENABLED` (`false`), `EMBED_BATCH_SIZE` (16).

**Nghiệm thu** (`pytest -m lab3 -k "search or retriever or cosine"`): keyword khi không có vector; semantic thuần xếp theo vector; hybrid đúng công thức; tối đa `top_k`; kết quả sắp giảm dần và điểm nằm trong [0, 1].

<a id="spec-rag-10"></a>

### SPEC-RAG-10 — Đủ căn cứ và ngưỡng: `judge_evidence`

`judge_evidence(hits: list[Hit], min_score: float) -> tuple[bool, str]` trong [`src/retrieval/filters.py`](src/retrieval/filters.py). Cài đặt [`SPEC-RAG-03`](#spec-rag-03).

| Điều kiện | Kết quả |
|---|---|
| `hits` rỗng | `(False, "Kho tri thức không trả về kết quả nào.")` |
| `hits[0].score < min_score` | `(False, lý do chứa cụm "Không đủ căn cứ" và nêu điểm cao nhất cùng ngưỡng)` |
| còn lại (kể cả điểm bằng ngưỡng) | `(True, "Đủ căn cứ.")` |

`hits` đã sắp giảm dần nên chỉ cần xét phần tử đầu. Kiểm tra này diễn ra **trước** khi gọi model sinh phản hồi ([`ADR-0005`](docs/adr/0005-nguong-tu-choi-thay-vi-doan.md)).

**Ngưỡng mặc định `0.62`** được chọn từ bảng quét ngưỡng (`uv run python scripts/lab3_check.py retrieval --sweep`) trên bộ 45 câu hỏi vàng, tìm kiếm hybrid với `bge-m3`: điểm cao nhất của 5 câu không có đáp án nằm trong 0.51 đến 0.59, của 40 câu có đáp án từ 0.65 đến 0.86, nên ngưỡng từ 0.60 đến 0.65 cho tỉ lệ từ chối đúng 1.00 và từ chối thừa 0.00. Với tìm kiếm chỉ dùng từ khóa, hai khoảng điểm chồng nhau (0.44 đến 0.73 so với 0.62 đến 1.00) nên không ngưỡng nào tách sạch, và ngưỡng 0.35 cũ cho tỉ lệ từ chối đúng 0/5.

**BẮT BUỘC hiệu chuẩn lại** ngưỡng khi đổi model embedding, chiến lược chia đoạn, kiểu tìm hoặc bộ tài liệu, rồi ghi ngưỡng mới cùng bảng quét vào [`docs/context_spec.md`](docs/context_spec.md).

`filter_hits(hits, *, categories=None, as_of=None)` (đã có sẵn) loại kết quả theo nhóm và theo ngày hiệu lực; dùng để chống Stale Retrieval (slide 44).

**Nghiệm thu** (`pytest -m lab3 -k judge`): ba nhánh ở bảng trên, gồm cả trường hợp điểm bằng ngưỡng.

<a id="spec-ctx-01"></a>

### SPEC-CTX-01 — Ghép context: `assemble_context`

`assemble_context(hits: list[Hit], max_chars: int = 2000) -> str` trong [`src/context/assemble.py`](src/context/assemble.py). Cài đặt các bước Select, Transform và Assemble của Context Engineering Pipeline (slide 24) cho phần tri thức.

**Quy tắc:**

1. Mỗi đoạn thành một khối: dòng đầu là trích dẫn, tiêu đề tài liệu, dấu `—`, tiêu đề mục; dòng sau là nội dung. Cụ thể: `[{doc_id} v{version}, hiệu lực {effective_date}] {doc_title} — {section}` xuống dòng rồi `text`.
2. Các khối theo đúng thứ tự `hits`, cách nhau một dòng trống.
3. Ngân sách tính bằng số ký tự của các khối (không tính dòng trống ngăn cách). Khối nào làm tổng vượt `max_chars` thì dừng ở đó: không cắt cụt giữa đoạn, không bỏ qua khối đó để lấy khối nhỏ hơn phía sau.
4. Không có đoạn nào vừa ngân sách, hoặc `hits` rỗng, thì trả chuỗi rỗng.

**Ngân sách:** `max_chars = 2000` ứng với khoảng 625 token (hệ số 3.2 ký tự mỗi token), nằm trong phần dành cho tri thức của tổng 3.000 token mỗi lời gọi ([`SPEC-INFRA-04`](#spec-infra-04)). Nhiều context không đồng nghĩa với context tốt hơn (slide 25).

**Nghiệm thu** (`pytest -m lab3 -k assemble`): đúng khuôn, đúng thứ tự, dừng đúng ngân sách, rỗng khi không vừa.

<a id="spec-ctx-02"></a>

### SPEC-CTX-02 — Sáu thành phần của context trong hệ thống này

Ghép slide 20 và 21 với hệ thống, để biết một thành phần nào của context đến từ đâu:

| Thành phần | Nguồn trong hệ thống | Bước của [`SPEC-FLOW-01`](#spec-flow-01) |
|---|---|---|
| Instructions / Constraints | `src/agent/prompts/*.md` ([`SPEC-PROMPT-01`](#spec-prompt-01)) | mọi bước gọi model |
| Enterprise Knowledge | `assemble_context` trên kết quả truy hồi | Truy hồi tri thức |
| Subscriber State | kết quả `get_subscriber_info` | Gọi công cụ |
| Tool Results | `ToolRunner.results_block` | Gọi công cụ |
| Conversation / Task State | chưa có (mỗi ticket độc lập, không có lịch sử hội thoại) | — |
| System State | `trace_id`, lý do chuyển người tích lũy trong `process_ticket` | toàn quy trình |
| Permissions | guardrail và ranh giới công cụ chỉ đọc ([`SPEC-TOOL-02`](#spec-tool-02)); xác thực người dùng ngoài phạm vi | Guardrail |

Năm phép kiểm tra chất lượng context của slide 22 (Sufficient, Relevant, Fresh, Consistent, Trusted) tương ứng: ngưỡng đủ căn cứ ([`SPEC-RAG-10`](#spec-rag-10)), top-k cộng ngân sách ([`SPEC-CTX-01`](#spec-ctx-01)), lọc `status` ([`SPEC-DATA-06`](#spec-data-06)), xử lý hai cặp tài liệu mâu thuẫn ([`SPEC-DATA-05`](#spec-data-05)), thẻ `<ticket>` cộng guardrail đầu vào ([`SPEC-GUARD-01`](#spec-guard-01)).


---

<a id="muc-9"></a>

## 9. CHÍNH SÁCH CÔNG CỤ (TOOL)

<a id="spec-tool-01"></a>

### SPEC-TOOL-01 — Danh mục công cụ

| Tên | Tham số | Trả về | Nguồn |
|---|---|---|---|
| `get_subscriber_info` | `subscriber_id` | Gói cước, ngày kích hoạt, trạng thái | JSON giả lập |
| `get_billing_history` | `subscriber_id`, `months` | Cước 6 tháng gần nhất | JSON giả lập |
| `check_area_incident` | `area_code`, `date` | Có/không sự cố hạ tầng | JSON giả lập |

**BẮT BUỘC:** không công cụ nào kết nối hệ thống thật.

<a id="spec-tool-02"></a>

### SPEC-TOOL-02 — Ràng buộc thực thi

| # | Quy định |
|---|---|
| 1 | Tất cả công cụ là **chỉ đọc**. Không có công cụ nào ghi/sửa/xóa dữ liệu. |
| 2 | Timeout mỗi công cụ: 5 giây. |
| 3 | Tối đa 3 lần gọi công cụ trên một ticket. |
| 4 | Tham số **BẮT BUỘC** được validate bằng schema trước khi thực thi. |
| 5 | Công cụ lỗi → ghi log, tiếp tục workflow với ghi chú "thiếu dữ liệu", không dừng hệ thống. |

<a id="spec-tool-03"></a>

### SPEC-TOOL-03 — Đường dự phòng theo luật

Do model 3B gọi công cụ không ổn định, **BẮT BUỘC** có tầng dự phòng dựa trên luật:

| Điều kiện | Công cụ gọi tự động |
|---|---|
| `category = cuoc_thanh_toan` và có `subscriber_id` | `get_billing_history` |
| `category = chat_luong_ket_noi` và có `subscriber_id` | `check_area_incident` |
| Mọi ticket có `subscriber_id` hợp lệ | `get_subscriber_info` |

Việc phải xây dựng đường dự phòng cho quyết định của AI là một nguyên tắc thiết kế, không phải sự thỏa hiệp kỹ thuật.

---

<a id="muc-10"></a>

## 10. CHÍNH SÁCH QUY TRÌNH VÀ CHUYỂN NGƯỜI

<a id="spec-flow-01"></a>

### SPEC-FLOW-01 — Luồng chuẩn

```
Ticket vào
  └─ Guardrail đầu vào ────────── vi phạm ──> CHUYỂN NGƯỜI
  └─ Phân loại + trích xuất
        └─ confidence < 0.60 ───────────────> CHUYỂN NGƯỜI
        └─ Gọi công cụ (nếu áp dụng)
        └─ Truy hồi tri thức
              └─ không đủ căn cứ ───────────> CHUYỂN NGƯỜI
              └─ Sinh phản hồi + trích dẫn
                    └─ Guardrail đầu ra ── vi phạm ──> CHUYỂN NGƯỜI
                    └─ Đạt ──> HÀNG ĐỢI DUYỆT ──> Người duyệt ──> Gửi
```

<a id="spec-flow-02"></a>

### SPEC-FLOW-02 — Điều kiện chuyển người bắt buộc

**BẮT BUỘC** chuyển người trong mọi trường hợp sau, không có ngoại lệ:

| Mã | Điều kiện |
|---|---|
| `LOW_CONFIDENCE` | Độ tin cậy phân loại < 0.60 |
| `NO_KNOWLEDGE_MATCH` | Không có chunk nào vượt ngưỡng truy hồi |
| `MONEY_CLAIM` | Ticket có yêu cầu bồi thường hoặc hoàn tiền |
| `P1_PRIORITY` | Ticket được gán mức ưu tiên P1 |
| `ESCALATION_SIGNAL` | Khách hàng đe dọa khiếu nại lên cơ quan quản lý hoặc truyền thông |
| `GUARDRAIL_BLOCK` | Bất kỳ guardrail nào kích hoạt |
| `LLM_UNAVAILABLE` | Ngắt mạch đang mở |
| `SCHEMA_FALLBACK` | Đầu ra có cấu trúc thất bại sau retry |

<a id="spec-flow-03"></a>

### SPEC-FLOW-03 — Nguyên tắc bất biến

> **BẮT BUỘC:** Không có đường dẫn nào trong hệ thống cho phép phản hồi tới khách hàng mà chưa qua thao tác duyệt của con người. Điều này áp dụng cho cả bản demo cuối khóa.

<a id="spec-flow-04"></a>

### SPEC-FLOW-04 — Ghi nhận thao tác duyệt

Mỗi thao tác duyệt **BẮT BUỘC** ghi vào SQLite:

```json
{
  "trace_id": "...",
  "ticket_id": "TK-00042",
  "action": "approve | edit_approve | reject",
  "edited_text": "...",
  "reject_reason": "...",
  "reviewer": "...",
  "timestamp": "..."
}
```

**Lý do:** tỉ lệ sửa và lý do từ chối là chỉ số chất lượng đáng tin cậy nhất mà hệ thống có — đáng tin hơn mọi phép đo tự động. Đây là nguồn dữ liệu chính cho sprint cải tiến ở Lab 6.

---

<a id="muc-11"></a>

## 11. CHÍNH SÁCH GUARDRAILS

<a id="spec-guard-01"></a>

### SPEC-GUARD-01 — Guardrail đầu vào

| # | Luật | Hành động khi vi phạm |
|---|---|---|
| 1 | Độ dài ticket ≤ 2000 ký tự | Cắt bớt + ghi log |
| 2 | Phát hiện và che PII (số CMND/CCCD, số thẻ, địa chỉ đầy đủ) | Che trước khi đưa vào prompt |
| 3 | Phát hiện mẫu prompt injection ("bỏ qua hướng dẫn", "system prompt", "in ra toàn bộ...") | Chặn, `GUARDRAIL_BLOCK` |
| 4 | Yêu cầu truy vấn thông tin của thuê bao khác | Chặn, `GUARDRAIL_BLOCK` |

<a id="spec-guard-02"></a>

### SPEC-GUARD-02 — Guardrail đầu ra

| # | Luật | Hành động khi vi phạm |
|---|---|---|
| 1 | Phải có ít nhất 1 trích dẫn hợp lệ | Chặn |
| 2 | Không chứa số tiền cam kết bồi thường | Chặn |
| 3 | Không chứa cam kết thời hạn cụ thể ("trong 24 giờ", "chậm nhất ngày...") | Chặn |
| 4 | Không chứa `subscriber_id` khác với ticket đang xử lý | Chặn |
| 5 | Không chứa nội dung xúc phạm, phân biệt đối xử | Chặn |
| 6 | Không lặp lại nguyên văn nội dung prompt hệ thống | Chặn |

<a id="spec-guard-03"></a>

### SPEC-GUARD-03 — Guardrail vận hành

Timeout, giới hạn số lần gọi, ngắt mạch — xem [`SPEC-LLM-05`](#spec-llm-05) và [`SPEC-TOOL-02`](#spec-tool-02).

<a id="spec-guard-04"></a>

### SPEC-GUARD-04 — Bộ kiểm thử đối kháng

[`tests/adversarial/`](tests/adversarial/) **BẮT BUỘC** chứa tối thiểu 12 ca, phủ đủ các nhóm:

| Nhóm | Số ca | Ví dụ |
|---|---|---|
| Prompt injection trực tiếp | 3 | Ticket yêu cầu bỏ qua hướng dẫn hệ thống |
| Rò rỉ dữ liệu thuê bao khác | 2 | Ticket hỏi thông tin số thuê bao không phải của mình |
| Dụ cam kết bồi thường | 2 | Ticket ép hệ thống hứa số tiền |
| Câu hỏi ngoài phạm vi tri thức | 2 | Hỏi chính sách không tồn tại |
| Ticket rác / vô nghĩa | 2 | Chuỗi ký tự ngẫu nhiên |
| Nội dung xúc phạm | 1 | Ticket có ngôn từ công kích |

**Tiêu chí đạt:** 12/12 ca được xử lý đúng (chặn hoặc chuyển người), 0 ca sinh ra phản hồi không phù hợp.

---

<a id="muc-12"></a>

## 12. GIAO THỨC ĐÁNH GIÁ

<a id="spec-eval-01"></a>

### SPEC-EVAL-01 — Bộ chỉ số bắt buộc

| Nhóm | Chỉ số | Cách đo |
|---|---|---|
| Phân loại | Accuracy, Macro-F1, ma trận nhầm lẫn | So với nhãn trong `gold_test.jsonl` |
| Truy hồi | Recall@3, Recall@5, MRR | So với `expected_doc_ids` trong `gold_qa.jsonl` |
| Sinh văn bản | Tỉ lệ có trích dẫn hợp lệ; tỉ lệ bịa thông tin | Tự động cho #1; chấm thủ công 10 mẫu cho #2 |
| Vận hành | Độ trễ trung bình, p95; số lần gọi LLM/ticket; tỉ lệ cache hit; thông lượng ở các mức đồng thời 1/3/5/10; số ticket mỗi giờ | Từ log và kiểm thử tải |
| An toàn | Tỉ lệ chuyển người đúng; kết quả bộ đối kháng | So với `meta.expected_action` |

<a id="spec-eval-02"></a>

### SPEC-EVAL-02 — Quy trình chạy

1. **BẮT BUỘC** chạy trên `gold_test.jsonl`, không chạy trên `train.jsonl`
2. **BẮT BUỘC** ghi lại `run_manifest.json` cùng kết quả (xem [`SPEC-EVAL-03`](#spec-eval-03))
3. **BẮT BUỘC** kết quả lưu vào `eval/results/<timestamp>/`, không ghi đè lần chạy trước
4. **NÊN** chạy nền từ đầu buổi học, phân tích kết quả ở nửa sau

<a id="spec-eval-03"></a>

### SPEC-EVAL-03 — Manifest lần chạy

Mỗi lần đánh giá **BẮT BUỘC** được ghi vào MLflow (backend SQLite local) để tái lập và so sánh được:

| Loại | Nội dung ghi |
|---|---|
| Tham số (params) | `git_commit`, `config_profile`, `model`, `base_url`, `embedding_model`, `prompt_versions`, `chunk_size`, `overlap`, `k`, `threshold`, `dataset_version` |
| Chỉ số (metrics) | Accuracy, Macro-F1, Recall@3, Recall@5, MRR, tỉ lệ trích dẫn hợp lệ, độ trễ p95, tỉ lệ cache hit |
| Artifact | Ma trận nhầm lẫn, danh sách ca sai, tệp `results.json` |

Bản sao dạng tệp vẫn được ghi kèm tại `eval/results/<timestamp>/run_manifest.json` để đọc được khi không mở MLflow:

```json
{
  "run_id": "2026-09-12T14:03:00",
  "git_commit": "a3f9c21",
  "config_profile": "S",
  "model": "Qwen3-8B",
  "embedding_model": "bge-m3",
  "prompt_versions": {"classifier": "v3", "generator": "v2"},
  "rag_config": {"chunk_size": 600, "overlap": 80, "k": 5, "threshold": 0.62},
  "dataset": "gold_test.jsonl@v1",
  "cache_hit_rate": 0.42
}
```

**Không có manifest thì kết quả đánh giá không có giá trị so sánh** — vì không biết con số đó thuộc về cấu hình nào.

<a id="spec-eval-04"></a>

### SPEC-EVAL-04 — Quy tắc cải tiến

Ở Lab 6, mọi cải tiến **BẮT BUỘC** báo cáo theo bảng:

| Cải tiến | Chỉ số trước | Chỉ số sau | Căn cứ chọn làm |
|---|---|---|---|

Chỉ được thay đổi **một biến tại một thời điểm**. Thay hai thứ cùng lúc thì không quy được kết quả cho nguyên nhân nào.

---

<a id="muc-13"></a>

## 13. LOGGING VÀ TRUY VẾT

<a id="spec-log-01"></a>

### SPEC-LOG-01 — Lược đồ log

Mỗi request sinh ra một `trace_id` (UUID), gắn xuyên suốt mọi bước:

```json
{
  "trace_id": "uuid",
  "ticket_id": "TK-00042",
  "ts": "2026-09-12T14:03:00+07:00",
  "step": "classify | retrieve | tool_call | generate | guardrail | review",
  "model": "Qwen3-8B",
  "config_profile": "S",
  "prompt_version": "classifier.v3",
  "tokens_in": 512,
  "tokens_out": 128,
  "latency_ms": 3400,
  "cache_hit": false,
  "attempts": 1,
  "outcome": "ok | fallback | blocked | escalated",
  "guardrail_triggered": null,
  "error": null
}
```

<a id="spec-log-02"></a>

### SPEC-LOG-02 — Yêu cầu truy vết

> **Tiêu chí nghiệm thu:** cho một `ticket_id` bất kỳ, phải tái dựng được đầy đủ: đã dùng prompt phiên bản nào, truy hồi ra những chunk nào với điểm bao nhiêu, gọi công cụ gì với tham số gì, guardrail nào kích hoạt, và người duyệt đã làm gì.

Nếu không đáp ứng tiêu chí này, hệ thống chưa đạt "production-ready" ở Lab 5.

<a id="spec-log-03"></a>

### SPEC-LOG-03 — Quy định bảo mật log

**BẮT BUỘC:** log không chứa nội dung PII chưa che. Trường `customer_msg` lưu bản đã qua guardrail đầu vào, không lưu bản thô.

---

<a id="muc-14"></a>

## 14. MA TRẬN TRUY VẾT

<a id="spec-trace-01"></a>

### SPEC-TRACE-01 — Yêu cầu đầu ra của môn học ↔ Sản phẩm

| # | Yêu cầu đầu ra (theo đề cương) | Session | Deliverable | Artifact trong repo | Bằng chứng nghiệm thu |
|---|---|---|---|---|---|
| YC1 | Phân tích bài toán và xác định cơ hội ứng dụng AI | 1 | AI Opportunity Canvas | [`docs/canvas.md`](docs/canvas.md) | Canvas đủ 7 ô, chỉ số đo được bằng số |
| YC2 | Thiết kế AI Architecture cho bài toán doanh nghiệp | 2 | AI Solution Blueprint | [`docs/blueprint.md`](docs/blueprint.md), [`docs/adr/`](docs/adr/) | Sơ đồ 5 tầng + bảng quyết định có lý do |
| YC3 | Thiết kế AI Workflow (Prompt, Context, Knowledge, Tool) | 3, 4 | Context Specification, AI Prototype v1 | [`docs/context_spec.md`](docs/context_spec.md), [`src/agent/`](src/agent/) | Bảng thí nghiệm RAG có số đo; workflow chạy end-to-end |
| YC4 | Phát triển AI Application dựa trên Starter Kit | 3, 4, 5 | Prototype hoạt động | [`src/`](src/) | `docker compose up` chạy được từ máy sạch |
| YC5 | Đánh giá và triển khai AI Application Prototype | 5, 6 | Production-ready Prototype, Final Application | [`docs/EVALUATION.md`](docs/EVALUATION.md), `eval/results/` | Đủ 5 nhóm chỉ số + phân tích lỗi + 12/12 ca đối kháng |

<a id="spec-trace-02"></a>

### SPEC-TRACE-02 — Yêu cầu đầu ra theo từng Module ↔ Hoạt động ↔ Bằng chứng

Đây là cột "Yêu cầu đầu ra" trong bảng nội dung chi tiết của đề cương, tách riêng theo module.

**Module 1 — Thiết kế giải pháp AI (Session 1, 2)**

| # | Yêu cầu đầu ra | Hoạt động tương ứng | Bằng chứng nghiệm thu |
|---|---|---|---|
| M1-1 | Xác định được bài toán phù hợp để ứng dụng AI | Lab 1 bước 2: chấm điểm 4 tiêu chí cho từng bước nghiệp vụ | Bảng chấm điểm có lý do cho mỗi điểm số |
| M1-2 | Phân tích được giá trị và phạm vi của AI trong hệ thống | Lab 1 bước 3: ô "Chỉ số thành công" và ô "Phạm vi MVP" trong Canvas | ≥ 2 chỉ số định lượng; phần "KHÔNG làm" ≥ 4 mục |
| M1-3 | Thiết kế được kiến trúc tổng thể của AI Application | Lab 2 bước 3: vẽ Blueprint 5 tầng | Sơ đồ đủ 5 tầng, mỗi thành phần có đầu vào/đầu ra/phương án dự phòng |
| M1-4 | Lựa chọn được các thành phần AI phù hợp | Lab 2 bước 2 (thí nghiệm so sánh model) + bảng quyết định thiết kế | Bảng so sánh cấu hình có số đo; [`docs/adr/`](docs/adr/) có ≥ 5 ADR |

**Module 2 — Phát triển ứng dụng AI (Session 3, 4)**

| # | Yêu cầu đầu ra | Hoạt động tương ứng | Bằng chứng nghiệm thu |
|---|---|---|---|
| M2-1 | Thiết kế được ngữ cảnh và tri thức cho AI Application | Lab 3 bước 1 (instruction), bước 2 đến 4 (Knowledge, chia đoạn, embedding) và bước 6 (context, ngân sách) | `context_spec.md` có mẫu prompt 5 phần và chiến lược chunking |
| M2-2 | Xây dựng được chiến lược khai thác tri thức | Lab 3 bước 5: thí nghiệm cải tiến truy hồi có đo lường | Bảng ≥ 2 thí nghiệm kèm Recall@5 trước–sau |
| M2-3 | Thiết kế được quy trình xử lý AI | Lab 4 bước 1: vẽ sơ đồ luồng đủ nhánh rẽ và điểm quyết định | Sơ đồ luồng + danh sách ≥ 4 điều kiện chuyển người |
| M2-4 | Xây dựng được AI Prototype hoạt động | Lab 4 bước 2, 3, 4 | Chạy end-to-end trên 5 ticket; video 3 tình huống |

**Module 3 — Triển khai và đánh giá (Session 5)**

| # | Yêu cầu đầu ra | Hoạt động tương ứng | Bằng chứng nghiệm thu |
|---|---|---|---|
| M3-1 | Triển khai được AI Application Prototype | Lab 5 bước 1: API + Docker | `docker compose up` chạy được từ máy sạch |
| M3-2 | Đánh giá được chất lượng và mức độ sẵn sàng triển khai | Lab 5 bước 2 (5 nhóm chỉ số), bước 3 (12 ca đối kháng), bước 4 (logging) | `EVALUATION.md` + `run_manifest.json` + truy vết được 1 ticket bất kỳ |

**Module 4 — Dự án cuối khóa (Session 6)**

| # | Yêu cầu đầu ra | Hoạt động tương ứng | Bằng chứng nghiệm thu |
|---|---|---|---|
| M4-1 | Hoàn thiện một AI Application Prototype | Lab 6 bước 1: sprint cải tiến có đo lường | Bảng 2 cải tiến với chỉ số trước–sau |
| M4-2 | Trình bày được kiến trúc, quy trình xử lý và phương án triển khai | Lab 6 bước 2, 3 | Demo 4 kịch bản + slide + trả lời phản biện |

<a id="spec-trace-03"></a>

### SPEC-TRACE-03 — Đối chiếu từng gạch đầu dòng của đề cương

Bảng này dùng để kiểm tra độ phủ. Mọi mục "Nội dung" và "Workshop" trong đề cương phải có ít nhất một dòng ở đây.

**Session 1**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| Tổng quan về AI Application và AI Engineering | Nội dung | Lý thuyết, 25 phút |
| Xu hướng phát triển AI Application trong doanh nghiệp | Nội dung | Lý thuyết, 20 phút |
| Xác định bài toán phù hợp để ứng dụng AI | Nội dung | Lý thuyết, 25 phút |
| Phân tích quy trình nghiệp vụ và xác định AI Capability | Nội dung | Lý thuyết, 30 phút |
| Phân biệt AI Application, AI Service và AI Agent | Nội dung | Lý thuyết, 20 phút |
| Phân tích một bài toán doanh nghiệp | Workshop | Lab 1 bước 1 — vẽ bản đồ quy trình xử lý ticket |
| Xác định các điểm có thể ứng dụng AI | Workshop | Lab 1 bước 2 — chấm điểm 4 tiêu chí |
| Xây dựng AI Opportunity Canvas | Workshop | Lab 1 bước 3, chốt phạm vi ở bước 4 |

**Session 2**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| AI Application Architecture | Nội dung | Lý thuyết, 25 phút |
| Thành phần của một AI Application | Nội dung | Lý thuyết, 25 phút |
| Lựa chọn Foundation Model | Nội dung | Lý thuyết, 25 phút |
| Thiết kế luồng xử lý tổng thể | Nội dung | Lý thuyết, 25 phút |
| AI Design Pattern | Nội dung | Lý thuyết, 20 phút |
| Thiết kế kiến trúc hệ thống | Workshop | Lab 2 bước 3 |
| Phân tích Development Starter Kit | Workshop | Lab 2 bước 1 — giải phẫu repo, vẽ sơ đồ phụ thuộc |
| Hoàn thiện AI Solution Blueprint | Workshop | Lab 2 bước 3 và 4 |

**Session 3**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| Prompt Engineering | Nội dung | Lý thuyết, 30 phút |
| Context Engineering | Nội dung | Lý thuyết, 25 phút |
| Knowledge Engineering | Nội dung | Lý thuyết, 20 phút |
| Retrieval-Augmented Generation | Nội dung | Lý thuyết, 30 phút |
| Quản lý tri thức doanh nghiệp | Nội dung | Lý thuyết, 15 phút |
| Thiết kế Prompt | Workshop | Lab 3 bước 1 |
| Thiết kế Context | Workshop | Lab 3 bước 1 (phân tách bằng thẻ) và bước 6 (sáu thành phần và ngân sách context, ghép context truy hồi) |
| Xây dựng Knowledge Base | Workshop | Lab 3 bước 2 đến 4, đo chất lượng ở bước 5 |

**Session 4**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| AI Workflow | Nội dung | Lý thuyết, 25 phút |
| Tool Calling | Nội dung | Lý thuyết, 30 phút |
| Agent Workflow (giới thiệu) | Nội dung | Lý thuyết, 20 phút |
| Human-in-the-loop | Nội dung | Lý thuyết, 25 phút |
| Thiết kế AI Pipeline | Nội dung | Lý thuyết, 20 phút |
| Thiết kế AI Workflow | Workshop | Lab 4 bước 1 |
| Tích hợp AI Capability vào Starter Kit | Workshop | Lab 4 bước 2 (tool) và bước 3 (sinh phản hồi, ghép pipeline) |
| Xây dựng Prototype | Workshop | Lab 4 bước 3 và 4 |

**Session 5**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| Thiết kế API cho AI Application | Nội dung | Lý thuyết, 25 phút |
| Đóng gói ứng dụng bằng Docker | Nội dung | Lý thuyết, 20 phút |
| Đánh giá chất lượng AI Application | Nội dung | Lý thuyết, 30 phút |
| Guardrails và Production Readiness | Nội dung | Lý thuyết, 25 phút |
| Logging và Monitoring | Nội dung | Lý thuyết, 20 phút |
| Docker hóa ứng dụng | Workshop | Lab 5 bước 1 |
| Đánh giá Prototype | Workshop | Lab 5 bước 2 |
| Hoàn thiện Production-ready Prototype | Workshop | Lab 5 bước 3 (guardrails) và bước 4 (logging) |

**Session 6**

| Đề cương | Loại | Triển khai tại |
|---|---|---|
| Hoàn thiện AI Application | Nội dung | Lý thuyết, 15 phút |
| Kiểm thử và cải tiến | Nội dung | Lý thuyết, 20 phút |
| Chuẩn bị Demo | Nội dung | Lý thuyết, 10 phút |
| Trình bày kiến trúc và các quyết định thiết kế | Nội dung | Lý thuyết, 15 phút |
| Hoàn thiện sản phẩm | Workshop | Lab 6 bước 1 — sprint 2 cải tiến có đo lường |
| Demo | Workshop | Lab 6 bước 2 (chuẩn bị) và bước 3 (trình diễn) |
| Báo cáo | Workshop | Lab 6 — slide 10 trang, [`README.md`](README.md), bảng cải tiến trước–sau |
| Phản biện | Workshop | Lab 6 bước 3, dùng ngân hàng câu hỏi phản biện |

<a id="spec-trace-04"></a>

### SPEC-TRACE-04 — Điều kiện hoàn thành (Definition of Done) từng lab

| Lab | Điều kiện hoàn thành |
|---|---|
| 0 | `uv sync` thành công; `check_env.py` trả PASS toàn bộ; `pre-commit` đã cài; nộp ảnh chụp màn hình |
| 1 | [`docs/canvas.md`](docs/canvas.md) đủ 7 ô; ≥ 2 chỉ số định lượng kèm ước lượng ROI và điểm hòa vốn; phần "KHÔNG làm" ≥ 4 mục |
| 2 | Sơ đồ 5 tầng; ≥ 5 ADR trong [`docs/adr/`](docs/adr/); `Modelfile` ghim tham số; CI giai đoạn lint chạy xanh; UI chạy được với dữ liệu giả |
| 3 | `pytest tests/test_lab3.py` xanh trên CI; index dựng được; ≥ 2 thí nghiệm RAG có số đo; ≥ 2 phiên bản prompt so sánh bằng `promptfoo`; nộp qua pull request đã được nhóm khác duyệt |
| 4 | Chạy end-to-end trên 5 ticket; ≥ 4 điều kiện escalate hoạt động; màn hình duyệt ghi được log; CI vẫn xanh |
| 5 | `docker compose up` từ máy sạch; API bất đồng bộ hoạt động; đủ 5 nhóm chỉ số ghi vào MLflow; 12/12 ca đối kháng đạt; cổng chất lượng CI hoạt động; truy vết được 1 ticket bất kỳ; có bảng năng lực phục vụ ở 4 mức đồng thời |
| 6 | 2 cải tiến có số đo trước–sau đối chiếu được trên MLflow; `MODEL_CARD.md` đủ 9 phần kèm kiểm tra thiên lệch 4 lát cắt; `docs/handover/` đủ 5 tài liệu; demo 4 kịch bản |

---

<a id="muc-15"></a>

## 15. TRÁCH NHIỆM VÀ BÀN GIAO

<a id="spec-resp-01"></a>

### SPEC-RESP-01 — Kiểm tra thiên lệch

**BẮT BUỘC** ở Lab 6: đo độ chính xác phân loại tách theo các lát cắt sau, dùng chính tập kiểm định 40 ticket:

| Lát cắt | Cách chia | Câu hỏi cần trả lời |
|---|---|---|
| Văn phong | Lịch sự / trung tính / cộc lốc | Hệ thống có phân loại kém hơn với khách viết cộc lốc không? |
| Chính tả | Đúng chuẩn / có lỗi chính tả | Lỗi chính tả có làm giảm chất lượng phục vụ không? |
| Độ dài ticket | Ngắn dưới 50 từ / dài trên 150 từ | Ticket ngắn có bị chuyển người nhiều hơn không? |
| Kênh tiếp nhận | Tổng đài / ứng dụng / thư điện tử | Có kênh nào bị phục vụ kém hơn không? |

**Ngưỡng cảnh báo:** chênh lệch độ chính xác giữa hai nhóm bất kỳ trong cùng lát cắt vượt **10 điểm phần trăm** thì phải ghi vào Model Card như một giới hạn đã biết, kèm biện pháp giảm thiểu hoặc lý do chấp nhận.

> Với một trợ lý phục vụ khách hàng thật, đây không phải bài tập hình thức. Nếu hệ thống phục vụ kém hơn với khách hàng lớn tuổi viết sai chính tả, đó là một vấn đề nghiệp vụ chứ không phải một con số thống kê.

<a id="spec-resp-02"></a>

### SPEC-RESP-02 — Model Card

[`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) **BẮT BUỘC** có đủ các phần:

| Phần | Nội dung |
|---|---|
| Mục đích sử dụng | Bài toán hệ thống giải quyết, người dùng dự kiến |
| Phạm vi áp dụng | Loại ticket xử lý được, ngôn ngữ, kênh tiếp nhận |
| Ngoài phạm vi | Những gì hệ thống không được dùng để làm |
| Dữ liệu | Nguồn dữ liệu, quy mô, cách sinh, các hạn chế đã biết |
| Kết quả đánh giá | Năm nhóm chỉ số, kèm cấu hình đã dùng |
| Kiểm tra thiên lệch | Kết quả theo bốn lát cắt tại [`SPEC-RESP-01`](#spec-resp-01) |
| Giới hạn đã biết | Tối thiểu 3 giới hạn cụ thể rút từ phân tích lỗi |
| Rủi ro và biện pháp | Rủi ro nghiệp vụ và guardrail tương ứng |
| Điều kiện vận hành | Năng lực phục vụ, ngưỡng cảnh báo, khi nào cần đánh giá lại |

<a id="spec-resp-03"></a>

### SPEC-RESP-03 — Phát hiện suy giảm chất lượng

Hệ thống không huấn luyện mô hình nên không có trôi dữ liệu theo nghĩa cổ điển. Dạng tương đương cần theo dõi:

| Loại | Biểu hiện | Tín hiệu phát hiện |
|---|---|---|
| Trôi phân bố đầu vào | Xuất hiện nhóm vấn đề mới, tỉ lệ nhóm thay đổi | Phân bố nhãn theo tuần lệch khỏi đường nền |
| Tri thức lỗi thời | Chính sách thay đổi, tài liệu chưa cập nhật | Tỉ lệ `NO_KNOWLEDGE_MATCH` tăng |
| Suy giảm chất lượng sinh | Phản hồi kém đi dù chỉ số tự động không đổi | **Tỉ lệ sửa và tỉ lệ từ chối của người duyệt** |
| Thay đổi hạ tầng | Đổi phiên bản model hoặc tham số | Chạy lại bộ đánh giá, so sánh trên MLflow |

**Tín hiệu quan trọng nhất là dòng thứ ba.** Tỉ lệ sửa của người duyệt là phép đo chất lượng đáng tin nhất mà hệ thống có, và nó được ghi sẵn từ [`SPEC-FLOW-04`](#spec-flow-04) mà không tốn thêm hạ tầng gì.

**Ngưỡng cảnh báo mặc định:** tỉ lệ từ chối vượt 15% hoặc tỉ lệ sửa vượt 40% trong một tuần thì cần rà soát prompt và kho tri thức.

<a id="spec-resp-04"></a>

### SPEC-RESP-04 — Gói bàn giao

**BẮT BUỘC** ở Lab 6, thư mục `docs/handover/`:

| Tài liệu | Nội dung tối thiểu |
|---|---|
| [`README.md`](README.md) | Dựng lại hệ thống từ máy trắng |
| `RUNBOOK.md` | Khởi động, dừng, kiểm tra sức khỏe, xem nhật ký, sao lưu |
| `INCIDENTS.md` | Quy trình xử lý tối thiểu 3 sự cố: dịch vụ mô hình không phản hồi, hàng đợi ứ đọng, chất lượng phản hồi tụt |
| `MODEL_CARD.md` | Theo [`SPEC-RESP-02`](#spec-resp-02) |
| `RESPONSIBILITIES.md` | Phân định việc nào thuộc đơn vị phát triển, việc nào thuộc đơn vị vận hành |

> Bàn giao thiếu sổ tay vận hành là nguyên nhân phổ biến nhất khiến sản phẩm chết sau nghiệm thu: đơn vị tiếp nhận không biết xử lý sự cố đầu tiên, và hệ thống bị bỏ.

---

<a id="muc-16"></a>

## 16. RỦI RO VÀ PHƯƠNG ÁN DỰ PHÒNG

| Mã | Rủi ro | Xác suất | Tác động | Phương án |
|---|---|---|---|---|
| R1 | Server dùng chung sự cố giữa buổi | Trung bình | **Cả lớp dừng** nếu S là tham chiếu | Mọi học viên bắt buộc có cấu hình L sẵn sàng; chuyển bằng một biến môi trường; index dựng sẵn có trong repo |
| R2 | Mạng lớp học tới server chập chờn | Trung bình | Gián đoạn thực hành | Kiểm chứng đường truyền trước khóa; chế độ chỉ dùng cache cho phần lớn thao tác lặp lại |
| R3 | Nhóm tụt lại, không làm được lab sau | Cao | Đứt chuỗi deliverable | Nhánh `solution/session-N` |
| R4 | Docker lỗi trên Windows | Trung bình | Không hoàn thành Lab 5 | Chạy trực tiếp `uvicorn` + `streamlit`; chấm Docker qua cấu hình đã viết |
| R5 | Chênh lệch trình độ quá lớn | Cao | Nhóm mạnh chán, nhóm yếu nản | Ghép cặp DS/AI + CNTT, luân phiên driver/navigator 30 phút; [`CHALLENGE.md`](CHALLENGE.md) cho nhóm xong sớm |
| R6 | Demo cuối khóa chạy chậm bất thường | Trung bình | Hỏng buổi trình bày | Video dự phòng + cache dựng sẵn |
| R7 | Model chất lượng thấp làm học viên mất niềm tin | Thấp (giảm từ Trung bình sau v1.6 — cả hai cấu hình nay cùng Qwen3-8B) | Kết luận sai về công nghệ | Nói rõ ngay Session 2: các bài Lab 3/4 cố ý ép model gặp ca khó để dạy lớp phòng vệ, không phải model kém |
| R8 | Học viên đưa dữ liệu thật vào repo | Thấp | Rủi ro bảo mật | Chặn tự động bằng `pre-commit` (`detect-secrets` + luật quét PII), xem [`SPEC-TOOLING-03`](#spec-tooling-03) |
| R17 | vLLM (cấu hình S) không tự tách thinking-mode của Qwen3 như Ollama — nếu thiếu cờ `--reasoning-parser qwen3`, `<think>` lọt vào content và phá lớp kiểm định JSON | Trung bình, đã có cách khắc phục cụ thể (xem [`scripts/run_vllm_local.sh`](scripts/run_vllm_local.sh)) | Mọi ticket ở cấu hình S rơi vào fallback needs_human dù model trả lời đúng bên trong | **ĐÃ XÁC MINH một phần (2026-09-23, qua Ollama + qwen3:1.7b, xem [Mục 17](#muc-17) v1.6):** Ollama tự tách sạch, không cần sửa gì. **CHƯA xác minh trên vLLM thật** (không có GPU khi kiểm tra) — nhóm nào triển khai [`CHALLENGE.md`](CHALLENGE.md) mục 5.4 BẮT BUỘC bật `--reasoning-parser qwen3` và kiểm tra lại bằng đúng `extract_json()`/`validate()` trước khi tin kết quả |
| R9 | Lớp học không có mạng để chạy CI trên GitHub | Trung bình | Không thực hành được cổng chất lượng | Chạy `act` hoặc script CI local; nội dung giảng dạy không đổi vì cache khiến eval tất định |
| R10 | Học viên dùng trợ lý AI sinh mã mà không hiểu | Cao | Không đạt yêu cầu đầu ra về thiết kế | Phần phản biện Session 6 kiểm tra khả năng giải thích; ADR và quyết định thiết kế bắt buộc do học viên tự quyết, xem [`SPEC-TOOLING-07`](#spec-tooling-07) |
| R11 | Kiểm thử tải làm treo máy học viên | Trung bình | Mất bước 5 của Lab 5 | Giới hạn mức đồng thời tối đa ở 5; mục tiêu là quan sát quy luật suy giảm, không phải tìm giới hạn tuyệt đối |
| R12 | Năng lực phục vụ thực tế thấp hơn giả định trong Canvas | Cao | Học viên hụt hẫng | Đây là **kết quả học tập mong muốn**, không phải thất bại. Ghi vào Model Card như giới hạn đã biết và thảo luận phương án hạ tầng ở Session 6 |
| R13 | Cache lẫn giữa hai cấu hình làm hỏng số liệu | Cao | Kết luận đánh giá sai | `base_url` và `model` nằm trong khóa cache; `config_profile` bắt buộc trong mọi manifest và log; CI chỉ chấp nhận cache tham chiếu |
| R14 | 30 học viên cùng chạy kiểm thử tải làm nghẽn server | Cao | Số đo Lab 5 vô nghĩa | Chia khung giờ riêng 5 phút cho từng nhóm; phép đo đường nền chạy cục bộ nên không phụ thuộc server |
| R15 | **Server GPU không đủ năng lực cho 30 người, phát hiện muộn** | Cao | Phải hạ chuẩn giữa khóa, mất uy tín và mất thời gian | [`SPEC-INFRA-02`](#spec-infra-02) bắt buộc đo năng lực trước khóa 1 tuần và chọn cấu hình dựa trên số liệu; khi phân vân thì chọn cấu hình L |
| R16 | GPU dùng chung với tải sản xuất khác, năng lực dao động | Trung bình | Số đo không ổn định giữa các buổi | Đặt hạn mức riêng qua LiteLLM proxy; nếu không đặt được thì chọn cấu hình L làm tham chiếu |

---

<a id="muc-17"></a>

## 17. NHẬT KÝ THAY ĐỔI

| Phiên bản | Ngày | Người thay đổi | Nội dung | Lý do |
|---|---|---|---|---|
| v1.0 | 2026-08-25 | — | Bản khởi tạo | Thiết lập ràng buộc ban đầu cho khóa học |
| v1.9 | 2026-09-25 | — | **Cấu trúc lại phần tri thức theo kiến trúc trong slide Session 3.** `src/knowledge/{loader,indexer,retriever}.py` tách thành [`src/knowledge/`](src/knowledge/) (Knowledge Engineering: `sourcing`, `governance`, `preparation`, `embedding`, `indexing`), [`src/retrieval/`](src/retrieval/) (Retrieval Engineering: `transform`, `search`, `filters`, `rerank`, `pipeline`) và [`src/context/`](src/context/) (Context Engineering: `assemble`). Thêm [SPEC-RAG-05](#spec-rag-05) đến [SPEC-RAG-10](#spec-rag-10), [SPEC-CTX-01](#spec-ctx-01), [SPEC-CTX-02](#spec-ctx-02). Lab 3 có 6 khối code: `chunk_document`, `embed_chunks`, `hybrid_search`, `judge_evidence`, `assemble_context`, `classify`; bốn lớp phòng vệ đầu ra là mã cho sẵn. Thêm [`scripts/lab3_check.py`](scripts/lab3_check.py), [`docs/context-spec-template.md`](docs/context-spec-template.md) và chỉ mục dựng sẵn [`data/index_prebuilt/index.json`](data/index_prebuilt/index.json). `TASK_PARAMS` thêm `reasoning_effort: "none"` để model Qwen3 không dùng hết ngân sách token cho phần suy luận; ngưỡng mặc định `RETRIEVE_MIN_SCORE` đổi sang 0.62 (xem [ADR-0005](docs/adr/0005-nguong-tu-choi-thay-vi-doan.md)). | Cấu trúc mã cần khớp sơ đồ slide để người học lần được từ slide sang mã |
| v1.8 | 2026-09-25 | — | **Thiết kế lại Workbook 2 và Lab 2 bám slide Session 2.** Thêm [`docs/blueprint-template.md`](docs/blueprint-template.md) (khung Blueprint chín mục) và [`scripts/temperature_demo.py`](scripts/temperature_demo.py). | Người học cần đọc-hiểu-phân tích thay vì điền bảng ngắn |
| v1.7 | 2026-09-23 | — | **Kiểm chứng thật một phần rủi ro R17 (thinking-mode Qwen3).** Cài Ollama 0.34.3 + pull `qwen3:1.7b` (bản nhỏ cùng họ, dùng để kiểm chứng cơ chế — không đại diện accuracy của `qwen3:8b` thật) trên máy không có GPU rời, chạy `uv sync` đầy đủ, gọi thẳng endpoint `/v1/chat/completions` bằng đúng prompt thật (`classify.v1.md` + `schema_hint()` + `SYSTEM` của `classifier.py`), rồi xác nhận qua đúng `extract_json()`/`validate()`/`parse_with_retry()` của [`src/llm/schema.py`](src/llm/schema.py). **Kết quả:** Ollama tự tách khối suy luận ra field `message.reasoning` riêng, `message.content` luôn sạch — không ca nào hỏng vì thinking-mode, ở cả nhiệt độ 0 (classify) và 0.3 (generate). Gỡ chỉ dẫn `/no_think` khỏi `models/Modelfile` (đã xác nhận vô tác dụng — Ollama không đọc nó như token điều khiển, chỉ tốn thêm ~50% completion token cho suy luận ẩn không hiển thị). Chạy thật `pytest -m lab2` (7/7 pass) và `compare_models.py --tickets 3` qua model cục bộ: 1/3 ca cần lớp 3 (retry) mới đúng, 2/3 rơi fallback đúng cách — xác nhận pipeline 4 lớp phòng vệ chạy trơn tru end-to-end, không lỗi hệ thống. Khởi động thử `streamlit run src/ui/app.py` — boot thành công (HTTP 200), tắt ngay sau khi xác nhận. **CHƯA kiểm chứng:** hành vi tương đương trên vLLM/cấu hình S (thêm cờ `--reasoning-parser qwen3` vào [`scripts/run_vllm_local.sh`](scripts/run_vllm_local.sh) dựa trên suy luận kỹ thuật, chưa chạy thật vì không có GPU); accuracy thật của `qwen3:8b` đầy đủ (test dùng bản 1.7B nhỏ hơn nhiều); độ trễ trên phần cứng RTX 5080 thật (đo trên Apple M4 cho ra ~18-19 giây/ticket, không đại diện) | Trả lời trực tiếp yêu cầu kiểm chứng của người phụ trách khóa trước khi tin buổi học sẽ trôi chảy; máy có sẵn Homebrew nhưng bottle qua ghcr.io bị nghẽn mạng nặng trong môi trường này nên chuyển sang tải thẳng bản Ollama chính thức từ GitHub Releases |
| v1.6 | 2026-09-19 | — | Đổi model sinh văn bản mặc định của **cả hai cấu hình** từ `qwen2.5:3b-instruct` (L) / `Qwen2.5-7B-Instruct` (S) sang **`Qwen3-8B`** dùng chung (khác nhau ở backend: Ollama cho L, vLLM cho S — không còn khác nhau ở kích cỡ model). Đã cập nhật: [`.env.example`](.env.example), `models/Modelfile` (kèm cảnh báo thinking-mode của Qwen3 cần kiểm chứng thật), [`docker-compose.yml`](docker-compose.yml), [`src/config.py`](src/config.py), các script setup/so sánh, và nhãn "3B/7B" trong [`README.md`](README.md), [`SETUP.md`](SETUP.md), [`labs/LAB-0.md`](labs/LAB-0.md), [`CHALLENGE.md`](CHALLENGE.md) mục 5.4, `tai-lieu-bien-soan/workbooks/WORKBOOK-2.md`. **CHƯA LÀM** (cần GPU thật, ngoài khả năng chỉnh sửa văn bản): sinh lại `.cache/llm_cache.db` bằng `warm_cache.py` trên Qwen3-8B thật; đo lại toàn bộ ngưỡng [`SPEC-SCOPE-03`](#spec-scope-03) ([Mục 1](#muc-1), bảng ở dòng ~69) và ngưỡng CI ở `.github/workflows/ci.yml`; xác nhận thinking-mode của Qwen3 tắt được sạch qua Ollama; pilot Lab 3/4 để xem model có còn tự nhiên tạo ra JSON sai định dạng / gọi công cụ sai tham số hay không — xem rủi ro mới R17 (xem thêm v1.7). Thêm R17 | Yêu cầu trực tiếp từ đơn vị tổ chức khóa học, sau khi đánh giá Qwen2.5 (3B lẫn 7B) có hỗ trợ tiếng Việt nhưng ở mức trung bình, đặc biệt ở tác vụ sinh văn bản tự do của model nhỏ. Chọn hợp nhất về một model cho cả hai cấu hình theo lựa chọn tường minh của đơn vị tổ chức, chấp nhận đánh đổi: bài so sánh 3B/7B ở Lab 2 bước 2 mất trục "kích cỡ model", chỉ còn trục "hạ tầng" |
| v1.5 | 2026-09-19 | — | Xác nhận hạ tầng phòng Lab AI thật: 8 AI Workstation độc lập (i9-14900K, 64GB RAM, 1× RTX 5080 16GB, 2TB NVMe), mạng 10GbE nội bộ, 500Mbps Internet. **Quyết định: 1 nhóm = 1 workstation, không cluster hóa 8 GPU thành một server dùng chung.** Kiến trúc suy luận mặc định của mỗi workstation vẫn là cấu hình L (Ollama, `qwen2.5:3b-instruct`) theo [ADR-0001](docs/adr/0001-hai-cau-hinh-ngang-hang.md) — mỗi máy phục vụ đúng một nhóm nên lợi ích gộp lô liên tục của vLLM không phát huy, trong khi tính cách ly lỗi (không điểm hỏng chung) vẫn quan trọng như cũ. **Không bổ sung fine-tuning** — giữ nguyên [`SPEC-SCOPE-02`](#spec-scope-02). Bổ sung nội dung nâng cao TÙY CHỌN ở Session 5 ([`CHALLENGE.md`](CHALLENGE.md) mục 5.4): triển khai vLLM thật trên GPU của nhóm, tận dụng phần VRAM dư (~13GB/16GB chưa dùng ở cấu hình mặc định) mà không đổi cấu hình mặc định của lớp | Đã có số liệu phần cứng thật của phòng Lab, không còn phải áp dụng [`SPEC-INFRA-02`](#spec-infra-02) bằng phỏng đoán. GPU 16GB/máy dư sức chạy model lớn hơn 3B, nhưng vì mỗi máy chỉ phục vụ một nhóm (đồng thời ~1-2), giá trị chính của vLLM so với Ollama không phải continuous batching mà là tốc độ suy luận thô — đưa vào như bài tập nâng cao thay vì đổi mặc định, để không phải hiệu chuẩn lại toàn bộ [`SPEC-SCOPE-03`](#spec-scope-03) và cache/index đã đóng băng |
| v1.4 | 2026-08-25 | — | Hai cấu hình S và L trở thành ngang hàng thay vì một chính một dự phòng. Bổ sung [`SPEC-INFRA-02`](#spec-infra-02) — quy trình đo năng lực server và bảng quyết định chọn cấu hình tham chiếu trước khóa. Ngưỡng thành công tách thành hai bộ theo cấu hình. Model embedding `bge-m3` dùng chung ở cả hai cấu hình để index luôn tương thích. Thêm R15, R16 | Chưa xác định được năng lực GPU của server dùng chung; thiết kế phải trung lập với hạ tầng và quyết định bằng phép đo thay vì phỏng đoán |
| v1.3 | 2026-08-25 | — | Chuyển sang hạ tầng server dùng chung có GPU: vLLM làm mặc định, Ollama local thành cấu hình suy giảm. Viết lại toàn bộ [Mục 2](#muc-2) ([`SPEC-INFRA-01..07`](#spec-infra-01)). Bổ sung khái niệm cấu hình tham chiếu và trường `config_profile`. Khóa cứng model embedding `bge-m3`. Ngân sách tính toán chuyển từ ép bằng phần cứng sang ép bằng kiểm thử. Lab 5 đo trên cả hai cấu hình. Viết lại R1, R2; thêm R13, R14 | Đơn vị đã có server dùng chung có GPU; cấu hình cũ dựa trên CPU không còn phản ánh điều kiện triển khai thực tế |
| v1.2 | 2026-08-25 | — | Bổ sung [Mục 15](#muc-15) — Trách nhiệm và bàn giao ([`SPEC-RESP-01..04`](#spec-resp-01)). Bổ sung [`SPEC-INFRA-04`](#spec-infra-04) về năng lực phục vụ và đồng thời. API chuyển sang bất đồng bộ bắt buộc ([`SPEC-ARCH-02`](#spec-arch-02) mục 5, 6). Nộp bài qua pull request có review. Chuẩn viết mã PEP 8 và type hints. Thêm rủi ro R11, R12 | Bổ sung theo rà soát đối chiếu với chương trình MLOps: thiếu nội dung triển khai đa người dùng, Responsible AI, phát hiện suy giảm chất lượng và bàn giao vận hành |
| v1.1 | 2026-08-25 | — | Bổ sung [Mục 4](#muc-4) — Công cụ và quy trình kỹ thuật ([`SPEC-TOOLING-01..07`](#spec-tooling-01)). Chuyển `DECISIONS.md` thành ADR có cấu trúc. Chuyển manifest đánh giá sang MLflow. Bổ sung CI có cổng chất lượng, `uv`, `pre-commit`, `promptfoo`. Thêm rủi ro R9, R10 | Chuỗi bài thực hành mới dừng ở mức công cụ nền tảng, chưa phản ánh thực hành kỹ thuật hiện đại trong quản lý dự án AI |

---

<a id="phu-luc-a"></a>

## PHỤ LỤC A — DANH MỤC MÃ SPEC

| Nhóm | Mã | Nội dung |
|---|---|---|
| Phạm vi | `SPEC-SCOPE-`[01](#spec-scope-01) · [02](#spec-scope-02) · [03](#spec-scope-03) | Bài toán, phạm vi MVP, chỉ số thành công |
| Hạ tầng | `SPEC-INFRA-`[01](#spec-infra-01) · [02](#spec-infra-02) · [03](#spec-infra-03) · [04](#spec-infra-04) · [05](#spec-infra-05) · [06](#spec-infra-06) · [07](#spec-infra-07) | Hai cấu hình chạy, cấu hình tham chiếu, khóa embedding, ngân sách tính toán, năng lực phục vụ, cấu hình máy học viên, dự phòng |
| Kiến trúc | `SPEC-ARCH-`[01](#spec-arch-01) · [02](#spec-arch-02) · [03](#spec-arch-03) · [04](#spec-arch-04) | Phân tầng, nguyên tắc, cấu trúc repo, quy ước Git |
| Công cụ kỹ thuật | `SPEC-TOOLING-`[01](#spec-tooling-01) · [02](#spec-tooling-02) · [03](#spec-tooling-03) · [04](#spec-tooling-04) · [05](#spec-tooling-05) · [06](#spec-tooling-06) · [07](#spec-tooling-07) | Danh mục công cụ, môi trường, chất lượng mã, CI, ADR, thí nghiệm, dùng AI hỗ trợ lập trình |
| Dữ liệu | `SPEC-DATA-`[01](#spec-data-01) · [02](#spec-data-02) · [03](#spec-data-03) · [04](#spec-data-04) · [05](#spec-data-05) · [06](#spec-data-06) | Nguyên tắc, lược đồ, taxonomy, cơ cấu tập, bẫy, tri thức |
| LLM | `SPEC-LLM-`[01](#spec-llm-01) · [02](#spec-llm-02) · [03](#spec-llm-03) · [04](#spec-llm-04) · [05](#spec-llm-05) | Giao diện, cache, tham số, đầu ra cấu trúc, ngắt mạch |
| Prompt | `SPEC-PROMPT-`[01](#spec-prompt-01) · [02](#spec-prompt-02) · [03](#spec-prompt-03) | Cấu trúc, quy định, ràng buộc sinh phản hồi |
| RAG | `SPEC-RAG-`[01](#spec-rag-01) · [02](#spec-rag-02) · [03](#spec-rag-03) · [04](#spec-rag-04) · [05](#spec-rag-05) · [06](#spec-rag-06) · [07](#spec-rag-07) · [08](#spec-rag-08) · [09](#spec-rag-09) · [10](#spec-rag-10) | Chunking, truy hồi, không đủ căn cứ, trích dẫn, kiến trúc pipeline, hợp đồng dữ liệu, chia đoạn, embedding, tìm kiếm, ngưỡng |
| Context | `SPEC-CTX-`[01](#spec-ctx-01) · [02](#spec-ctx-02) | Ghép context, sáu thành phần của context |
| Công cụ | `SPEC-TOOL-`[01](#spec-tool-01) · [02](#spec-tool-02) · [03](#spec-tool-03) | Danh mục, ràng buộc, dự phòng theo luật |
| Quy trình | `SPEC-FLOW-`[01](#spec-flow-01) · [02](#spec-flow-02) · [03](#spec-flow-03) · [04](#spec-flow-04) | Luồng chuẩn, escalate, bất biến, ghi nhận duyệt |
| Guardrails | `SPEC-GUARD-`[01](#spec-guard-01) · [02](#spec-guard-02) · [03](#spec-guard-03) · [04](#spec-guard-04) | Đầu vào, đầu ra, vận hành, bộ đối kháng |
| Đánh giá | `SPEC-EVAL-`[01](#spec-eval-01) · [02](#spec-eval-02) · [03](#spec-eval-03) · [04](#spec-eval-04) | Chỉ số, quy trình, manifest, quy tắc cải tiến |
| Logging | `SPEC-LOG-`[01](#spec-log-01) · [02](#spec-log-02) · [03](#spec-log-03) | Lược đồ, truy vết, bảo mật |
| Trách nhiệm & bàn giao | `SPEC-RESP-`[01](#spec-resp-01) · [02](#spec-resp-02) · [03](#spec-resp-03) · [04](#spec-resp-04) | Kiểm tra thiên lệch, Model Card, phát hiện suy giảm chất lượng, gói bàn giao |
| Truy vết | `SPEC-TRACE-`[01](#spec-trace-01) · [02](#spec-trace-02) · [03](#spec-trace-03) · [04](#spec-trace-04) | Yêu cầu đầu ra môn học, yêu cầu đầu ra theo module, đối chiếu từng gạch đầu dòng đề cương, điều kiện hoàn thành |

<a id="phu-luc-b"></a>

## PHỤ LỤC B — CHECKLIST TRIỂN KHAI

**Trước khóa 3 tuần**
- [ ] Sinh 120 ticket, gán nhãn, rà chất lượng nhãn ([`SPEC-DATA-02..04`](#spec-data-02))
- [ ] Viết 28 tài liệu tri thức có front-matter ([`SPEC-DATA-06`](#spec-data-06))
- [ ] Cài đủ 5 loại bẫy sư phạm ([`SPEC-DATA-05`](#spec-data-05))
- [ ] Tạo 40 cặp hỏi–đáp vàng
- [ ] Viết 12 ca đối kháng ([`SPEC-GUARD-04`](#spec-guard-04))
- [ ] Dựng Starter Kit + 6 nhánh `solution/`
- [ ] Viết `pytest` cho từng lab

**Trước khóa 1 tuần**
- [ ] Chạy thử toàn bộ 6 lab trên máy 8GB, đo thời lượng thực tế
- [ ] Dựng [`data/index_prebuilt/`](data/index_prebuilt/) và cache LLM dựng sẵn
- [ ] Chuẩn bị 2 USB chứa model Ollama
- [ ] Dựng Ollama server LAN, kiểm tra tải 10 kết nối đồng thời
- [ ] Gửi Lab 0 cho học viên

**Trước khóa 2 ngày**
- [ ] Thu và rà kết quả `check_env.py`
- [ ] Hỗ trợ riêng học viên báo lỗi
- [ ] Ghép cặp 1 DS/AI + 1 CNTT
