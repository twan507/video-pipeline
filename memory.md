# VBSE Video Pipeline — Project Memory

Tracker cho tiến độ, decisions, blockers. Spec gốc: [vbse_video_pipeline.md](vbse_video_pipeline.md).

> Cập nhật file này mỗi session/milestone. Không dùng làm sổ tay cá nhân — chỉ ghi cái mà session sau cần biết.

---

## Current status

**Phase hiện tại:** Pre-Phase 0 (scaffold xong, chưa POC Vbee).

**Việc kế tiếp:** Phase 0 — POC Vbee API (xem [Blockers](#blockers)).

---

## Phase tracker

| Phase | Mục tiêu | Trạng thái | Ghi chú |
|---|---|---|---|
| Scaffold | Tạo folder structure + stub files | DONE 2026-05-11 | Hoàn tất theo spec section 2 |
| 0 | POC Vbee TTS | TODO | Blocker — phải clear trước Phase 1 |
| 1 | Core `lib/` + Remotion shared + template `bulletin/` + 1 video E2E | TODO | Spec đề xuất 1-2 tuần |
| 2 | Refactor + thêm `editorial_mystery/` | TODO | Template phức tạp nhất, sẽ định hình lại shared/ + theme |
| 3+ | Thêm `news_analysis/` và template khác | TODO | Tốc độ tăng dần sau Phase 2 |

---

## Locked decisions (Section 19 — không đổi sau Phase 1)

1. **Font stack:** Fraunces (serif) + Inter (sans) — cả 2 đều variable, Google Fonts free.
2. **Voice config:** 1 giọng Vbee duy nhất (`anh_khoi` tentatively). Speed khác per template:
   - bulletin: 1.05
   - editorial_mystery: 0.92
   - news_analysis: 1.0
3. **Scene ID format:** `s01`, `s02`, ... (2-digit zero-padded).
4. **video_id format:** `YYYY-MM-DD_<topic>_<template>`.
5. **Aspect ratio Phase 1:** 9:16 (1080x1920). 16:9 / 1:1 để roadmap.
6. **Theme tokens base:** `shared/theme/tokens.ts` — spacing scale, font weights, safe zones.

---

## Blockers

### Phase 0 — POC Vbee (1 ngày)
Cần clear trước khi viết `lib/vbee.py`:
- [ ] Lấy API key Vbee
- [ ] Test endpoint: sync hay async (job_id + polling)?
- [ ] Voice slug chính xác (`anh_khoi` có thể là alias UI)
- [ ] Rate limit per minute / per day
- [ ] SSML support (cần để đọc số, ngắt câu, nhấn)
- [ ] Pricing per character thực tế

---

## Architectural boundaries (Section 11 — đừng vi phạm)

- Python (`lib/`, `notebooks/`) **KHÔNG** chạm `remotion/src/`.
- TypeScript (`remotion/`) **KHÔNG** chạm `lib/` hay `notebooks/`.
- Interface duy nhất giữa 2 phía: `remotion/public/runs/<video_id>/script.json` + `audio/*.mp3`.

Schema source of truth: Pydantic. Sửa `lib/schema.py` → chạy `python scripts/sync_schema.py` → TS regenerate.

---

## Workflow checkpoints

- **Sửa schema:** `python scripts/sync_schema.py` → re-upload `prompts/<template>/schema.ts` vào Claude.ai Project (replace file cũ).
- **Làm video mới:** `cp notebooks/_template_<X>.ipynb notebooks/runs/<video_id>.ipynb` → đổi inputs → run cells 1-8.
- **Preview Remotion:** `cd remotion && npm start` → http://localhost:3000.

---

## Cost ceiling

Target monthly: $1-12 (chỉ Vbee). Mọi thứ khác free hoặc đã trả (Claude Max).

Upgrade triggers (theo Section 18):
- Music Content ID claim → Epidemic Sound $7.99/mo
- >10 video/ngày → Remotion Lambda
- >5 video/tuần manual paste thành bottleneck → Anthropic API direct

---

## Activity log

### 2026-05-11
- Scaffold toàn bộ folder structure theo spec section 2.
- Tạo stub files (Python `lib/`, Remotion src/, prompts/, scripts/) — chỉ placeholder, chưa implement.
- Tạo config: `pyproject.toml`, `remotion/package.json` (deps minimal), `remotion/tsconfig.json`, `.env.example`, `.gitignore`.
- Notebook blueprints (`_template_*.ipynb`) chỉ có markdown cell trỏ về section 4 — Phase 1 fill nội dung.
- Memory file này khởi tạo.
