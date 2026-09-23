"""Kho prompt có phiên bản — SPEC-PROMPT-02.

Prompt là dữ liệu, không phải code. Chúng nằm ở đây dưới dạng tệp Markdown có
front-matter, được nạp bằng ``loader.load_prompt``, và **không bao giờ được
viết thẳng trong mã Python**. Lý do rất cụ thể: Session 3 bước 4 yêu cầu so
sánh hai phiên bản prompt trên cùng bộ ca kiểm thử, và Session 6 yêu cầu chứng
minh cải tiến bằng bảng trước–sau. Cả hai đều bất khả thi nếu prompt bị trộn
vào logic.
"""
