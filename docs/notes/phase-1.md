# Phase 1 — PRD-0

## Nguồn và phạm vi

Nguồn trực tiếp là bản tóm chi tiết PRD-0 và Test Contract v1.0 trong `HUONG_DAN_CHI_TIET.md`, mục Phase 1. Artifact Claude được liên kết trong README nhưng công cụ web và trình duyệt tự động của phiên này không mở được, nên chưa thể đối chiếu trực tiếp. Không giả định nội dung Phase 2–4.

## Tiêu chí nghiệm thu

| Yêu cầu | Kiểm chứng |
|---|---|
| Đêm 1 có đảo tròn và 5 đèn | Quan sát WebGL; snapshot có L1–L5 |
| Mây đi, nhảy, camera góc ba | Điều khiển trong browser; snapshot thay đổi vị trí |
| Nhặt, nạp và thắp đèn | Test pickup/deposit/win, event JSONL |
| Bóng Mực đuổi, gây sát thương; xung đẩy và choáng | Test hit/pulse; kiểm tra snapshot |
| Thắng/thua, điểm, chơi lại | Test win/dawn, browser restart |
| Test Contract v1.0 | CLI, schema JSONL, determinism, lỗi mã 2 |

## Giả định thiết kế

- Mọi con số không được PRD quy định lấy từ `game.contract.json`; xem `README_GAME.md` để hiểu ý nghĩa. Không coi chúng là yêu cầu gốc.
- Mỗi đèn cần 3 đom đóm; một lần nhấn F nạp tối đa lượng còn thiếu, đồng thời thắp khi đủ.
- Xung tiêu hao đom đóm đang mang, không tiêu hao ngọn lửa sinh mệnh.
- Người chơi không thể ra khỏi mép đảo; vì vậy `fall_enabled=false` và không có sự kiện `player_hit` do rơi.
- Nhảy chỉ thay đổi độ cao hiển thị/vị trí Y; các bán kính gameplay tính trên XZ như contract.
- Mote mặc định bố trí quanh tâm; bóng mặc định bắt đầu ở mép đảo. Scenario thay thế danh sách khi có `motes`/`shades`. `random_*: false` với danh sách vắng mặt tạo danh sách rỗng.
- Điểm thắng cộng phần thời gian còn lại làm tròn xuống và số ngọn lửa còn lại; scenario dựng sẵn không sinh điểm hoặc event.

## Đánh giá

Các test tự động cốt lõi đạt (xem `docs/proof/phase-1.md`). Giao diện chưa được kiểm chứng bằng quan sát trực tiếp trên máy này vì trình duyệt tự động không khả dụng. Việc mở artifact gốc cũng chưa thành công; cần đối chiếu khi môi trường truy cập được.
