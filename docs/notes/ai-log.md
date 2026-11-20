# Nhật ký AI

## Phase 1

- Công cụ: Codex (model GPT-6); mục tiêu: đọc yêu cầu, hiện thực mô phỏng Python, WebGL và Test Contract.
- Lỗi/giới hạn phát hiện: công cụ web không đọc được Claude artifact; trình duyệt tự động báo host không khả dụng. Đã dùng bản PRD-0/Test Contract v1.0 trong `HUONG_DAN_CHI_TIET.md` và ghi rõ nguồn.
- Harness cập nhật: `AGENTS.md` có lệnh build, chạy, test, headless thực tế; logic tách khỏi render.
- Token/chi phí: giao diện phiên không cung cấp số token/chi phí chính xác, nên chưa ước tính số liệu để tránh ghi sai.
- Tiết kiệm token: dùng thư viện chuẩn Python, một module gameplay dùng chung cho browser và headless.
