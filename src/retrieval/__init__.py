"""Retrieval Engineering — tìm đúng thông tin, đúng thời điểm, cho đúng tác vụ (slide 9, 37–44).

Các module đi theo pha runtime của RAG Pipeline (slide 39):

* ``transform`` — Query Transformation: viết lại truy vấn.
* ``search``    — Retrieve: keyword, semantic, hybrid (slide 40).
* ``filters``   — Filter: lọc siêu dữ liệu và quyết định đủ căn cứ.
* ``rerank``    — Rerank: xếp hạng lại.
* ``pipeline``  — ghép các bước trên thành ``Retriever``.
"""
