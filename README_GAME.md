# Hướng dẫn chơi Đảo Đèn Lồng — Phase 1

## Cài đặt và chạy

Cần Python 3.10+ và trình duyệt hỗ trợ WebGL. Không cần gói Python ngoài. Trên macOS/Linux:

```bash
python3 -m compileall -q src
python3 -m src.server
```

Mở `http://127.0.0.1:8000`. Trên Windows thay `python3` bằng `python`.

## Điều khiển

| Phím | Tác dụng |
|---|---|
| W/A/S/D | Di chuyển theo hướng camera |
| Q/E | Xoay camera |
| Space | Nhảy |
| F | Nạp đom đóm vào đèn gần nhất |
| J | Phát xung xua Bóng Mực |

Thu thập đom đóm vàng; mỗi Đèn Lồng Lớn cần 3 đom đóm. Thắp đủ 5 đèn trước bình minh để thắng. Mây có 3 ngọn lửa; mất hết sẽ thua. Sau khi kết thúc, bấm **Chơi lại**.

## Kiểm tra

```bash
python3 -m unittest discover -s tests -v
python3 -m src.headless --seed 1 --night 1 --ticks 60 --out result.jsonl
```

`result.jsonl` chứa snapshot tick 0, các snapshot tiếp theo, event và dòng `end`. Lệnh đầy đủ:

```text
python3 -m src.headless --seed <int> --night 1 [--scenario <file.json>] [--inputs <file.json>] --ticks <int> --out <file.jsonl> [--snapshot-every <int>]
```

Định dạng scenario/inputs và output xem [Test Contract trong hướng dẫn lab](HUONG_DAN_CHI_TIET.md). Logic gameplay nằm trong `src/game.py` và được cả server lẫn headless dùng chung. `game.contract.json` là nguồn thông số.

## Thông số Phase 1 tự chọn

Tốc độ Mây 4 m/s; mang tối đa 6 đom đóm; mỗi đèn cần 3; nhặt trong 1 m, tương tác trong 2,2 m. Xung tốn 2 đom đóm, bán kính 5 m, choáng 2 giây, đẩy 3 m, hồi 1 giây. Đêm dài 300 giây; Mây có 3 ngọn lửa, bất tử 1,5 giây sau khi bị chạm, làm rơi 50% số đom đóm đang mang (làm tròn lên). Bóng Mực chạy 1,6 m/s, chạm trong 0,8 m, tránh vùng 3 m quanh đèn đã sáng. Không có phạt rơi khỏi đảo; bờ đảo chặn người chơi. Các giá trị điểm nằm trong `game.contract.json`.

## Sáng tạo của tôi

Đảo có hình tròn, mái đèn thay màu theo trạng thái và các đom đóm nhấp nhô khi hiển thị. Chuyển động nhấp nhô chỉ nằm ở phần WebGL, không tác động mô phỏng headless. Bằng chứng logic và tính tất định: `docs/proof/phase-1.md`.

## Giới hạn hiện tại

Đồ họa 3D được dựng bằng hình khối WebGL đơn giản. Giao diện chơi cần trình duyệt hỗ trợ WebGL; lệnh headless không cần GPU. Chưa kiểm tra hình ảnh trực tiếp trên máy này do trình duyệt tự động không khả dụng.
