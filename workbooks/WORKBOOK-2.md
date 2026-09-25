# WORKBOOK 2 — Thiết kế kiến trúc ứng dụng AI

**Ngày 1, buổi chiều · Workshop 2: From Architecture to Development Starter Kit · 120 phút thực hành · Deliverable: `docs/blueprint.md` + 5 ADR**

| | |
|---|---|
| Nhóm | `______________` |
| Nhánh | `team/______________` |
| Cấu hình lớp | S / L |

> Buổi sáng chốt **AI nên làm gì** (Canvas). Buổi chiều này chốt **hệ thống được ghép từ những mảnh nào, ai quyết định cái gì, và mảnh nào hỏng thì xử lý ra sao** (Blueprint). Workbook đi đúng theo sáu mục tiêu học tập ở slide 2 của Session 2: **Phân rã → Xác định ranh giới → Chọn model → Thiết kế luồng end-to-end → Áp dụng pattern → Chuyển thành Blueprint.** Mỗi bước ghi số slide để đối chiếu. Không viết code mới — bạn đọc code đã có sẵn trong Starter Kit để hiểu nó vận hành thế nào, rồi ghi lại thành các quyết định thiết kế.

---

## Đọc slide bằng case của khóa

Slide dùng case **CRM AI Assistant** (Sales Manager, khách hàng ABC, tạo follow-up task). Khóa này xây **trợ lý xử lý ticket CSKH viễn thông**. Cấu trúc kiến trúc giống hệt nhau — chỉ đổi tên. Khi slide nói một thứ, hãy tự dịch sang cột bên phải:

| Trong slide (CRM) | Trong khóa này (CSKH) |
|---|---|
| Sales Manager | Giao dịch viên tuyến một |
| Câu hỏi "Customer ABC có vấn đề gì?" | Một ticket của khách hàng |
| Tạo follow-up task | Soạn dự thảo phản hồi chờ người duyệt |
| CRM System / Customer Data | Dữ liệu thuê bao giả lập + `store.py` |
| Chính sách bán hàng, playbook | 28 tài liệu chính sách trong `data/knowledge/` |
| Human Approval | Màn hình duyệt: duyệt / sửa / từ chối |

---

## Trước khi bắt đầu (3 phút)

- [ ] `scripts/checkpoint.py 1` đã PASS
- [ ] Đã nắm phạm vi MVP **thống nhất của lớp** (không phải bản riêng của nhóm)
- [ ] Có sẵn slide Session 2 để mở lại theo số slide ghi trong từng bước

---

## Bước 1 — Phân rã: các thành phần của một ứng dụng AI · 20 phút

**Mục tiêu học tập 1 · Slide 9–12, 18–20, 24–26 · `___:___` → `___:___`**

Slide 10 chia một ứng dụng AI thành **năm tầng**: Experience, Orchestration, Intelligence, Context & Knowledge, Tools & Enterprise Systems — cộng hai thành phần xuyên suốt (Security & Guardrails, AI Platform & Operations). Bước này tìm xem mỗi thành phần đó nằm ở đâu trong repo.

### 1a — Luồng dữ liệu khi gửi một ticket

**Cách nghĩ:** đừng đọc toàn bộ code — lần theo đúng MỘT đường đi của một ticket, từ lúc vào tới lúc ra. Điểm bắt đầu tốt nhất là `src/agent/workflow.py` (hàm `process_ticket`) — đọc phần thân hàm theo thứ tự, mỗi lần thấy gọi sang module khác thì ghi tên tệp đó vào một ô trống. Bạn sẽ đi qua khoảng 6 tệp trước khi tới "dự thảo chờ duyệt".

```
ticket → ______________________ → ______________________
       → ______________________ → ______________________
       → ______________________ → ______________________
       → dự thảo chờ duyệt
```

### 1b — Bản đồ thành phần

**Cách nghĩ:** với mỗi thành phần của slide, tìm tệp (hoặc thư mục) trong `src/` đang đảm nhiệm nó. Các nơi cần nhìn: `src/ui/`, `src/api/`, `src/agent/`, `src/knowledge/`, `src/store.py`, `src/guardrails/`, `src/llm/`, `src/config.py`. "Trách nhiệm" trả lời câu: **nếu xóa phần này đi, hệ thống mất khả năng gì?** — trả lời bằng một hành động (ví dụ "gọi model qua API"), không diễn giải lại tên tệp. Lưu ý slide 11 xếp cả API vào Experience Layer (một cách con người/hệ thống khác tiếp cận AI).

| Thành phần (slide) | Tệp trong repo | Trách nhiệm — nếu xóa thì mất khả năng gì |
|---|---|---|
| Experience (11–12) | `______________` | `______________________` |
| Orchestration (13–17) | `______________` | `______________________` |
| Intelligence (18) | `______________` | `______________________` |
| Context & Knowledge (19–20) | `______________` | `______________________` |
| Tools & Enterprise Systems (21–23) | `______________` | `______________________` |
| Security & Guardrails (26) | `______________` | `______________________` |
| AI Platform & Operations (24–25) | `______________` | `______________________` |

### 1c — Lớp cache thuộc AI Platform & Operations ⚠︎

Slide 24 xếp cache vào nhóm **Cost & Latency** của tầng vận hành. Đọc `src/llm/cache.py::make_key` và `docs/adr/0002-cache-la-ha-tang.md`.

Khóa cache gồm những trường nào?
`___________________________________________________________________`

**Vì sao khóa bắt buộc chứa `base_url` và tên model?** (Câu trả lời "để chạy nhanh hơn" là **sai** — tốc độ không liên quan gì tới nội dung khóa cache.)
`___________________________________________________________________`
`___________________________________________________________________`

Chuyện gì xảy ra nếu bỏ hai trường đó, và vì sao **không ai phát hiện ra**? *(Gợi ý cách nghĩ: hai nhóm dùng hai cấu hình khác nhau nhưng tra cùng một khóa cache thì chuyện gì xảy ra với kết quả của họ?)*
`___________________________________________________________________`

---

## Bước 2 — Xác định ranh giới và cách điều phối · 20 phút

**Mục tiêu học tập 2 · Slide 8, 11–17, 21–23 · `___:___` → `___:___`**

Slide 8: kiến trúc bắt đầu bằng **xác định ranh giới** — trước khi vẽ thành phần, phải biết ai chịu trách nhiệm quyết định điều gì.

### 2a — Ai quyết định gì

**Cách nghĩ:** mỗi vai trò trả lời đúng câu hỏi slide 8 đặt ra cho nó. AI: *nên quyết định những gì, giới hạn ở đâu?* Ứng dụng nghiệp vụ: *ai kiểm tra dữ liệu, quyền hạn, business rules?* Hệ thống nghiệp vụ: *ai thực hiện hành động và lưu dữ liệu?* Con người: *khi nào cần can thiệp, ai chịu trách nhiệm cuối cùng?* Cột "Không được làm" quan trọng ngang cột "được làm" — ranh giới là chỗ ranh giới bị chặn, không phải chỗ liệt kê khả năng.

| Vai trò (slide 8) | Trong hệ thống của nhóm là gì | Được quyết định / thực hiện | KHÔNG được |
|---|---|---|---|
| AI / Agent | `__________` | `______________` | `______________` |
| Business Application | `__________` | `______________` | `______________` |
| Hệ thống nghiệp vụ / dữ liệu | `__________` | `______________` | `______________` |
| Con người | `__________` | `______________` | `______________` |

**Mô hình tương tác (slide 12):** hệ thống của nhóm thuộc loại nào?
`[ ] Chat` · `[ ] Copilot` · `[ ] Embedded AI` · `[ ] Background Agent`

Trên thang **Ask → Assist → Suggest → Act**, AI của nhóm dừng ở mức: `______________`. Vì sao không cao hơn?
`___________________________________________________________________`

### 2b — Workflow hay Agent

**Cách nghĩ:** slide 16 đưa một phổ bốn mức, từ đường đi hoàn toàn định sẵn tới đường đi do AI tự quyết: **(1) Workflow → (2) Workflow có AI → (3) Workflow + Agent → (4) Agent.** Cách chọn là đi lần lượt bốn câu hỏi bên dưới, dừng ở câu đầu tiên trả lời "Có". Trả lời bằng **bằng chứng lấy từ code** (ví dụ chỉ ra một dòng trong `process_ticket` quyết định bước tiếp theo), không trả lời bằng cảm nhận.

| Câu hỏi quyết định (slide 16) | Có / Không | Bằng chứng từ code |
|---|---|---|
| Đường đi đã rõ ràng? → dùng Workflow | `____` | `______________________` |
| Chỉ cần AI làm các tác vụ cụ thể trong đường đi đó? → Workflow có AI | `____` | `______________________` |
| Chỉ một phần bài toán còn mở? → Workflow + Agent | `____` | `______________________` |
| Toàn bộ đường đi phải linh hoạt? → Agent | `____` | `______________________` |

Mức nhóm chọn: `[ ] 1`  `[ ] 2`  `[ ] 3`  `[ ] 4`

**Câu thảo luận ở slide 17:** khi thiết kế một AI Application, nên *bắt đầu từ Agent rồi giảm autonomy*, hay *bắt đầu từ workflow rồi thêm autonomy ở nơi thực sự cần*? Với hệ thống của nhóm, chọn hướng nào và vì sao?
`___________________________________________________________________`
`___________________________________________________________________`

### 2c — Tool Contract

**Cách nghĩ:** slide 21 tách rạch ròi: **Knowledge giúp AI ra quyết định; Tools cho phép AI thực thi hành động lên hệ thống.** Vì tool chạm vào hệ thống nghiệp vụ, slide 22 đòi mỗi tool có một **hợp đồng năm phần**: Input Contract (AI được truyền gì), Permission (AI có được phép làm không), Business Rules (hành động có hợp lệ không), Execution (thực thi thế nào), Output Contract (trả kết quả gì). Chọn **một** tool trong `src/agent/tools.py` và đọc `validate_args` cùng `ToolRunner` để tìm câu trả lời cho từng phần. Nếu một phần không có trong code, ghi "chưa có" — đó là một phát hiện, không phải chỗ để bịa.

Tool được chọn: `______________________`

| Phần của hợp đồng | Trong tool này |
|---|---|
| 1. Input Contract | `______________________` |
| 2. Permission | `______________________` |
| 3. Business Rules | `______________________` |
| 4. Execution | `______________________` |
| 5. Output Contract | `______________________` |

Slide 23 so sánh hai cách: model gọi tool qua API/service có kiểm soát, và model tự chạy thẳng lệnh vào cơ sở dữ liệu. **Vì sao cách thứ hai không nên?** Nêu ít nhất hai lý do gắn với dữ liệu thuê bao:
`___________________________________________________________________`
`___________________________________________________________________`

---

## Bước 3 — Chiến lược model · 20 phút

**Mục tiêu học tập 3 · Slide 18, 30–33 · `___:___` → `___:___`**

Slide 31: **không có "best model"** — chỉ có model phù hợp với bài toán, dữ liệu, ràng buộc và bối cảnh triển khai. Làm bước này song song: chạy thí nghiệm 3a trước (mất vài phút), rồi điền 3b trong lúc chờ.

### 3a — Thí nghiệm đo (chạy trước)

Cùng một model, đo qua hai cấu hình hạ tầng (Ollama/L, vLLM/S) ở hai mức nhiệt độ. Mục tiêu không phải để biết "cấu hình nào nhanh hơn" — mà để tự tay đo ra vì sao một ứng dụng AI cần **tham số khác nhau cho từng tác vụ**, thay vì nghe giảng viên nói suông. Số đo này cũng là bằng chứng cho tiêu chí "khả thi vận hành" ở 3b.

```bash
CACHE_MODE=off uv run python scripts/compare_models.py --tickets 5
```

⚠︎ `CACHE_MODE=off` là bắt buộc. Quên nó thì nhóm đang đo tốc độ đọc SQLite, không phải tốc độ suy luận.

| Tổ hợp | **Cấu hình** | Đúng | p50 (ms) | Số ca phải cứu bằng lớp phòng vệ |
|---|---|---|---|---|
| Qwen3-8B · nhiệt độ 0.0 | L | `____%` | `______` | `___/5` |
| Qwen3-8B · nhiệt độ 0.7 | L | `____%` | `______` | `___/5` |
| Qwen3-8B · nhiệt độ 0.0 | S | `____%` | `______` | `___/5` |
| Qwen3-8B · nhiệt độ 0.7 | S | `____%` | `______` | `___/5` |

Nhiệt độ ảnh hưởng thế nào tới **phân loại**?
`___________________________________________________________________`

Còn với **soạn phản hồi** thì sao? Vì sao khác? *(Gợi ý cách nghĩ: phân loại cần MỘT đáp án đúng lặp lại được; soạn phản hồi cần câu chữ không bị cứng nhắc lặp lại giống hệt nhau mỗi lần.)*
`___________________________________________________________________`

Mở `src/config.py`, tìm `TASK_PARAMS`. Nhóm có đồng ý với các giá trị ở đó không? Nếu đổi, đổi cái gì và vì sao?
`___________________________________________________________________`

> Kết luận cần chốt: **một ứng dụng AI không dùng chung một cấu hình model cho mọi bước.**

### 3b — Chọn model bằng bốn tiêu chí (slide 31)

**Cách nghĩ:** với model của khóa (Qwen3-8B), đi qua bốn câu hỏi theo đúng thứ tự slide và ghi **bằng chứng** cho từng câu — có thể lấy từ Bước 3a, từ Canvas hôm nay, hoặc từ ràng buộc dữ liệu của bài toán. Sau đó nêu **một model khác** nhóm đã cân nhắc và lý do loại. Mục "Doanh nghiệp" hay bị bỏ qua: dữ liệu thuê bao có được gửi ra dịch vụ đám mây bên ngoài không?

| Tiêu chí (slide 31) | Câu hỏi | Bằng chứng của nhóm |
|---|---|---|
| 1. Phù hợp năng lực | Có làm được việc? (sinh nội dung, suy luận, dùng tool, đầu ra có cấu trúc, ngữ cảnh dài) | `______________________` |
| 2. Đủ chất lượng | Đáp ứng yêu cầu chưa? (ngưỡng theo tác vụ, độ tin cậy, mức bịa) | `______________________` |
| 3. Khả thi vận hành | Có chạy được không? (độ trễ, chi phí, mở rộng, nơi triển khai) | `______________________` |
| 4. Phù hợp doanh nghiệp | Có được phép dùng không? (bảo mật, tuân thủ, chính sách, môi trường) | `______________________` |

Model khác đã cân nhắc: `______________`  ·  Bị loại vì tiêu chí số `___`, lý do:
`___________________________________________________________________`

### 3c — Một model hay nhiều model (slide 32–33)

**Cách nghĩ:** đếm cho chính xác — đừng chỉ đếm model sinh văn bản. Slide 18 cho thấy tầng Intelligence gồm nhiều loại model cho nhiều loại tác vụ (tìm kiếm cần embedding, phân loại có thể dùng model nhỏ, sinh nội dung dùng LLM). Mở `.env.example` để xem hệ thống này cấu hình những model nào.

Hệ thống của nhóm dùng bao nhiêu model? Liệt kê từng model và việc nó làm:
`___________________________________________________________________`

Trong bốn dấu hiệu "khi nào nên thêm model" ở slide 33 (thiếu năng lực · tác vụ đặc thù · ràng buộc triển khai · lợi ích đủ lớn so với chi phí), dấu hiệu nào — nếu xuất hiện — sẽ khiến nhóm thêm một model nữa? Thêm để làm việc gì?
`___________________________________________________________________`

---

## Bước 4 — Design Patterns và luồng end-to-end · 25 phút

**Mục tiêu học tập 4, 5, 6 · Slide 34–43 · `___:___` → `___:___`**

### 4a — Chọn pattern (slide 41)

**Cách nghĩ:** slide 35–40 giới thiệu bốn pattern, mỗi pattern giải một loại vấn đề: **Grounded Generation** (AI thiếu tri thức cần thiết → bổ sung từ nguồn nội bộ, RAG là cách hiện thực), **Controlled Action** (AI cần thực hiện hành động → qua tool có kiểm soát), **AI-Augmented Workflow** (đường đi đã biết, một số bước cần AI), **Bounded Agent** (đường đi phải quyết định lúc chạy, trong ranh giới cho trước). Cộng thêm **Human-in-the-Loop** cho quyết định rủi ro cao. Slide 41 nói **pattern kết hợp được với nhau**: đi qua năm câu hỏi, câu nào "Có" thì hệ thống dùng pattern đó — và chỉ ra pattern đó nằm ở tệp nào. Pattern nào **không** dùng cũng cần có lý do.

| Câu hỏi chọn pattern (slide 41) | Có / Không | Pattern | Nằm ở đâu trong code |
|---|---|---|---|
| AI có thiếu knowledge cần thiết không? — "AI cần biết gì?" | `____` | Grounded Generation | `______________` |
| AI có cần thực hiện action không? — "AI được làm gì?" | `____` | Controlled Action | `______________` |
| Đường đi đã biết trước? — "Quy trình như thế nào?" | `____` | AI-Augmented Workflow | `______________` |
| Đường đi phải quyết định khi runtime? — "AI tự quyết định ra sao?" | `____` | Bounded Agent | `______________` |
| Quyết định / action có rủi ro cao? — "Ai chịu trách nhiệm?" | `____` | Human-in-the-Loop | `______________` |

Pattern nào hệ thống **không** dùng, và vì sao dùng nó ở đây là quá mức?
`___________________________________________________________________`

Hệ thống của nhóm ghép những pattern nào lại với nhau? (một câu)
`___________________________________________________________________`

### 4b — Luồng end-to-end có nhánh lỗi

**Cách nghĩ:** đây là mục tiêu học tập 4 của slide — mô tả luồng xử lý từ đầu đến cuối, gồm cả nhánh lỗi và cơ chế kiểm soát. Dùng chính chuỗi tệp ở 1a làm khung, mỗi dòng là một bước. Slide 26: **guardrail phải đặt tại nơi rủi ro phát sinh, không chỉ ở output cuối cùng** — nên cột guardrail hỏi từng bước: rủi ro nào có thể xuất hiện ở đây, và có gì chặn nó không? Cột cuối là "phương án dự phòng" — cột hay bị bỏ trống nhất; giảng viên sẽ kiểm đúng cột đó.

| # | Bước | Thành phần (tầng) | Vào → Ra | Guardrail đặt tại đây | Nếu lỗi / không chắc thì |
|---|---|---|---|---|---|
| 1 | `________` | `______` | `________` | `________` | `________________` |
| 2 | `________` | `______` | `________` | `________` | `________________` |
| 3 | `________` | `______` | `________` | `________` | `________________` |
| 4 | `________` | `______` | `________` | `________` | `________________` |
| 5 | `________` | `______` | `________` | `________` | `________________` |
| 6 | `________` | `______` | `________` | `________` | `________________` |
| 7 | `________` | `______` | `________` | `________` | `________________` |

**Nguyên tắc tầng trên không gọi vượt cấp — vì sao?** *(Gợi ý cách nghĩ: nếu tầng Giao diện gọi thẳng xuống tầng Intelligence, bỏ qua tầng Orchestration ở giữa, điều gì đặt ở tầng Orchestration sẽ bị bỏ sót?)*
`___________________________________________________________________`

### 4c — Blueprint: bảy mục (slide 43)

**Cách nghĩ:** slide 43 nói kiến trúc phải được biến thành một **AI-Ready Spec** — đủ rõ để đội phát triển bắt tay vào làm. Spec gồm bảy mục. Không cần viết dài: mỗi mục một câu trả lời cô đọng, lấy từ những gì bạn vừa làm ở Bước 1–4b, rồi chép sang `docs/blueprint.md`. Blueprint mô tả **trách nhiệm và giao diện giữa các thành phần**, không mô tả cách hiện thực bên trong — vẽ tới mức mã nguồn là lỗi thường gặp nhất ở bước này.

| # | Mục (slide 43) | Câu hỏi mục này phải trả lời | Câu trả lời của nhóm | Lấy từ |
|---|---|---|---|---|
| 1 | Use Case Contract | Hệ thống nhận gì, trả gì, cho ai dùng, giới hạn ở đâu? | `______________` | Canvas hôm nay |
| 2 | Context Contract | AI cần biết những thông tin nào, lấy ở đâu, đảm bảo luôn mới và chính xác thế nào? (slide 29) | `______________` | Bước 1b |
| 3 | Model / Intelligence | Dùng model nào cho tác vụ nào, vì sao? | `______________` | Bước 3 |
| 4 | Tool Contract | Tool nào, hợp đồng năm phần ra sao? | `______________` | Bước 2c |
| 5 | Agent / Workflow | Mức nào trên phổ bốn mức, pattern nào ghép với nhau? | `______________` | Bước 2b, 4a |
| 6 | Guardrails & Policy | Đâu là ranh giới AI không được vượt, kiểm soát dữ liệu / hành động / nội dung ở đâu? (slide 29) | `______________` | Bước 2a, 4b |
| 7 | Evaluation | Đo thành công bằng chỉ số nào? | `______________` | Canvas ô 5 |

---

## Bước 5 — Ghi lại thành năm ADR · 15 phút

**`___:___` → `___:___`**

**Cách nghĩ:** những quyết định bạn vừa đưa ra ở Bước 2–4 chính là nguyên liệu của ADR — không cần nghĩ thêm quyết định mới, chỉ cần chọn năm quyết định **có phương án thay thế thật sự**. Một ADR (Architecture Decision Record) không phải "báo cáo đã làm gì" — nó ghi lại **đã cân nhắc và LOẠI những phương án nào, vì sao**. Mẫu bốn phần ở `docs/adr/0000-template.md`, và 5 ADR mẫu có sẵn trong `docs/adr/` để tham khảo cách viết — đọc một bản trước khi viết bản của nhóm. Nơi dễ tìm quyết định: mức Workflow/Agent (2b), ranh giới cho tool (2c), chọn model (3b), số lượng model (3c), pattern (4a).

⚠︎ Phần **"Các phương án đã cân nhắc"** là phần hay bị bỏ nhất — thiếu nó thì đó không phải ADR, chỉ là một tuyên bố. "Phương án đã loại" phải là một lựa chọn thật sự nhóm có cân nhắc, không phải một phương án dựng lên cho có để loại. Nhóm tự viết, không sao chép ADR mẫu.

| # | Tệp | Quyết định (lấy từ bước nào) | Phương án đã LOẠI | Lý do loại |
|---|---|---|---|---|
| 1 | `docs/adr/____` | `______________` | `______________` | `______________` |
| 2 | `docs/adr/____` | `______________` | `______________` | `______________` |
| 3 | `docs/adr/____` | `______________` | `______________` | `______________` |
| 4 | `docs/adr/____` | `______________` | `______________` | `______________` |
| 5 | `docs/adr/____` | `______________` | `______________` | `______________` |

> Bảng này **chính là tài liệu dùng để phản biện ở Session 6**. Ghi nghiêm túc bây giờ, đừng cố nhớ lại vào ngày cuối. Phần bảo vệ quyết định thiết kế chiếm 1,5/10 điểm cuối khóa.

---

## Bước 6 — Nối dây và kích hoạt CI · 15 phút

**Mục đích: từ kiến trúc sang Development Starter Kit (slide 42) · `___:___` → `___:___`**

### 6a — Kiểm chứng chuyển cấu hình không sửa mã

Mục đích: chứng minh bằng tay rằng đổi `CONFIG_PROFILE` chỉ là đổi biến môi trường — nếu phải sửa một dòng code nào đó, đó là dấu hiệu kiến trúc đang sai (hạ tầng và logic nghiệp vụ bị trộn lẫn).

```bash
CONFIG_PROFILE=L uv run python scripts/check_env.py --skip-llm
CONFIG_PROFILE=S uv run python scripts/check_env.py --skip-llm
```

| | Kết quả | Có phải sửa dòng mã nào không? |
|---|---|---|
| Cấu hình L | PASS / FAIL | Có / **Không** |
| Cấu hình S | PASS / FAIL | Có / **Không** |

### 6b — Đẩy nhánh, xem CI chạy lần đầu

```bash
git add -A && git commit -m "[LAB-2] Blueprint và ADR" && git push -u origin team/______
```

CI giai đoạn 1 (kiểm tra mã): `[ ] xanh`  ·  `[ ] đỏ`

Nếu đỏ, lỗi gì và sửa thế nào? *(CI đỏ ở lần đầu là bình thường — đọc kỹ log lỗi trước khi hỏi trợ giảng.)*
`___________________________________________________________________`

### 6c — Khởi động giao diện

```bash
uv run streamlit run src/ui/app.py
```

Ảnh chụp màn hình: `____________________`

---

## Mốc kiểm tra cuối buổi · 5 phút

```bash
uv run pytest -m lab2
uv run python scripts/checkpoint.py 2 --team ______
```

Kết quả: `[ ] ĐỦ ĐIỀU KIỆN`  ·  `[ ] THIẾU ____/____`

### Nộp
- [ ] `docs/blueprint.md` đủ năm tầng theo slide 10, mỗi thành phần có dự phòng, đủ bảy mục ở 4c
- [ ] ≥ 5 ADR trong `docs/adr/`, mỗi ADR đủ bốn phần
- [ ] Kết quả kiểm chứng chuyển cấu hình
- [ ] Ảnh chụp giao diện chạy được

---

## Nếu xong sớm

### Governance và vận hành (slide 25, 27)

Slide 27 chia Governance thành năm mảng: **Policy · Risk · Model · Change · Compliance & Audit**. Slide 25 vẽ vòng vận hành **Run → Observe → Evaluate → Improve → Deploy**. Với mỗi mảng, chỉ ra hệ thống hiện có thứ gì (một tệp, một quy trình, một công cụ) — hoặc ghi "chưa có" nếu không có. Những ô "chưa có" chính là việc của Session 5 và 6.

| Mảng | Hệ thống hiện có gì |
|---|---|
| Policy | `______________` |
| Risk | `______________` |
| Model | `______________` |
| Change | `______________` |
| Compliance & Audit | `______________` |

### Dự đoán Session 4

Vẽ sơ đồ tuần tự cho luồng xử lý một ticket **có gọi công cụ** — dự đoán trước cấu trúc sẽ xây ở Session 4, dựa trên những gì đã đọc ở Bước 1 và 2c.

Cuối Session 4 quay lại đây, ghi:

| Nhóm dự đoán | Thực tế | Vì sao khác |
|---|---|---|
| `________________` | `________________` | `________________` |
