# WORKBOOK — sáu buổi

Phân biệt ba loại tài liệu, đừng lẫn:

| Tài liệu | Là gì | Ai viết |
|---|---|---|
| `labs/LAB-N.md` | **Đề bài.** Phải làm gì, thang điểm, lỗi thường gặp | Giảng viên, cố định |
| `workbooks/WORKBOOK-N.md` | **Chỗ viết trong giờ học.** Bảng để điền, quyết định để ghi, số đo để chép | Học viên, mỗi nhóm một bản |
| `docs/canvas.md`, `docs/blueprint.md`… | **Deliverable.** Bản sạch nộp sau buổi | Học viên, chắt lọc từ workbook |

## Dùng thế nào

Đầu mỗi buổi, mỗi nhóm sao chép workbook của buổi đó vào nhánh của mình:

```bash
cp workbooks/WORKBOOK-3.md docs/workbook/nhom-a-session-3.md
```

Điền trong giờ học. Cuối buổi, chắt lọc phần cần thiết sang deliverable rồi commit cả hai.

## Vì sao tách workbook khỏi deliverable

Deliverable là bản sạch để chấm và để bàn giao. Workbook giữ **quá trình**: con số đo được ở lần thử thứ nhất, phương án đã loại, lý do loại.

Phần phản biện ở Session 6 hỏi *"nhóm đã thử phương án nào khác, kết quả ra sao?"* — câu trả lời nằm trong workbook, không nằm trong deliverable. Nhóm nào chỉ giữ bản sạch sẽ không trả lời được.

## Quy ước điền

| Ký hiệu | Nghĩa |
|---|---|
| `______` | Điền vào |
| `[ ]` | Đánh dấu khi xong |
| `S / L` | Khoanh cấu hình đang dùng |
| ⚠︎ | Chỗ hay bị bỏ trống, giảng viên sẽ kiểm |

**Mọi bảng số liệu bắt buộc ghi cấu hình.** Một con số không kèm cấu hình sinh ra nó là một con số vô nghĩa (`SPEC-INFRA-03`).
