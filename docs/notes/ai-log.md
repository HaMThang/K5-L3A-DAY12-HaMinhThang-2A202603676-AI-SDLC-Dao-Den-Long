# Nhật ký AI

## Phase 1

- Công cụ: Codex (model GPT-6); mục tiêu: đọc yêu cầu, hiện thực mô phỏng Python, WebGL và Test Contract.
- Lỗi/giới hạn phát hiện: công cụ web không đọc được Claude artifact; trình duyệt tự động báo host không khả dụng. Đã dùng bản PRD-0/Test Contract v1.0 trong `HUONG_DAN_CHI_TIET.md` và ghi rõ nguồn.
- Harness cập nhật: `AGENTS.md` có lệnh build, chạy, test, headless thực tế; logic tách khỏi render.
- Token/chi phí: giao diện phiên không cung cấp số token/chi phí chính xác, nên chưa ước tính số liệu để tránh ghi sai.
- Tiết kiệm token: dùng thư viện chuẩn Python, một module gameplay dùng chung cho browser và headless.

## Phase 2

- Công cụ: Codex; đọc Ticket-02 trực tiếp trong Chrome qua giao diện trợ năng do web fetch không mở được Claude artifact.
- Mục tiêu: thay số Phase 1 bằng chuẩn v1.1, thêm ba bản đồ, dash/pause/charm/drifter, màn chơi và test.
- Sai sót phát hiện trong quá trình làm: ánh xạ E trùng xoay camera; chuyển xoay phải sang R và thêm chuột. Resume pause cần nhả cạnh phím trước khi gửi `pause:true`; đã sửa.
- Harness: cập nhật `AGENTS.md`, thêm `tests/test_phase2.py`; vẫn không dùng phụ thuộc ngoài Python chuẩn.
- Token/chi phí: phiên không cung cấp số đếm chính xác, nên không ghi ước tính giả.
