# ADR-0003: Mọi lời gọi model đi qua đúng một cửa

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-01-17
- **Người quyết định:** Hội đồng xây dựng chương trình
- **Mã spec liên quan:** [SPEC-ARCH-02](../../PROJECT-SPEC.md#spec-arch-02), [SPEC-LLM-01](../../PROJECT-SPEC.md#spec-llm-01), [SPEC-LLM-05](../../PROJECT-SPEC.md#spec-llm-05)

## Bối cảnh

Hệ thống cần bốn thứ hoạt động đồng nhất trên mọi lời gọi model: lớp cache, ghi nhật ký có mã truy vết, đếm ngân sách gọi trên mỗi ticket, và ngắt mạch khi máy chủ suy luận treo.

Trong một dự án nhiều người cùng viết, lời gọi model có xu hướng mọc ra ở khắp nơi: một chỗ trong bộ phân loại, một chỗ trong bộ sinh phản hồi, một chỗ trong script thí nghiệm ai đó viết vội.

## Các phương án đã cân nhắc

1. **Quy ước bằng tài liệu.** Ghi vào README rằng nên dùng `LLMClient`. Ưu: không tốn công. Nhược: quy ước không được ép sẽ bị vi phạm, và vi phạm chỉ lộ ra khi hệ thống đang chịu tải — đúng lúc tệ nhất.

2. **Một lớp cơ sở mà mọi thành phần AI kế thừa.** Ưu: ép được ở mức kiểu dữ liệu. Nhược: kế thừa làm cấu trúc cứng, và vẫn không chặn được ai đó gọi `httpx.post` thẳng.

3. **Một module duy nhất, kèm bài kiểm thử quét mã nguồn để ép ràng buộc.** Ưu: ép được thật, và vi phạm bị chặn ở CI chứ không ở môi trường chạy. Nhược: bài kiểm thử dựa trên biểu thức chính quy nên có thể bỏ sót cách gọi lạ.

## Quyết định

Chọn phương án 3. Toàn bộ lời gọi model nằm trong [`src/llm/client.py`](../../src/llm/client.py). [`tests/test_lab2.py::test_no_llm_call_outside_client`](../../tests/test_lab2.py) quét mọi tệp trong [`src/`](../../src/) tìm dấu hiệu gọi trực tiếp và chặn CI nếu phát hiện.

Tiêu chí quyết định: ràng buộc kiến trúc không được ép tự động là ràng buộc sẽ bị vi phạm. Cùng nguyên tắc với việc ép chuẩn viết mã bằng `ruff` thay vì bằng lời nhắc trong buổi rà soát mã.

## Hệ quả chấp nhận

- Bài kiểm thử dùng biểu thức chính quy nên có thể bỏ sót. Nó là hàng rào, không phải chứng minh. Danh sách mẫu cần bổ sung khi phát hiện cách gọi mới.
- Mọi thí nghiệm nhanh cũng phải đi qua `LLMClient`, kể cả script dùng một lần. Hơi phiền, nhưng đổi lại là thí nghiệm nào cũng được cache và ghi log — và hóa ra đó chính là thứ cần khi muốn tái dựng lại kết quả một tuần sau.
- Ngân sách gọi model (`MAX_LLM_CALLS_PER_TICKET`) đếm được chính xác, nên [`SPEC-INFRA-04`](../../PROJECT-SPEC.md#spec-infra-04) ép được bằng `pytest` thay vì dựa vào việc học viên tự thấy chậm.
