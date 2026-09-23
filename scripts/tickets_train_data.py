"""80 ticket huấn luyện, viết tay và gán nhãn thủ công theo data/LABEL_GUIDE.md.

Công khai cho học viên từ Lab 3. Dùng để phát triển và thử prompt.

Các bẫy sư phạm có trong tập này (SPEC-DATA-05):
  - 6 ticket mơ hồ, gán được hai nhãn (``ambiguous=True``)
  - 2 ticket chứa thông tin cá nhân nhạy cảm (``pii=True``)
  - 1 ticket rác (``junk=True``)

Trường ``note`` giải thích lý do gán nhãn cho các ca khó. Giảng viên dùng nó
khi chữa bài; học viên nhìn thấy nó và đó là chủ ý — nhãn có lập luận dạy được
nhiều hơn nhãn trần.
"""

from __future__ import annotations

from typing import Any

TRAIN_CASES: list[dict[str, Any]] = [
    # ------------------------------------------------ cước và thanh toán (20)
    {
        "msg": "Tháng này tôi bị trừ 320 nghìn trong khi mọi tháng chỉ có 149 nghìn. Tôi không đăng ký thêm gì cả, đề nghị kiểm tra lại giúp tôi.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Cho tôi hỏi hóa đơn tháng 2 phát hành ngày nào và hạn thanh toán tới khi nào ạ?",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi thấy trên hóa đơn có mục cước dịch vụ giá trị gia tăng 45 nghìn mà tôi không biết là dịch vụ gì. Kiểm tra giúp tôi xem đó là cái gì.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi đã chuyển khoản thanh toán từ hôm kia rồi mà hệ thống vẫn báo nợ cước. Tiền đã trừ khỏi tài khoản ngân hàng của tôi.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tại sao tôi bị tính phí chậm nộp trong khi tôi đóng đúng ngày 20? Các anh xem lại đi, tôi có biên lai đây.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Vừa đi Nhật về, hóa đơn lên tới 4 triệu 2. Tôi có gói không giới hạn mà sao vẫn bị tính cước data như vậy?",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Nhờ tổng đài gửi lại bản kê chi tiết cước tháng 1 vào email đã đăng ký giúp tôi.",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi nạp thẻ 100 nghìn nhưng tài khoản không thấy cộng tiền. Số seri thẻ tôi vẫn giữ.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Ba tháng liên tiếp cước của tôi đều cao hơn 100 nghìn so với gói đăng ký. Lần này tôi yêu cầu hoàn lại toàn bộ phần chênh, nếu không tôi sẽ khiếu nại lên Bộ.",
        "cat": "cuoc_thanh_toan",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
        "note": "P1 vì khách hàng đe dọa khiếu nại lên cơ quan quản lý.",
    },
    {
        "msg": "Cho hỏi tôi có thể thanh toán cước bằng ví điện tử không, và bao lâu thì hệ thống ghi nhận?",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Thuê bao của tôi bị khóa vì nợ cước nhưng tôi đã đóng từ sáng nay rồi. Bao giờ mở lại?",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi muốn khiếu nại khoản cước 890 nghìn tháng 12 năm ngoái. Giờ khiếu nại còn kịp không?",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Sao tự nhiên mất tiền trong tài khoản vậy? Sáng còn 200 nghìn giờ còn 130 nghìn mà tôi không gọi ai.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Công ty tôi có 45 thuê bao, tháng này hóa đơn tổng thiếu mất bản kê chi tiết của 3 số. Gửi bổ sung giúp.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi bị mất sóng cả tuần vừa rồi, tháng này vẫn phải trả đủ cước à? Tôi muốn được giảm trừ.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
        "note": "Nội dung có nhắc mất sóng nhưng yêu cầu thực sự là về cước và bồi thường.",
    },
    {
        "msg": "Xin cho biết mức phí chậm nộp được tính như thế nào và tối đa là bao nhiêu.",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Hóa đơn tháng này có mục cước chuyển vùng 1 triệu 8 nhưng tôi không đi nước ngoài tháng đó. Kiểm tra lại.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Tôi đã hủy gói TS299 từ tháng trước rồi mà tháng này vẫn bị thu 299 nghìn.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi muốn đổi hình thức nhận hóa đơn từ giấy sang email, và hỏi luôn cước tháng này là bao nhiêu.",
        "cat": "cuoc_thanh_toan",
        "pri": "P3",
        "sen": "trung_tinh",
        "ambiguous": True,
        "note": "Mơ hồ: có cả yêu cầu đổi thông tin (thong_tin_thue_bao) lẫn hỏi cước.",
    },
    {
        "msg": "Đề nghị giải thích rõ tại sao dùng hết dung lượng rồi mà vẫn phát sinh cước data ngoài gói.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    # ------------------------------------------------ chất lượng kết nối (16)
    {
        "msg": "Khu vực nhà tôi ở Cầu Giấy mất sóng hoàn toàn từ 8 giờ sáng nay, gọi không được mà mạng cũng không có.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "buc_boi",
    },
    {
        "msg": "Mạng nhà tôi tối nào cũng chậm, xem phim toàn bị giật. Ban ngày thì bình thường.",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "Gọi đi hay bị rớt giữa chừng, một cuộc gọi phải gọi lại ba bốn lần mới xong.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Cho hỏi khu vực Thanh Xuân có đang bị sự cố gì không, cả xóm tôi đều không có mạng.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "trung_tinh",
    },
    {
        "msg": "Máy tôi hiện đủ 4 vạch sóng nhưng vào mạng không được. Đã tắt bật máy bay rồi vẫn thế.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Văn phòng công ty tôi 60 người từ sáng nay không ai gọi được. Chúng tôi đang có cuộc họp với đối tác, cần xử lý gấp.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
        "note": "P1 vì ảnh hưởng hoạt động doanh nghiệp, thuộc diện chuyển tuyến theo KB-018.",
    },
    {
        "msg": "Tốc độ mạng cam kết 5G mà tôi đo chỉ được 8 Mbps. Như vậy có đúng cam kết không?",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Nhà tôi ở vùng nông thôn, sóng lúc có lúc không đã hai tháng nay rồi mà không thấy khắc phục.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Đêm qua từ 1 giờ tới 3 giờ sáng mất mạng hoàn toàn, có phải các anh bảo trì không?",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Mạng chậm kinh khủng suốt hai ngày nay, tôi làm việc online mà không nổi. Đề nghị xử lý ngay.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "gay_gat",
    },
    {
        "msg": "Tôi ở chung cư tầng 18, trong nhà gần như không có sóng, ra ban công mới có.",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Sự cố khu vực Long Biên hôm qua các anh báo 6 tiếng là xong, giờ vẫn chưa có mạng.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "gay_gat",
    },
    {
        "msg": "Máy tôi không tự nhận cấu hình mạng, không vào được internet dù có sóng đầy.",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "trung_tinh",
        "ambiguous": True,
        "note": "Mơ hồ: có thể là thiet_bi_sim (cấu hình APN) hoặc chat_luong_ket_noi.",
    },
    {
        "msg": "Tại sao cứ đến 8 giờ tối là mạng chậm hẳn đi? Có phải các anh bóp băng thông không?",
        "cat": "chat_luong_ket_noi",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "Gọi cho tổng đài 18008098 thì được nhưng gọi số di động khác báo không liên lạc được.",
        "cat": "chat_luong_ket_noi",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Cả nhà tôi 4 số dùng mạng này, từ chiều qua tất cả đều không vào được internet.",
        "cat": "chat_luong_ket_noi",
        "pri": "P1",
        "sen": "buc_boi",
    },
    # ------------------------------------------------ gói cước, khuyến mãi (14)
    {
        "msg": "Cho tôi hỏi gói TS149 gồm những gì và cước một tháng bao nhiêu ạ?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi muốn chuyển từ gói MI50 sang gói V120N. Có phải chờ tới đầu tháng sau không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi nạp 200 nghìn trong đợt khuyến mãi mà không thấy cộng tiền khuyến mãi. Mã giao dịch tôi có đây.",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Gói không giới hạn B5G500 có thật sự không giới hạn không hay dùng nhiều bị chậm?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi muốn hủy gói data bổ sung D15 mà không biết cú pháp, hướng dẫn giúp tôi.",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tiền khuyến mãi trong tài khoản của tôi có dùng để đóng cước thuê bao tháng được không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi dùng mạng 8 năm rồi mà không thấy ưu đãi khách hàng lâu năm nào cả. Điều kiện là gì?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "Đăng ký gói mới thì gói cũ có tự hủy không, hay phải hủy thủ công?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Chuyển đổi gói cước có mất phí không? Tôi nghe nói mất 20 nghìn một lần.",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
        "note": "Ca kiểm chứng bẫy tài liệu mâu thuẫn KB-010 và KB-013. Đáp án đúng theo KB-013 là không mất phí.",
    },
    {
        "msg": "Tôi hết dung lượng tốc độ cao rồi, giờ đăng ký thêm data thì có những gói nào?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Dung lượng chưa dùng hết của gói cũ khi đổi sang gói mới có được giữ lại không?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi đăng ký gói khuyến mãi mà bị từ chối, hệ thống báo không đủ điều kiện. Tại sao?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Sao tôi bị đăng ký gói cước gì đó mà tôi không hề bấm gì cả, giờ mất tiền hàng tháng.",
        "cat": "cuoc_thanh_toan",
        "pri": "P2",
        "sen": "gay_gat",
        "ambiguous": True,
        "note": "Mơ hồ: nhắc gói cước nhưng vấn đề cốt lõi là bị trừ tiền, nên gán cuoc_thanh_toan.",
    },
    {
        "msg": "Gói cước cho học sinh sinh viên có những gói nào và cần giấy tờ gì để đăng ký?",
        "cat": "goi_cuoc_khuyen_mai",
        "pri": "P3",
        "sen": "trung_tinh",
        "note": "Kho tri thức không có tài liệu về gói sinh viên. Hệ thống phải nói không đủ căn cứ.",
    },
    # ------------------------------------------------ thiết bị và SIM (12)
    {
        "msg": "SIM của tôi bị gãy góc, giờ máy không nhận nữa. Đổi SIM mới thì làm thế nào và mất bao nhiêu tiền?",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi làm mất điện thoại, cần khóa SIM gấp để không ai dùng được.",
        "cat": "thiet_bi_sim",
        "pri": "P1",
        "sen": "buc_boi",
    },
    {
        "msg": "Máy tôi mới mua có hỗ trợ eSIM, tôi muốn chuyển sang eSIM thì làm sao?",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Điện thoại tôi mua ở cửa hàng của tổng đài, mới 4 tháng đã hỏng màn hình. Bảo hành thế nào?",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "SIM tôi tự nhiên mất tín hiệu hoàn toàn từ chiều qua. Tôi lo có ai đó đã đổi SIM của tôi.",
        "cat": "thiet_bi_sim",
        "pri": "P1",
        "sen": "gay_gat",
        "action": "escalate",
        "note": "Nghi chiếm đoạt SIM. KB-011 bắt buộc chuyển tuyến, không xử lý ở tuyến một.",
    },
    {
        "msg": "Tôi đổi máy mới, lắp SIM cũ vào thì vào mạng không được dù gọi điện bình thường.",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Cho hỏi đổi SIM 4G lên 5G có mất phí không và làm ở đâu?",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Sau khi đổi SIM tôi không nhận được mã OTP của ngân hàng. Đây là lỗi gì?",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Bộ phát wifi di động các anh bán cho tôi hỏng rồi, mới dùng 5 tháng. Bảo hành ở đâu?",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Máy tôi xách tay từ Mỹ về, sóng rất yếu trong khi máy của vợ tôi cùng chỗ lại đầy sóng.",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "buc_boi",
        "ambiguous": True,
        "note": "Mơ hồ: biểu hiện giống chat_luong_ket_noi nhưng nguyên nhân thuộc thiết bị.",
    },
    {
        "msg": "Thuê bao của tôi bị khóa một chiều, tôi không biết vì sao vì tôi trả trước.",
        "cat": "thiet_bi_sim",
        "pri": "P2",
        "sen": "buc_boi",
        "ambiguous": True,
        "note": "Mơ hồ: có thể là cuoc_thanh_toan (nợ cước) hoặc thiet_bi_sim (trạng thái thuê bao).",
    },
    {
        "msg": "Vợ tôi mất SIM, tôi muốn ra cửa hàng làm lại giúp vợ thì cần mang những gì?",
        "cat": "thiet_bi_sim",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    # ------------------------------------------------ thông tin thuê bao (12)
    {
        "msg": "Tôi vừa chuyển nhà, muốn cập nhật địa chỉ nhận hóa đơn thì làm ở đâu?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi muốn chuyển số thuê bao này sang tên con trai tôi. Thủ tục thế nào?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Hệ thống báo thông tin thuê bao của tôi chưa chuẩn hóa và sắp bị khóa. Tôi phải làm gì?",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Một cá nhân được đăng ký tối đa bao nhiêu số thuê bao trả trước?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi đổi họ tên theo quyết định của tòa án, giờ cần cập nhật trên thuê bao.",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Công ty tôi muốn thêm một người vào danh sách được ủy quyền liên hệ. Làm thế nào?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tôi muốn kiểm tra xem số của tôi đang đứng tên ai, vì tôi mua lại số này từ người khác.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "trung_tinh",
    },
    {
        "msg": "Sao tôi phải ra tận cửa hàng mới đổi được thông tin, không làm online được à? Bất tiện quá.",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "buc_boi",
    },
    {
        "msg": "Tôi làm thủ tục chuyển nhượng tuần trước mà tra vẫn thấy tên chủ cũ.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "buc_boi",
    },
    {
        "msg": "Cho tôi biết cú pháp tra cứu thông tin thuê bao đang đăng ký với ạ.",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Doanh nghiệp tôi có 220 thuê bao, hạn thanh toán hóa đơn tổng là ngày nào?",
        "cat": "thong_tin_thue_bao",
        "pri": "P3",
        "sen": "trung_tinh",
        "ambiguous": True,
        "note": "Mơ hồ: hỏi về hạn thanh toán (cuoc_thanh_toan) trong bối cảnh hợp đồng doanh nghiệp.",
    },
    {
        "msg": "Số căn cước của tôi là 001199012345, tài khoản ngân hàng 19035678901234 ở Techcombank. Đề nghị cập nhật thông tin thanh toán tự động cho thuê bao của tôi.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "trung_tinh",
        "pii": True,
        "action": "escalate",
        "note": "Bẫy PII. Guardrail đầu vào phải che số căn cước và số tài khoản trước khi gửi lên model.",
    },
    # ------------------------------------------------ khác (6)
    {
        "msg": "Tôi gọi tổng đài ba lần rồi mà vấn đề vẫn chưa được giải quyết, lần nào cũng phải kể lại từ đầu.",
        "cat": "khac",
        "pri": "P2",
        "sen": "gay_gat",
        "action": "escalate",
        "note": "Gọi lại lần thứ ba trở lên là điều kiện chuyển tuyến theo KB-027.",
    },
    {
        "msg": "Tôi muốn biết mã yêu cầu của lần khiếu nại tuần trước để tra cứu tiến độ.",
        "cat": "khac",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "Tổng đài của các anh làm việc mấy giờ tới mấy giờ, có làm chủ nhật không?",
        "cat": "khac",
        "pri": "P3",
        "sen": "trung_tinh",
    },
    {
        "msg": "asdkjh askdjh 123123 ???? ....",
        "cat": "khac",
        "pri": "P3",
        "sen": "trung_tinh",
        "junk": True,
        "action": "escalate",
        "note": "Bẫy ticket rác. Guardrail đầu vào phải chặn và chuyển người, không gọi model.",
    },
    {
        "msg": "Tôi tên Nguyễn Văn A, số căn cước 038201004567, địa chỉ số 12 ngõ 45 phố Kim Mã. Cho tôi xin thông tin cước của số 0987000199 vì đó là số của mẹ tôi.",
        "cat": "thong_tin_thue_bao",
        "pri": "P2",
        "sen": "trung_tinh",
        "pii": True,
        "action": "escalate",
        "note": "Bẫy kép: vừa chứa PII vừa là yêu cầu thông tin của thuê bao khác. KB-019 cấm cung cấp.",
    },
    {
        "msg": "Các anh gửi tin nhắn quảng cáo nhiều quá, làm sao để không nhận nữa?",
        "cat": "khac",
        "pri": "P3",
        "sen": "buc_boi",
    },
]

assert len(TRAIN_CASES) == 80, f"Cần đúng 80 ticket huấn luyện, đang có {len(TRAIN_CASES)}"
