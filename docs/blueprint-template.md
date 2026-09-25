# AI SOLUTION BLUEPRINT — <Tên nhóm>

> **Cách dùng khung này:** sao chép thành `docs/blueprint.md` rồi điền. Lệnh: `cp docs/blueprint-template.md docs/blueprint.md` (Windows: `copy docs\blueprint-template.md docs\blueprint.md`). Xóa các dòng hướng dẫn bắt đầu bằng "Gợi ý:" sau khi điền xong.
>
> Blueprint mô tả **trách nhiệm và giao diện giữa các thành phần**, không mô tả cách hiện thực bên trong. Viết đủ rõ để một người chưa dự buổi học đọc xong vẫn hiểu hệ thống gồm những gì và mảnh nào hỏng thì chuyện gì xảy ra.

| | |
|---|---|
| Nhóm | |
| Thành viên | |
| Ngày | |
| Cấu hình chạy | S / L |
| ADR liên quan | `docs/adr/0006` … |

---

## 1. Hệ thống gồm những thành phần nào

Gợi ý: đây là kết quả Bước 1 của Workbook 2. Mỗi dòng một thành phần. Cột "Dự phòng khi hỏng" là cột hay bị bỏ trống nhất — hãy trả lời câu hỏi: *nếu thành phần này không phản hồi giữa lúc đang xử lý, hệ thống làm gì tiếp theo?*

| Thành phần (theo slide 10) | Tệp trong repo | Nhận vào | Trả ra | Dự phòng khi hỏng |
|---|---|---|---|---|
| Experience | | | | |
| Orchestration | | | | |
| Intelligence | | | | |
| Context & Knowledge | | | | |
| Tools & Enterprise Systems | | | | |
| Security & Guardrails (xuyên suốt) | | | | |
| AI Platform & Operations (xuyên suốt) | | | | |

## 2. Use Case Contract — hệ thống nhận gì, trả gì, cho ai

Gợi ý: lấy từ Canvas ô 1, 2, 7 của buổi sáng. Tối đa ba câu.



## 3. Context Contract — AI cần biết gì, lấy ở đâu

Gợi ý: AI cần những thông tin nào để làm đúng việc? Mỗi nguồn nằm ở đâu, và làm sao bảo đảm thông tin luôn mới và chính xác (ví dụ tài liệu chính sách hết hiệu lực thì sao)?



## 4. Model / Intelligence — dùng model nào cho việc gì, vì sao

Gợi ý: lấy từ Bước 3 của Workbook 2 (bốn tiêu chí, số model, tham số nhiệt độ theo tác vụ).



## 5. Tool Contract — công cụ nào, hợp đồng ra sao

Gợi ý: lấy từ Bước 2c. Mỗi công cụ một dòng: nhận gì, ai được gọi, luật nghiệp vụ, thực thi thế nào, trả gì.

| Công cụ | Nhận vào | Quyền | Luật nghiệp vụ | Thực thi | Trả ra |
|---|---|---|---|---|---|
| | | | | | |

## 6. Agent / Workflow — mức tự chủ và pattern

Gợi ý: lấy từ Bước 2b và 4a. Ghi rõ mức đã chọn trên phổ bốn mức (Workflow → Workflow có AI → Workflow + Agent → Agent), các pattern được dùng và ghép với nhau ở đâu, và lý do không chọn mức cao hơn.



## 7. Guardrails & Policy — ranh giới AI không được vượt

Gợi ý: lấy từ Bước 2a và 4b. Liệt kê những việc AI tuyệt đối không được làm, và guardrail đặt ở bước nào của hành trình một ticket.



## 8. Evaluation — đo thành công bằng gì

Gợi ý: lấy từ Canvas ô 5. Ghi chỉ số, ngưỡng "đạt", và buổi nào sẽ đo.



## 9. Điều blueprint này CHƯA giải quyết

Gợi ý: một blueprint không nêu giới hạn của chính nó là một blueprint chưa xong. Ghi ít nhất hai giới hạn mà nhóm nhìn thấy (ví dụ: thiếu xác thực người dùng, thiếu cách cập nhật kho tri thức khi đang chạy).

- 
- 
