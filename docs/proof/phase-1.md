# Bằng chứng Phase 1

Ngày kiểm tra: 2026-11-20. Môi trường: Windows, Python 3.12.10. Mã chưa được commit/tag tại thời điểm ghi.

| Yêu cầu | Lệnh/kiểm tra | Kết quả |
|---|---|---|
| Python hợp lệ | `python -m compileall -q src` | Exit 0 |
| Nhặt ở biên, nạp và thắng, pulse, hit/bất tử, dawn, di chuyển/nhảy, hết máu | `python -m unittest discover -s tests -v` | 7 test, OK |
| JSONL deterministic và input lỗi | Test `test_cli_determinism_and_bad_input` chạy CLI 2 lần và so byte, rồi thử JSON lỗi | Output bằng nhau; JSON lỗi exit 2 |
| Chạy headless mẫu | `python -m src.headless --seed 1 --night 1 --ticks 60 --out docs/proof/phase-1-sample.jsonl` | Exit 0; snapshot tick 0, tick 10…60 và `end` ticks 60; [output](phase-1-sample.jsonl) |
| HTTP phục vụ giao diện và bước mô phỏng | Khởi tạo `ThreadingHTTPServer` trong cùng process, gửi GET `/` và POST `/step` bằng `urllib.request` | GET 200 (8480 byte), POST 200, snapshot tick 1 |
| Sửa lỗi không mở được trang | Phát hiện nhiều tiến trình lắng nghe cổng 8000; đổi server sang cổng trống tự chọn. Chạy `python -m src.server`, nhận `http://127.0.0.1:61453`, sau đó gọi GET `/` và POST `/step` từ tiến trình khác | GET 200 (8448 ký tự), POST 200, snapshot tick 1, state `playing` |
| WebGL/HUD và thao tác chơi | Chưa xem trực tiếp | Chưa xác nhận vì browser access host không khả dụng |

Test Contract đối chiếu theo bản trong `HUONG_DAN_CHI_TIET.md`. Artifact Claude gốc chưa truy cập được trong phiên này. Không dùng bằng chứng đồ họa giả định.
