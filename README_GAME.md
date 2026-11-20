# Hướng dẫn chơi Đảo Đèn Lồng — Phase 2

## Cài đặt và chạy

Cần Python 3.10+ và trình duyệt hỗ trợ WebGL. Không cần gói Python ngoài. Trên macOS/Linux:

```bash
python3 -m compileall -q src
python3 -m src.server
```

Mở **đúng địa chỉ in trong terminal**; server tự chọn một cổng trống mỗi lần chạy. Giữ terminal chạy trong lúc chơi. Có thể chọn cổng cụ thể bằng `python3 -m src.server --port 9000` nếu cổng đó không bị chiếm. Trên Windows thay `python3` bằng `python`.

## Điều khiển

| Phím | Tác dụng |
|---|---|
| W/A/S/D | Di chuyển theo hướng camera |
| Q/R hoặc rê chuột sau khi bấm vào game | Xoay camera |
| Space | Nhảy |
| Shift | Lướt |
| E | Nạp đom đóm vào đèn gần nhất |
| J | Tỏa Sáng xua Bóng Mực và Gió Lạc |
| P hoặc Esc | Tạm dừng |
| F9 | Mở console admin; nhập `map 1`, `map 2` hoặc `map 3` để chọn bản đồ trực tiếp |

Thu thập đom đóm vàng; mỗi Đèn Lồng Lớn cần 10 đom đóm và có thể nạp nhiều lần. Thắp đủ đèn trước bình minh để qua Đêm tiếp theo. Mây có 3 Ngọn Lửa mỗi Đêm; mất hết sẽ thua. Đêm 2 có Gió Lạc cướp đom đóm và Bùa Gió tăng tốc; Đêm 3 có tầng đảo và gió mạnh. Menu có chơi lại Đêm, cài đặt âm lượng/độ nhạy chuột và về menu.

Ở Đêm 3, Mây bắt đầu trên tầng cao cạnh tháp chuông. Bục nhảy có bán kính kích hoạt 0,5 m; chân tháp là vật cản, không thể đi xuyên vào bên dưới. Đèn hiện thanh nhiên liệu; khi dầu dưới 30, đèn và thanh nhấp nháy. Trong **Cài đặt**, bật **Bảng màu dễ phân biệt** để đổi mắt/viền Bóng Mực sang xanh lam và cảnh báo sang trắng kèm biểu tượng ⚠.

Môi trường có cỏ, hoa dại và hai ngôi nhà gỗ mỗi bản đồ. Đảo Chuông có cụm núi đá cao quanh các tầng; vùng chân núi có va chạm. Mây dùng model Archangel Artamiel từ gói người dùng cung cấp, đứng theo trục Y, đội nón lá và tự phát sáng.

## Kiểm tra

```bash
python3 -m unittest discover -s tests -v
python3 -m src.headless --seed 1 --night 2 --ticks 60 --out result.jsonl
```

`result.jsonl` chứa snapshot tick 0, các snapshot tiếp theo, event và dòng `end`. Lệnh đầy đủ:

```text
python3 -m src.headless --seed <int> --night 1|2|3 [--scenario <file.json>] [--inputs <file.json>] --ticks <int> --out <file.jsonl> [--snapshot-every <int>]
```

Định dạng Phase 1 xem [Test Contract trong hướng dẫn lab](HUONG_DAN_CHI_TIET.md); phần mở rộng v1.1 xem [spec Phase 2](docs/notes/phase-2.md) và [lab board](https://claude.ai/artifact/Q1RYyv1dxjUczzCbd2ZnoW). Logic gameplay nằm trong `src/game_v2.py` và được cả server lẫn headless dùng chung. `game.contract.json` là nguồn thông số.

## Thông số Phase 2 chuẩn

Tốc độ Mây 6 m/s; sức chứa 10; mỗi đèn cần 10; nhặt trong 1 m, tương tác trong 2 m. Tỏa Sáng tốn 3 đom đóm, bán kính 5 m, choáng Bóng Mực 120 tick, đẩy 4 m trong 15 tick, hồi 3 giây. Lướt 14 m/s trong 0,2 giây, hồi 1,5 giây. Đêm dài 300/330/360 giây. Bóng Mực chạy 4 m/s (Đêm 3: 4,5), vùng an toàn đèn 6 m. Các giá trị còn lại nằm trong `game.contract.json` và [spec Phase 2](docs/notes/phase-2.md).

## Sáng tạo của tôi

Mái đèn thay màu theo trạng thái và các đom đóm nhấp nhô khi hiển thị. Chuyển động nhấp nhô chỉ nằm ở phần WebGL, không tác động mô phỏng headless. Bằng chứng logic và tính tất định: `docs/proof/phase-2.md`.

## Giới hạn hiện tại

Đồ họa 3D được dựng bằng hình khối WebGL đơn giản. Giao diện chơi cần trình duyệt hỗ trợ WebGL; lệnh headless không cần GPU. Số FPS được hiện ở cuối HUD để người chơi đo tại 1280×720.
