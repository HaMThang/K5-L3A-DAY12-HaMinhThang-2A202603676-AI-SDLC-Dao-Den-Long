# Phase 2 — Ticket-02 “Ba hòn đảo”

Nguồn: [lab board Phase 2](https://claude.ai/artifact/Q1RYyv1dxjUczzCbd2ZnoW#p2), đọc trực tiếp ngày 2026-11-20. Contract v1.1 thay các số Phase 1 tự chọn. `game.contract.json` khai báo các số chuẩn; `src/game_v2.py` là mô phỏng dùng chung cho browser và headless.

## Acceptance criteria

| Mục Ticket-02 | Tiêu chí kiểm tra |
|---|---|
| Số chuẩn | Snapshot và scenario thể hiện chạy 6 m/s, 10 đom đóm tối đa, 10/đèn, tương tác 2 m, pulse 3/5 m/3 s, dash 14 m/s trong 12 tick và hồi 90 tick; điểm chỉ cộng khi nạp, thắp, choáng và thắng. |
| Bản đồ | Night 1 có 5 đèn theo tọa độ chuẩn; Night 2 có 2 đảo và cầu với 6 đèn; Night 3 có 3 tầng và 7 đèn. |
| Gió Lạc | Night 2/3 sinh ở tick 1200; khi Mây mang ≥5 và trong 15 m thì chase; chạm cướp tối đa 3; pulse làm flee hoặc thả đồ. |
| Bùa Gió | Nhặt trong 1 m, hiệu lực 600 tick, tốc độ 7,2 m/s, lướt không hồi chiêu; hồi sinh sau 2700 tick. |
| Chuỗi ba Đêm | Menu → giới thiệu → chơi → kết quả → Đêm kế; thắng Đêm 3 hiện Bình Minh và tổng điểm; thua được thử lại Đêm đó. |
| Tạm dừng | P/Esc phát event, tick tăng trong khi sim_tick và timer đứng yên; giao diện có Tiếp tục, Chơi lại, Cài đặt, Về menu. |
| Cài đặt | Âm lượng và độ nhạy chuột được lưu bằng localStorage. |
| Âm thanh | Có nhạc nền tổng hợp và âm báo cho tương tác/hành động chính; đếm ngược 10 giây cuối. |
| HUD | Ngọn Lửa, đồng hồ mm:ss, đèn và điểm, 10 ô đom đóm, cooldown, gợi ý E gần đèn và mũi tên đến đèn ngoài góc nhìn. |
| Màu và sáng | Màu giao diện/thực thể theo bảng chuẩn; ambient = 0,15 + 0,55 × tỉ lệ đèn sáng. |
| Contract v1.1 | `--night 1|2|3`, snapshot thêm night/wind/vel/cooldown/motes/drifters/charms; scenario và input mới; JSONL deterministic; 21.600 tick ≤ 30 giây. |
| Hiệu năng bản thường | Cần đo FPS thực tế ở 1280×720, mục tiêu trung bình ≥30. |

## Thay đổi giả định Phase 1

Ticket-02 ghi rõ “thay mọi giá trị bạn tự chọn”. Vì vậy, các test Phase 1 được cập nhật **chỉ tại kỳ vọng đã bị ticket thay thế**: chi phí thắp/xung, điểm nhặt (từ +10 thành 0), số đom đóm rơi (từ làm tròn lên thành `floor`), quãng đẩy xung (từ tức thời sang 15 tick). Các test vẫn kiểm tra hành vi thật, không bị bỏ.

## Quyết định và giới hạn

- Điểm đom đóm ban đầu là 20 điểm đầu trong danh sách điểm sinh chuẩn; các điểm còn lại dành cho spawn sau.
- Bóng Mực trong scenario mặc định ở trạng thái `chase` để kiểm tra tiếp xúc tức thời; Bóng sinh theo lịch ở trạng thái `wander`.
- Gió Lạc idle bay theo quỹ đạo chậm xác định bằng `sim_tick`. Mọi RNG dùng seed của mô phỏng.
- Giao diện 3D dùng hình khối tự tạo; âm thanh tổng hợp bằng WebAudio, không dùng asset ngoài.
- Mô phỏng đêm 3 có hình học cơ bản của tầng/dốc/tháp. Chưa có test đo FPS trực tiếp 1280×720; HUD hiển thị FPS để người dùng xác nhận.
- Console kiểm thử local: F9, lệnh `map 1|2|3`. Luồng menu thường vẫn chỉ bắt đầu Đêm 1 và mở đêm kế tiếp sau chiến thắng. Đây là tiện ích kiểm thử của bản chạy local, chưa có xác thực tài khoản admin.
- Yêu cầu bổ sung: Mây bắt đầu Đêm 3 tại (0,6,5), trên tầng cao cạnh tháp; bục nhảy bán kính 0,5 m; tháp trụ bán kính 2 m, cao 8 m chặn chuyển động từ mọi phía ở dưới đỉnh. Nhân vật dùng mesh cầu/nón và tháp mesh trụ để tăng độ rõ hình khối 3D.
