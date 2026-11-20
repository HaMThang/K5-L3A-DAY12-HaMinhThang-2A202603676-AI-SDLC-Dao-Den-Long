# Hướng dẫn chi tiết: Lab Đảo Đèn Lồng

Tài liệu này tóm tắt mục tiêu lab và biến [bài lab](README.md) thành một quy trình thực hiện cụ thể.

Tài liệu liên quan:

- [Mục tiêu và tổng quan](README.md)
- [Bảng tự kiểm checkpoint](CHECKPOINTS.md)
- [Quy trình làm với AI](GUIDE.md)
- [Quy định bắt buộc](RULES.md)
- [Cách chấm điểm](RUBRIC.md)
- [Cách nộp và release](SUBMISSION.md)

Yêu cầu chi tiết của từng phase chỉ lấy từ [Lab board Đảo Đèn Lồng](https://claude.ai/artifact/Q1RYyv1dxjUczzCbd2ZnoW). Nội dung lab board khi phase phát hành là nguồn xác thực cuối cùng.

## 1. Tóm tắt lab

Bạn làm **một mình** một game 3D góc nhìn thứ ba có tên Đảo Đèn Lồng trong vòng 4 giờ:

- Người chơi điều khiển nhân vật thu gom đom đóm để thắp lại Đèn Lồng Lớn.
- Người chơi né Bóng Mực trong sương đen.
- Có thể sáng tạo thêm nhân vật, cơ chế, câu chuyện, hiệu ứng hoặc âm thanh nếu không phá yêu cầu cốt lõi.
- Không bắt buộc engine hay ngôn ngữ. Sản phẩm phải chạy trên macOS hoặc Linux.
- Mỗi phase nhận thêm hoặc thay đổi yêu cầu. Mục tiêu là sản phẩm đúng yêu cầu và có bằng chứng, không phải đồ họa phức tạp.
- Mỗi thay đổi phải giữ được hoặc kiểm chứng lại phần đã làm trước đó.

Bạn nộp một repo GitHub cá nhân, public, gồm mã nguồn, tag 4 phase, Release `v1.0.0`, video demo, bằng chứng, harness AI và ghi chép retro.

## 2. Timeline bắt buộc

| Thời điểm | Việc phát hành | Hạn hành động |
|---|---|---|
| 0h | Phase 1: PRD-0 và Test Contract | Trước 1h: gắn tag `phase-1` |
| 1h | Phase 2: Ticket-02 | Trước 2h: gắn tag `phase-2` |
| 2h | Phase 3: Ticket-03 | Trước 2h30: gắn tag `phase-3` |
| 2h30 | Phase 4: Ticket-04 | Trước 4h: gắn tag `phase-4`, tạo Release `v1.0.0` và video |
| 4h | Kết thúc lab | Chỉ nộp link; không commit thêm nội dung sản phẩm |

Hết thời gian của một phase, hãy gắn tag và chuyển sang phase tiếp theo dù bài chưa hoàn hảo. Ghi trung thực phần chưa đạt thay vì giả vờ đã hoàn thành.

## 3. Chuẩn bị trước lab

### Bước 3.1: Tạo repo cá nhân

Tên repo theo quy ước:

```text
K5-<L3A hoặc L3B>-DAY12-<HoVaTen>-<MSSV>-AI-SDLC-Dao-Den-Long
```

Ví dụ:

```text
K5-L3A-DAY12-NguyenVanA-2A2026xxxxx-AI-SDLC-Dao-Den-Long
```

Repo phải ở chế độ public.

### Bước 3.2: Chuẩn bị môi trường

- Cài engine, runtime hoặc package manager đã chọn.
- Cài Git và công cụ quay/chụp màn hình.
- Cài công cụ AI có thể truy cập repo.
- Cài công cụ chạy test; cài Docker nếu engine cần.
- Thử build và chạy một chương trình 3D hoặc headless tối thiểu.
- Đăng nhập lab board và xác nhận tab Phase 1 hoạt động.

Lệnh kiểm tra Git cơ bản:

```bash
git --version
git status
git remote -v
```

### Bước 3.3: Tạo cấu trúc bắt đầu

Cấu trúc gợi ý:

```text
README.md
LICENSE
CREDITS.md
AGENTS.md
src/
tests/
docs/
  notes/
  proof/
  demo/
.env.example
.gitignore
```

Cấu trúc không bắt buộc; người chấm chỉ cần tìm được mã nguồn, bằng chứng, harness và ghi chép.

### Bước 3.4: Không commit dữ liệu nhạy cảm

- Không commit API key, token hoặc file `.env`.
- Chỉ commit `.env.example` với các khóa mẫu.
- Không dán khóa vào README, commit message, issue hoặc chat công khai.
- Nếu đã lỡ commit khóa: thu hồi khóa ngay trước khi dọn lịch sử và push lại.

## 4. Vòng làm việc cho mỗi phase

Thực hiện lặp lại bảy bước sau.

### Bước 4.1: Đọc và tách yêu cầu

Đọc tài liệu của phase ít nhất hai lần:

1. Lần một: nắm mục tiêu chơi được.
2. Lần hai: gạch chân yêu cầu bắt buộc, con số, tên lệnh, định dạng đầu ra và nội dung Test Contract.

Chia yêu cầu thành hai nhóm:

- Yêu cầu bắt buộc.
- Chỗ mơ hồ cần tự giả định.

Ví dụ ghi quyết định:

```markdown
## Giả định - Phase 1

- Vùng sương mờ theo toạ độ X, Y, Z được quy định trong contract.
- Tốc độ nhân vật, bán kính gom đom đóm và luật thua đều lấy giá trị tự chọn
  nếu ticket không nêu; ghi rõ giá trị trong cấu hình.
- Thứ tự seed cố định được dùng để chạy lại cùng kịch bản.
```

Nếu lab board nói "chưa được quy định", hãy ghi giả định hợp lý thay vì tự suy ra rằng nó là yêu cầu bắt buộc.

### Bước 4.2: Viết tiêu chí nghiệm thu

Mỗi yêu cầu chính phải có câu kiểm tra được. Mẫu:

```text
Cho đầu vào X, chương trình phải Xử lý Y và xuất Z.
```

Trước code, lập một bảng:

| Yêu cầu | Cách kiểm chứng | Bằng chứng dự kiến | Kết quả |
|---|---|---|---|
| Có chế độ headless | Chạy đúng lệnh contract | Output JSON/log | Chưa/Đạt |
| Không hỏng phase trước | Chạy test hồi quy | Báo cáo test | Chưa/Đạt |
| Đạt số đo | Chạy benchmark | FPS hoặc thời gian thực thi | Chưa/Đạt |

### Bước 4.3: Lập kế hoạch với agent

Giao cho agent một prompt ngắn có đủ:

- Yêu cầu bắt buộc.
- Giả định đã ghi.
- Cách kiểm chứng cần qua.
- Các file được phép sửa.
- Quy tắc commit và quy tắc không sửa test để ép kết quả.
- Tiêu chí dừng: dừng khi test đỏ hoặc khi phát hiện yêu cầu mơ hồ.

Yêu cầu agent lập kế hoạch và đợi bạn duyệt trước khi code. Với thay đổi lớn, ghi lý do một dòng.

### Bước 4.4: Thiết kế hợp chế độ headless

Đọc Test Contract trước khi chọn kiến trúc.

- Tách logic game khỏi phần render và điều khiển cửa sổ.
- Cho đầu vào và seed đi qua lệnh headless cố định.
- Xuất đầu ra đúng schema và thứ tự yêu cầu.
- Không phụ thuộc thời gian thực để test khi contract yêu cầu tính tất định.
- Tự tạo vài scenario nhỏ trước rồi tự chạy.

Nếu contract thay đổi ở phase sau, cập nhật code và scenario, sau đó chạy lại các test còn hiệu lực.

### Bước 4.5: Xây dựng theo commit nhỏ

- Làm từng việc nhỏ: khung project, contract, logic, HUD, asset, đo hiệu năng.
- Mỗi commit nên làm một mục rõ ràng.
- Xem diff sau khi agent sửa code.
- Không để agent tự sửa test để che lỗi.
- Khi agent sai, sửa harness hoặc quy tắc kiểm tra ở vị trí gần lỗi nhất thay vì chỉ nhắc bằng lời.

Ví dụ thông điệp commit:

```text
feat: add headless lantern scene runner
test: add deterministic spawn scenarios
docs: document phase 1 assumptions
```

### Bước 4.6: Kiểm chứng thật

Chạy ít nhất:

- Test hoặc lệnh của repo.
- Chế độ headless theo Test Contract.
- Một test hồi quy phần phase trước.
- Chạy game trực tiếp để xem giao diện và điều khiển.
- Hai lần chạy cùng seed nếu yêu cầu tính tất định.
- Benchmark nếu ticket yêu cầu số đo.

Kết quả cần lưu vào `docs/proof/` hoặc thư mục bằng chứng tương đương.

Mỗi bằng chứng cần ghi:

- Yêu cầu nó chứng minh.
- Lệnh đã chạy.
- Commit hoặc tag.
- Kết quả đầu ra.
- Cấu hình máy nếu đo hiệu năng.
- Phần chưa đạt và lý do.

Không sửa output test bằng tay. Không viết test chỉ để luôn đạt. Không ghi đạt khi chưa chạy.

### Bước 4.7: Evaluation và phát hành

Cuối mỗi phase:

- Đánh giá yêu cầu đã đạt, chưa đạt và phần cũ có hỏng không.
- Ghi lỗi của AI đã phát hiện.
- Ghi thay đổi harness giúp tránh lỗi lặp.
- Ước tính token hoặc chi phí đã dùng.
- Cập nhật README và ghi chép.
- Gắn tag, push và xác nhận tag trỏ đúng commit.

## 5. Thực hiện từng phase

### Phase 1: PRD-0

Trong khoảng 60 phút:

1. Chuẩn bị repo, engine và công cụ trong khoảng 10 phút.
2. Đọc PRD-0 và Test Contract.
3. Ghi giả định vào `docs/notes/phase-1.md`.
4. Viết tiêu chí nghiệm thu.
5. Xây bản màn đầu tiên có thể chạy.
6. Tách logic để chạy headless.
7. Viết test/scenario tối thiểu.
8. Chạy test và lưu bằng chứng.
9. Cập nhật README.
10. Gắn `phase-1`, push và xác nhận.

Tag tối thiểu là mục tiêu. Chỉ tiếp tục Phase 2 nếu đã lưu đủ bằng chứng để biết phần nào đạt.

#### Yêu cầu cụ thể đã công bố trên Lab board

Lab board hiện công bố Phase 1; các tab Phase 2–4 đang khóa cho đến mốc phát hành. Vì vậy, phần dưới đây chỉ chi tiết hóa PRD-0 và Test Contract v1.0, không suy đoán nội dung ticket sau.

**Lõi trò chơi Phase 1:**

- Làm màn **Đêm 1 – Đảo Bến**, đảo tròn với đúng **5 Đèn Lồng Lớn**.
- Điều khiển Mây đi lại và nhảy trong môi trường 3D có camera.
- Thu thập đom đóm, mang ánh sáng đến đèn và tương tác để thắp đèn.
- Bóng Mực xuất hiện, đuổi theo Mây; khi chạm thì Mây mất máu.
- Mây có thể tiêu hao ánh sáng để phát xung xua Bóng Mực; Bóng Mực sợ đèn.
- Thắp đủ đèn thì thắng; hết máu thì thua. Có điểm số và HUD, có thể chơi lại sau khi kết thúc.
- Phong cách đêm, ấm áp, cổ tích; đảo sáng dần, ánh sáng vàng cam tốt, tím đen nguy hiểm. Mây đội nón lá có đèn lồng nhỏ; không bạo lực, không máu me.
- Các số chưa được PRD quy định (ví dụ tốc độ, lượng máu, thời lượng đêm, điểm) là quyết định thiết kế của bạn. Ghi rõ trong cấu hình, contract và README; không coi giả định là yêu cầu gốc.

**Tệp `game.contract.json` ở thư mục gốc** phải khai báo `contract_version`, `team`, `build_cmd`, `run_cmd`, `headless_cmd` và các thông số game. `tuning` phải phản ánh đúng giá trị thực tế trong game, không phải giá trị mong muốn:

```json
{
  "contract_version": "1.0",
  "team": "mssv-ho-ten",
  "build_cmd": "lệnh cài đặt/biên dịch",
  "run_cmd": "lệnh mở game có giao diện",
  "headless_cmd": "lệnh chạy headless",
  "tuning": {
    "player_speed": 0,
    "carry_capacity": 0,
    "lantern_cost": 0,
    "lantern_count_night1": 5,
    "pickup_radius": 0,
    "interact_radius": 0,
    "pulse_cost": 0,
    "pulse_radius": 0,
    "night1_duration_s": 0,
    "flames": 0,
    "invuln_s": 0,
    "hit_drop_ratio": 0,
    "pulse_stun_s": 0,
    "pulse_push_m": 0,
    "pulse_cooldown_s": 0,
    "safe_radius": 0,
    "shade_speed": 0,
    "shade_hit_radius": 0,
    "fall_enabled": false,
    "score": {
      "per_mote": 0,
      "per_lantern": 0,
      "per_stun": 0,
      "per_second_left": 0,
      "per_flame_left": 0
    }
  }
}
```

Điền các số 0 bằng thông số thực tế. Nếu game không có một khái niệm thì dùng `null` hoặc `false` theo kiểu dữ liệu phù hợp, và giải thích trong README. `hit_drop_ratio` là tỉ lệ đom đóm rơi khi bị đánh (0 nghĩa là không rơi); `safe_radius` là vùng quanh đèn Bóng Mực không thể vào; `fall_enabled` cho biết rơi khỏi đảo có bị phạt không; `score.*` là điểm được cộng cho từng sự kiện. Các lệnh build và chạy phải dùng được trên macOS/Linux; Docker hoặc bản web được chấp nhận nếu bạn phát triển trên Windows.

**Lệnh headless theo contract** (tham số được nối vào `headless_cmd`):

```text
<headless_cmd> --seed <int> --night 1 [--scenario <file.json>] [--inputs <file.json>] --ticks <int> --out <file.jsonl> [--snapshot-every <int>]
```

Quy tắc thực thi:

- Mô phỏng chạy ở **60 tick/giây cố định**, không mở cửa sổ, không cần GPU và chạy nhanh nhất có thể.
- Dừng khi đủ `--ticks` hoặc khi thắng/thua. Thành công thoát mã 0; lỗi thoát mã khác 0 và ghi lỗi ra stderr. Scenario/inputs sai định dạng phải thoát mã 2.
- Đơn vị chiều dài là mét; Y hướng lên; mặt đất ở Y=0; vị trí ban đầu của người chơi là `(0,0,0)`.
- Snapshot tick 0 là trạng thái sau khi dựng scenario và trước khi áp dụng input. Bước thứ `k` đọc input tick `k`, tạo trạng thái `k+1`, và sự kiện trong bước đó được ghi với `tick=k+1`. `--ticks N` chạy đúng N bước, trừ khi game kết thúc sớm.
- `time_left_s = night1_duration_s - số_bước_đã_chạy / 60`.
- Vị trí người chơi là chân nhân vật; vị trí Bóng Mực là tâm; vị trí đèn là chân cột; đom đóm nằm trên mặt đất dù phần hiển thị có thể lơ lửng. Khoảng cách tuning tính trên mặt phẳng XZ giữa các điểm này, không cộng kích thước vật thể; bán kính bao gồm đúng khoảng cách `<= r`.

**File inputs** chứa một mảng `frames`. Ví dụ:

```json
{
  "frames": [
    { "tick": 0, "move": [0, 1], "cam_yaw_deg": 0 },
    { "tick": 120, "move": [0, 0], "interact": true },
    { "tick": 121, "interact": false },
    { "tick": 200, "pulse": true },
    { "tick": 201, "pulse": false }
  ]
}
```

- Trước frame đầu tiên, `move=[0,0]`, `cam_yaw_deg=0`, tất cả nút là `false`.
- Frame chỉ đổi các trường được nêu; trường vắng mặt giữ giá trị trước đó.
- `tick` phải tăng nghiêm ngặt, không trùng và không giảm.
- `move=[x,z]`, mỗi thành phần thuộc `[-1,1]`. Xoay hướng theo góc camera `theta` (radian): `x' = x*cos(theta) + z*sin(theta)`, `z' = -x*sin(theta) + z*cos(theta)`. Khi yaw bằng 0, x hướng +X và z hướng +Z. Vector dài hơn 1 phải chuẩn hóa.
- `jump`, `interact`, `pulse` và `dash` (nếu game có dash) là boolean; hành động kích hoạt ở cạnh chuyển từ `false` sang `true`, không lặp liên tục chỉ vì nút vẫn giữ.
- Không có file inputs nghĩa là người chơi đứng yên.

**File scenario** cho phép dựng trạng thái kiểm thử, ví dụ:

```json
{
  "player": { "pos": [0, 0, 0], "carried": 0, "flames": 3 },
  "random_motes": false,
  "random_shades": false,
  "motes": [[0, 0, 5]],
  "shades": [{ "pos": [10, 0, 0] }],
  "lanterns": [{ "id": "L1", "pos": [0, 0, 25], "deposited": 0 }],
  "time_left_s": 300
}
```

- `random_motes:false` và `random_shades:false` tắt sinh ngẫu nhiên tương ứng; chỉ các thực thể được liệt kê tồn tại. Bóng Mực trong scenario bắt đầu hoạt động ngay.
- `motes` và `shades` thay thế toàn bộ danh sách tương ứng; mảng rỗng nghĩa là không có thực thể. Bóng Mực có thể có `id` để test tham chiếu.
- `lanterns` cập nhật theo ID đèn của màn (`L1`–`L5`); đèn không nêu giữ nguyên. Có thể cập nhật `pos` và đặt `lit:true`.
- Trường không có dùng mặc định của game.
- Dựng scenario không phát event và không cộng điểm. Ví dụ đèn đặt sẵn `lit:true` không được tính điểm thắp đèn.

**Output JSONL** ghi một JSON object trên mỗi dòng:

1. `snapshot` ở tick 0 và theo chu kỳ `--snapshot-every` (mặc định 10), gồm tối thiểu `type`, `tick`, `sim_tick`, `state`, `time_left_s`, `score`, `player` (`pos`, `flames`, `carried`), `lanterns` (`id`, `pos`, `lit`, `deposited`), `shades` (`id`, `pos`, `state`) và `motes_active`. Mảng `motes` với từng `id` và `pos` được khuyến nghị.
2. `event` ngay khi xảy ra. Các tên và data được quy định:

| `name` | `data` |
|---|---|
| `mote_picked` | `{"carried": n}` |
| `deposit` | `{"lantern_id": "L1", "amount": n, "deposited": n}` |
| `lantern_lit` | `{"lantern_id": "L1"}` |
| `pulse` | `{"stunned_ids": ["S1"]}` |
| `player_hit` | `{"by": "<shade hoặc fall>", "flames": n, "dropped": n}` |
| `shade_spawned` | `{"id": "S3"}` |
| `game_over` | `{"result": "<won hoặc lost>", "reason": "<all_lit, dawn hoặc no_flames>"}` |

3. Dòng cuối luôn là `end`, ví dụ:

```json
{"type":"end","ticks":4800,"state":"won","score":1730}
```

Giá trị `state` gồm `playing`, `won`, `lost`; trạng thái Bóng Mực tối thiểu có `stunned`, các trạng thái khác do game định nghĩa. Tọa độ trong output làm tròn 3 chữ số thập phân. Cùng seed, scenario và inputs phải tạo output giống hệt qua hai lần chạy, kể cả ID tự sinh. Không cần dùng cùng chuỗi ngẫu nhiên với các bài khác. Không ghi event nếu sự kiện tương ứng không tồn tại trong game.

**Bộ scenario nên tự kiểm tra trước khi nộp:**

- Không input: kiểm tra player đứng yên, snapshot tick 0 và dòng `end`.
- Một đom đóm ở trong/ngoài pickup radius: kiểm tra biên bán kính, số mang và event nhặt.
- Tương tác trong/ngoài bán kính đèn: kiểm tra lượng nạp, giới hạn sức chứa và thắp đèn.
- Bóng Mực đuổi theo và chạm người chơi: kiểm tra vị trí, mất máu, bất tử sau hit và rơi đom đóm theo đúng tuning.
- Pulse ở trong/ngoài bán kính, đủ/thiếu ánh sáng và trước/sau cooldown: kiểm tra event, stun và tiêu hao.
- Thắng, hết giờ (`dawn`) và hết máu (`no_flames`): kiểm tra game-over, state và điểm.
- Chạy lặp lại cùng seed/scenario/inputs rồi so sánh toàn bộ JSONL byte-for-byte; kiểm tra file sai định dạng thoát mã 2.

Phần thêm sáng tạo không được làm đổi output headless theo contract. Hãy tắt các thực thể/trang trí không thuộc mô phỏng khi chạy headless, ghi mục **“Sáng tạo của tôi”** trong README và kèm bằng chứng ngắn rằng yêu cầu lõi vẫn đúng.

### Phase 2: Ticket-02

Trong khoảng 60 phút:

1. Đọc Ticket-02 tại đúng mốc phát hành.
2. So sánh yêu cầu mới với giả định Phase 1.
3. Cập nhật ghi chú thay đổi.
4. Viết kế hoạch kiểm chứng phần mới trước khi code.
5. Rà harness; thêm quy tắc/hook/skill nếu agent sai lặp lại.
6. Tích hợp yêu cầu mới theo commit nhỏ.
7. Chạy toàn bộ test Phase 1 còn hiệu lực.
8. Chạy bằng chứng cho phần mới.
9. Ghi đánh giá AI và token.
10. Gắn `phase-2`, push và xác nhận.

Nếu Ticket-02 thay hoặc làm rõ giả định cũ, ghi lý do rồi cập nhật test và tài liệu.

### Phase 3: Ticket-03

Trong khoảng 30 phút:

1. Đọc Ticket-03; tìm rõ luật cũ bị thay thế.
2. Liệt kê test, tài liệu và giả định bị ảnh hưởng.
3. Ghi một đoạn ngắn giải thích thay đổi thiết kế.
4. Sửa hoặc bỏ test cũ kèm lý do.
5. Tích hợp phần thay thế.
6. Chạy tất cả kiểm chứng còn hiệu lực.
7. Ghi kết quả Phase 3.
8. Gắn `phase-3`, push và xác nhận.

Không xóa test âm thầm. Nếu test cũ không còn đúng, ghi lý do thay thế.

### Phase 4: Ticket-04 và phát hành

Trong khoảng 90 phút:

1. Đọc tất cả yêu cầu số đo và yêu cầu phát hành.
2. Chạy benchmark hoặc đo theo đúng cách ticket quy định.
3. Lưu cấu hình máy, lệnh đo và kết quả.
4. Chạy lại các kiểm chứng quan trọng của toàn dự án.
5. Làm sạch README.
6. Dọn thư mục build và file asset.
7. Ghi nguồn asset và AI trong `CREDITS.md`.
8. Viết hoặc cập nhật `LICENSE`.
9. Tạo Release `v1.0.0`.
10. Quay và đính kèm video.
11. Gắn `phase-4`, push và xác nhận.

README phải cho người mới clone sạch chạy trong tối đa 3 lệnh. Hướng dẫn bao gồm:

- Cài đặt.
- Chạy game.
- Điều khiển.
- Chạy test.
- Chạy chế độ headless.

## 6. Harness AI thực dụng

Giữ harness ngắn, hữu ích và cập nhật.

### `AGENTS.md`

Nên chứa:

- Lệnh build và test.
- Quy ước thư mục.
- Quy tắc không tự sửa test để ép xanh.
- Định dạng bằng chứng.
- Quy tắc không commit secret.

Chỉ cập nhật khi phát hiện lỗi lặp lại hoặc quy tắc thật sự ổn định.

### Skill

Nên có ít nhất một skill cho một việc lặp lại. Ví dụ:

- Chạy game headless, lưu output và so với kết quả mong đợi.
- Quay hoặc chụp bằng chứng.
- Soát thay đổi khi agent sửa nhiều file.

Ghi trong nhật ký skill đó dùng khi nào và có thay đổi kết quả không.

### Hook

Có thể dùng hook để:

- Chạy test sau mỗi lần agent sửa code.
- Chặn kết thúc nếu test đỏ.
- Kiểm tra secret hoặc file `.env` trước commit.

Hook có giá trị khi ép một quy tắc luôn chạy, không phụ thuộc trí nhớ của agent.

### Reviewer riêng

Chọn người hoặc agent khác người/agent đã viết code để review đổi lớn. Tìm:

- Yêu cầu bị hiểu sai.
- Test yếu.
- Bằng chứng không khớp tag.
- Test cũ bị bỏ mà không ghi lý do.

## 7. Ghi chép bắt buộc

Tạo các file trong `docs/notes/`:

```text
docs/notes/phase-1.md
docs/notes/phase-2.md
docs/notes/phase-3.md
docs/notes/phase-4.md
docs/notes/ai-log.md
docs/notes/retro.md
```

Nội dung tối thiểu:

### Giả định theo phase

- Chỗ mơ hồ.
- Giá trị tự chọn.
- Lý do mỗi giả định.
- Yêu cầu thay đổi ở phase sau.

### Nhật ký dùng AI

- Công cụ/model dùng.
- Prompt hoặc mục tiêu chính.
- AI làm sai gì.
- Bạn phát hiện bằng cách nào.
- Bạn sửa harness thế nào.
- Ước tính token hoặc chi phí cho mỗi phase.
- Cách tiết kiệm token.

### Evaluation và retro

- Yêu cầu nào đạt/chưa đạt.
- Phase trước có hỏng không.
- Điều AI làm sai.
- Điều hiệu quả.
- Nếu làm lại, thay đổi quy trình gì.

## 8. Gắn tag và Release

Gắn tag nhẹ:

```bash
git add .
git commit -m "feat: complete phase 1"
git tag phase-1
git push origin main
git push origin phase-1
```

Nếu nhánh chính không phải `main`, thay `main` bằng tên nhánh đang dùng.

Xem tag:

```bash
git tag --list
git log --oneline --decorate -20
git show phase-1 --stat
```

Nếu gắn sai tag trước hạn:

```bash
git tag -d phase-2
git push origin :refs/tags/phase-2
git tag phase-2 <commit-dung>
git push origin phase-2
```

Sau khi hoàn thành, tạo Release `v1.0.0` bằng giao diện GitHub hoặc GitHub CLI:

```bash
gh release create v1.0.0 demo.mp4 --title "v1.0.0" --notes "Ban phat hanh cuoi"
```

Nếu Release đã tồn tại:

```bash
gh release upload v1.0.0 demo.mp4
```

## 9. Video demo dưới 5 phút

Video nên có:

- Chạy và chơi trực tiếp một đoạn.
- Chạy test hoặc chế độ headless và xem kết quả đạt.
- Chạy benchmark nếu ticket yêu cầu.
- Lướt nhanh qua README, bằng chứng, harness hoặc lịch sử git.

Đặt link ở đầu README:

```markdown
[Video demo](https://github.com/<ten-tai-khoan>/<ten-repo>/releases/tag/v1.0.0)
```

File nên là `.mp4`, dưới 5 phút và mở được khi chưa đăng nhập.

Trên macOS có thể dùng QuickTime hoặc màn hình ghi:

```bash
ffmpeg -i input.mov -t 300 -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 96k demo.mp4
```

## 10. Checklist trước khi nộp

### Sản phẩm

- [ ] Repo public và tên đúng quy ước.
- [ ] Mã nguồn ở trạng thái có thể chạy.
- [ ] Clone repo sang thư mục sạch, làm theo README trong tối đa 3 lệnh.
- [ ] Chế độ headless chạy đúng Test Contract.
- [ ] Có `LICENSE` và `CREDITS.md`.
- [ ] Không có `.env`, API key hoặc token.

### Tag và Release

- [ ] Có `phase-1`.
- [ ] Có `phase-2`.
- [ ] Có `phase-3`.
- [ ] Có `phase-4`.
- [ ] Có Release `v1.0.0`.
- [ ] Release có bản chạy được hoặc hướng dẫn chạy.

### Bằng chứng

- [ ] Mỗi yêu cầu chính của mỗi phase có cách kiểm chứng.
- [ ] Bằng chứng khớp mã ở tag tương ứng.
- [ ] Test đơn vị hoặc scenario riêng có thể chạy bằng một lệnh.
- [ ] Có kiểm tra tất định nếu contract yêu cầu.
- [ ] Test bị thay đổi bởi yêu cầu mới có lý do sửa hoặc bỏ.
- [ ] Phần chưa đạt ghi trung thực.

### SDLC và AI

- [ ] Có giả định cho chỗ mơ hồ.
- [ ] Có đánh giá từng phase.
- [ ] Có phân tích lỗi của AI.
- [ ] Có nhật ký token/chi phí và cách tiết kiệm.
- [ ] Có retro tổng kết.
- [ ] Harness như `AGENTS.md`, skill hoặc hook còn trong repo.
- [ ] Harness tồn tại trong lịch sử git.
- [ ] Commit nhỏ, thông điệp rõ.

### Video

- [ ] File `.mp4` dưới 5 phút.
- [ ] Có chơi thử.
- [ ] Có chạy test hoặc headless và cho thấy kết quả.
- [ ] Có đo hiệu năng nếu ticket yêu cầu.
- [ ] Link video ở đầu README.
- [ ] Kiểm tra trên cửa sổ ẩn danh: repo, Release và video đều public.

## 11. Kiểm tra cuối bằng lệnh

```bash
git clone <link-repo-cua-ban> kiem-tra-lab
cd kiem-tra-lab
git tag --list
git log --oneline --decorate -30
git status
```

Sau đó checkout từng tag nếu cần:

```bash
git checkout phase-1
# chạy README và bằng chứng của Phase 1
git checkout phase-2
# chạy README và bằng chứng của Phase 2
git checkout phase-3
# chạy README và bằng chứng của Phase 3
git checkout phase-4
# chạy bản phát hành và bằng chứng Phase 4
```

Quay về nhánh chính sau khi kiểm tra:

```bash
git switch main
```

Cuối cùng nộp link repo public lên LMS theo lịch Coach. Sau 4 giờ lab không commit thêm nội dung sản phẩm.
