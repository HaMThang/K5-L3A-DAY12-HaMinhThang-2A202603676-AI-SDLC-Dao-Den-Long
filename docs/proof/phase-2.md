# Bằng chứng Phase 2

Ngày: 2026-11-20. Windows, Python 3.12.10. Mã chưa gắn tag khi ghi.

| Hạng mục | Lệnh / kiểm tra | Kết quả |
|---|---|---|
| Regression Phase 1 và tính năng mới | `python -m unittest discover -s tests -v` | 13/13 test đạt; 7 Phase 1 + 6 Phase 2 |
| Headless Night 2 | `python -m src.headless --seed 1 --night 2 --ticks 1201 --out docs/proof/phase-2-night2.jsonl` | Exit 0; [JSONL](phase-2-night2.jsonl) |
| Headless Night 3 | `python -m src.headless --seed 1 --night 3 --ticks 1801 --out docs/proof/phase-2-night3.jsonl` | Exit 0; [JSONL](phase-2-night3.jsonl) |
| Tốc độ headless Night 3 | `python -m src.headless --seed 17 --night 3 --ticks 21600 --out docs/proof/phase-2-benchmark.jsonl` | 0,778 giây (Measure-Command); `end` ticks 21600, state lost |
| HTTP game | GET `/`, POST `/start` Night 2, POST `/step` dash, POST `/restart` | HTTP 200; Night 2 mở, event `dash`, restart giữ Night 2 |
| Giao diện Chrome | Mở trang local trong Chrome | Trang có canvas và điều khiển; chưa có số đo FPS ở 1280×720 vì hộp thoại ứng dụng khác che giao diện lúc kiểm tra |

Kết quả 13 test đến từ lần chạy thực tế. Không suy diễn FPS từ tốc độ headless: hai chỉ số đo những thứ khác nhau.
