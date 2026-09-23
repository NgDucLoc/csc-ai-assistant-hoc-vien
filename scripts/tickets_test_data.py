"""40 ticket kiểm định, viết tay và gán nhãn thủ công.

**BẮT BUỘC giữ kín tới Lab 5** (SPEC-DATA-04). Tệp này nằm ở nhánh khóa riêng
và chỉ merge vào ``main`` sau khi Session 4 kết thúc.

Lý do rất cụ thể: nếu học viên nhìn thấy tập kiểm định trong lúc tinh chỉnh
prompt, họ sẽ vô tình tối ưu theo chính tập đó, và mọi con số đánh giá ở Lab 5
mất hoàn toàn ý nghĩa. Đây không phải chuyện hình thức — nó là điều kiện để
Session 5 dạy được nội dung về tính tái lập và về giữ riêng tập kiểm định.

Bẫy sư phạm trong tập này: 2 ticket mơ hồ, 1 ticket chứa thông tin cá nhân,
1 ticket rác. Phần còn lại của hạn ngạch bẫy nằm ở tập huấn luyện.

Tập này cố ý chứa nhiều ca thuộc hai nhóm dễ nhầm ``cuoc_thanh_toan`` và
``goi_cuoc_khuyen_mai``, để ma trận nhầm lẫn ở Session 5 có tín hiệu rõ và
học viên rút ra được kết luận đúng: đôi khi vấn đề nằm ở định nghĩa nhãn chứ
không nằm ở model.
"""

from __future__ import annotations

from typing import Any

TEST_CASES: list[dict[str, Any]] = [
    # cước và thanh toán (11)
    {
        "msg": "Hóa đơn tháng này của tôi là 512 nghìn trong khi gói chỉ 149 nghìn. Các anh giải thích giúp phần chênh lệch.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi thanh toán qua ví điện tử lúc 10 giờ sáng, tới giờ hệ thống vẫn chưa ghi nhận.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Xin hỏi nếu tôi đóng cước muộn 5 ngày thì bị phạt bao nhiêu tiền?",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi đi công tác Hàn Quốc 4 ngày mà cước lên 6 triệu. Tôi không chấp nhận, đề nghị hủy khoản này ngay lập tức nếu không tôi kiện.",
        "cat": "cuoc_thanh_toan",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
    },
    {
        "msg": "Mất mạng 3 ngày liền tuần trước, tôi muốn được bồi thường cước những ngày đó.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi bị trừ 15 nghìn mỗi tuần cho dịch vụ nào đó mà tôi không đăng ký. Hủy giúp tôi và hoàn lại tiền.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Cho hỏi bản kê chi tiết cuộc gọi có được đọc qua điện thoại không, tôi cần gấp.",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
        "note": "KB-019 cấm đọc bản kê qua điện thoại. Hệ thống phải trả lời đúng ràng buộc này.",
    },
    {
        "msg": "Thẻ cào tôi mua bị mờ mất 2 số, giờ nạp không được. Xử lý thế nào?",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi khiếu nại cước từ 20 ngày trước, giờ vẫn chưa thấy ai trả lời.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Trong thời gian đang khiếu nại cước, tôi có phải đóng phần tiền đang tranh chấp không?",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi muốn biết cước chuyển vùng của tôi tại Thái Lan là bao nhiêu một ngày.",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    # chất lượng kết nối (8)
    {
        "msg": "Khu vực Hà Đông từ 6 giờ sáng nay không có sóng, cả tòa nhà tôi đều vậy.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "buc_boi",
    },
    {
        "msg": "Mạng của tôi chậm từ hôm qua, tải một trang web mất cả phút.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Gọi trong nhà thì được, ra ngoài đường lại mất sóng liên tục. Đây là lỗi gì?",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tối qua từ 0 giờ tới 2 giờ mất mạng, sáng nay lại bình thường. Có phải bảo trì không?",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Cửa hàng tôi dùng máy quẹt thẻ qua mạng di động, hai hôm nay rớt liên tục nên không bán hàng được.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
    },
    {
        "msg": "Tôi đo tốc độ mạng chỉ được 3 Mbps trong giờ tối, ban ngày được 40 Mbps.",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "Sự cố khu vực nhà tôi đã 4 ngày chưa xử lý xong, các anh hẹn hết lần này tới lần khác.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "gay_gat",
    },
    {
        "msg": "Máy có sóng nhưng không vào được mạng, tôi đã thử cấu hình APN theo hướng dẫn rồi vẫn không được.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
        "ambiguous": True,
        "note": "Mơ hồ giữa chat_luong_ket_noi và thiet_bi_sim. Khách hàng đã loại trừ nguyên nhân cấu hình.",
    },
    # gói cước và khuyến mãi (7)
    {
        "msg": "Tôi muốn đổi từ gói TS99 sang TS299 ngay hôm nay có được không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Gói V120N có bao nhiêu GB và có gọi ngoại mạng không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi tham gia chương trình khuyến mãi nạp thẻ nhưng không được cộng tiền, trong khi bạn tôi nạp cùng lúc thì được.",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tiền trong tài khoản khuyến mãi của tôi tự nhiên hết mà tôi chưa dùng gì.",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Đổi gói cước giữa tháng thì tính cước thế nào, có bị tính cả hai gói không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Cho hỏi gói data bổ sung D5 dùng được bao lâu và bao nhiêu GB?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi đang nợ cước, giờ muốn đổi sang gói rẻ hơn cho đỡ tốn thì có được không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P2",
        "sen": "trung_tinh",
        "ambiguous": True,
        "note": "Mơ hồ giữa goi_cuoc_khuyen_mai và cuoc_thanh_toan. KB-013 cấm đổi gói khi đang nợ cước.",
    },
    # thiết bị và SIM (6)
    {
        "msg": "SIM tôi bị mất, cần làm lại. Tôi mang căn cước ra cửa hàng là được đúng không?",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi vừa đổi SIM xong nhưng SIM mới chưa hoạt động, đã 3 tiếng rồi.",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Điện thoại tôi mua kèm gói cước, mới 7 tháng đã hỏng loa. Bảo hành thế nào?",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Mã QR eSIM các anh cấp cho tôi tuần trước giờ quét báo lỗi, không kích hoạt được.",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Thuê bao trả trước của tôi lâu không nạp tiền, giờ gọi không được. Số của tôi còn giữ được không?",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi cần khóa khẩn cấp số thuê bao vì nghi ngờ có người vừa làm lại SIM của tôi ở đâu đó.",
        "cat": "thiet_bi_sim",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
    },
    # thông tin thuê bao (5)
    {
        "msg": "Tôi cần đổi email nhận hóa đơn sang địa chỉ mới, làm qua ứng dụng được không?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Hai vợ chồng tôi muốn chuyển số thuê bao từ tên tôi sang tên vợ, cần những gì?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi bị nhắn tin báo thông tin thuê bao chưa chuẩn hóa, còn bao lâu thì bị khóa?",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi là nhân viên công ty, dùng số của công ty cấp. Cho tôi xin bản kê cước của số này.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "trung_tinh",
        "note": "KB-018: nhân viên không thuộc danh sách ủy quyền không được cung cấp thông tin cước.",
    },
    {
        "msg": "Tôi là Trần Thị B, căn cước 001300012345, số nhà 78 đường Láng. Đề nghị gửi toàn bộ lịch sử cuộc gọi 6 tháng của tôi qua tin nhắn.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "trung_tinh",
        "pii": True,
        "action": "escalate",
        "note": "Bẫy PII. KB-019 cũng cấm gửi bản kê chi tiết qua tin nhắn.",
    },
    # khác (3)
    {
        "msg": "Tôi muốn góp ý về thái độ của nhân viên tại điểm giao dịch Cầu Giấy sáng nay.",
        "cat": "khac",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "..... ??? 000 xxx",
        "cat": "khac",
        "pri": "P3",
        "sen": "trung_tinh",
        "junk": True,
        "action": "escalate",
    },
    {
        "msg": "Cho tôi hỏi tổng đài có hỗ trợ tiếng Anh không?",
        "cat": "khac",
        "pri": "P3",
        "sen": "trung_tinh",
        "note": "Kho tri thức không có tài liệu về hỗ trợ đa ngôn ngữ. Phải trả lời không đủ căn cứ.",
    },
]

assert len(TEST_CASES) == 40, f"Cần đúng 40 ticket kiểm định, đang có {len(TEST_CASES)}"
