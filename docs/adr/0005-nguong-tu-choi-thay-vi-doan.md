# ADR-0005: Thà im lặng chuyển người còn hơn trả lời không có căn cứ

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-01-19
- **Người quyết định:** Hội đồng xây dựng chương trình
- **Mã spec liên quan:** [SPEC-RAG-03](../../PROJECT-SPEC.md#spec-rag-03), [SPEC-FLOW-02](../../PROJECT-SPEC.md#spec-flow-02), [SPEC-PROMPT-03](../../PROJECT-SPEC.md#spec-prompt-03)

## Bối cảnh

Hệ thống truy hồi chính sách từ kho tri thức rồi sinh dự thảo phản hồi. Kho tri thức có 28 tài liệu và cố ý không bao phủ hết mọi câu hỏi khách hàng có thể đặt — bộ hỏi–đáp vàng chứa 5 câu không có đáp án trong kho.

Model 3 tỉ tham số, khi được đưa các đoạn tài liệu không liên quan, có xu hướng vẫn viết ra một câu trả lời trôi chảy dựa trên kiến thức chung của nó. Câu trả lời đó nghe rất hợp lý và hoàn toàn sai.

## Các phương án đã cân nhắc

1. **Luôn sinh phản hồi, để người duyệt tự phát hiện chỗ sai.** Ưu: tỉ lệ tự động hóa cao, con số báo cáo đẹp. Nhược: đặt gánh nặng kiểm chứng lên người duyệt đúng vào lúc dự thảo trông thuyết phục nhất. Một dự thảo bịa ra chính sách bồi thường mà viết trôi chảy sẽ được bấm duyệt.

2. **Đặt ngưỡng điểm tương đồng, dưới ngưỡng thì gắn cảnh báo nhưng vẫn sinh.** Ưu: dung hòa. Nhược: cảnh báo nhìn mãi thành quen, và người duyệt sẽ bỏ qua nó sau ngày làm việc thứ ba.

3. **Dưới ngưỡng thì KHÔNG gọi model sinh phản hồi, chuyển thẳng giao dịch viên.** Ưu: ranh giới rõ ràng, không phụ thuộc sự tỉnh táo của người duyệt; tiết kiệm lời gọi model. Nhược: tỉ lệ chuyển người cao hơn, con số tự động hóa kém đẹp hơn.

## Quyết định

Chọn phương án 3. Kiểm tra `retrieval.grounded` diễn ra **trước** khi gọi model sinh phản hồi, không phải sau. Ngưỡng mặc định `RETRIEVE_MIN_SCORE=0.35`, là tham số cấu hình được để học viên hiệu chỉnh và đo lại ở Session 6.

Prompt sinh phản hồi có thêm lớp phòng vệ thứ hai: model được yêu cầu trả về đúng chuỗi `KHÔNG ĐỦ CĂN CỨ` khi tự thấy ngữ cảnh không đủ.

Tiêu chí quyết định: **với bài toán chăm sóc khách hàng, một trợ lý bịa ra chính sách gây rủi ro nghiệp vụ nghiêm trọng hơn nhiều so với một trợ lý im lặng và chuyển tiếp cho người xử lý.** Chi phí của việc chuyển thừa là vài phút của một giao dịch viên. Chi phí của một cam kết bồi thường sai là một nghĩa vụ pháp lý.

## Hệ quả chấp nhận

- Chỉ số `over_escalation_rate` sẽ cao hơn so với phương án 1, và đó là kết quả mong muốn chứ không phải khuyết điểm cần che.
- Ngưỡng 0.35 là một con số chọn theo kinh nghiệm, không có căn cứ lý thuyết. Nó **phải** được hiệu chuẩn lại nếu đổi model embedding hoặc đổi chiến lược chia đoạn — và việc hiệu chuẩn đó là một trong hai cải tiến gợi ý cho Session 6.
- Bộ chỉ số đánh giá phải đo `refusal_accuracy` tách riêng khỏi `recall`, vì một hệ thống truy hồi kém nhưng từ chối đúng vẫn an toàn hơn một hệ thống truy hồi khá nhưng không bao giờ từ chối.
- Guardrail đầu ra vẫn phải chặn cam kết tiền một lần nữa, kể cả khi đã có căn cứ. Hai lớp phòng vệ cho cùng một rủi ro là có chủ ý: đây là rủi ro nghiêm trọng nhất của hệ thống.
