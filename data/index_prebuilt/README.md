# Chỉ mục dựng sẵn

Thư mục này chứa `index.json` — chỉ mục vector của 28 tài liệu tri thức, dựng sẵn bằng `bge-m3` và **commit vào repo**.

## Vì sao commit một tệp sinh ra được

Dựng chỉ mục mất 2–4 phút mỗi máy cho khoảng 300 đoạn. Với 6 nhóm chạy song song trong 35 phút của bước 3 Session 3, đó là thời gian không có để mất. Bản dựng sẵn là **mặc định của lớp**; việc học viên tự chạy [`scripts/build_index.py`](../../scripts/build_index.py) chỉ để xác minh mình dựng lại được.

Chỉ mục dùng chung được vì `bge-m3` giống nhau ở cả cấu hình S và cấu hình L ([`SPEC-INFRA-01`](../../PROJECT-SPEC.md#spec-infra-01)). Đây là lý do ràng buộc đó tồn tại: **quyết định hạ tầng không được ảnh hưởng tới kho tri thức.**

## Ai dựng, và khi nào

Đơn vị tổ chức dựng ở mốc T−1 tuần, sau khi kho tri thức đã chốt:

```
uv run python scripts/build_index.py --out data/index_prebuilt
git add data/index_prebuilt/index.json
git commit -m "[SPEC-RAG-01] Chỉ mục dựng sẵn, bge-m3, cấu hình tham chiếu"
```

Sửa bất kỳ tài liệu nào trong [`data/knowledge/`](../../data/knowledge/) thì **bắt buộc dựng lại chỉ mục trong cùng một PR**. Chỉ mục lệch với kho tri thức là một lỗi im lặng: truy hồi vẫn trả về kết quả, chỉ là kết quả sai.

## Khi tệp này chưa có

`Retriever` tự dựng chỉ mục từ khóa trong bộ nhớ từ [`data/knowledge/`](../../data/knowledge/). Tìm kiếm vẫn hoạt động, chỉ kém chính xác hơn vì không có vector nhúng. Nhờ đường lùi này mà bộ kiểm thử chạy được ngay sau khi clone, và CI chạy được trên runner không có GPU.
