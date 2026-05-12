# VBSE Video Pipeline — Project Memory

Tracker cho tiến độ, decisions, blockers. Spec gốc: [docs/video_pipeline.md](docs/video_pipeline.md).

> Cập nhật file này mỗi session/milestone. Không dùng làm sổ tay cá nhân — chỉ ghi cái mà session sau cần biết.

---

## Current status (2026-05-12)

**Pipeline E2E hoạt động đầy đủ cho template `bulletin`** — từ data card → script → audio Vbee → render MP4 1080x1920 + BGM. 33 unit tests + 1 live test pass.

Output mới nhất: `outputs/2026-05-12_W19_banking/render.mp4` (~1.5MB, 24.6s, narration AAC + BGM mix).

### Phase status
- **Scaffold**: DONE
- **Phase 0** (POC Vbee): DONE
- **Phase 1** (lib core + bulletin template + E2E): **DONE except deferred items** (data_card, sync_schema)
- **Phase 2** (editorial_mystery): TODO
- **Phase 3+** (news_analysis): TODO

### Việc kế tiếp khi resume

Xem [Resume from here](#resume-from-here) ở cuối file.

---

## Phase tracker chi tiết

| Phase | Mục tiêu | Trạng thái | Ghi chú |
|---|---|---|---|
| Scaffold | Folder structure + stubs | DONE 2026-05-11 | Theo spec section 2 |
| 0 | POC Vbee TTS | DONE 2026-05-12 | Async polling, voice OK, audio quality OK |
| 1 — lib/ | schema, validator, cache, audio, vbee, render | DONE 2026-05-12 | 33 unit tests pass. `data_card.py` defer (chưa có JSON sample) |
| 1 — notebook | `_template_bulletin.ipynb` 8 cells E2E | DONE 2026-05-12 | Cell 1-8 chạy được, sample data inline |
| 1 — Remotion | `templates/bulletin/` Composition + 4 scenes + shared theme | DONE 2026-05-12 | Roboto Vietnamese, BGM mix, fade in/out |
| 1 — E2E render | 1 video bulletin từ đầu tới cuối | DONE 2026-05-12 | render.mp4 1.5MB, narration + BGM ổn |
| 1 — defer | `lib/data_card.py`, `scripts/sync_schema.py` | TODO | Wait user JSON sample data + Node `json2ts` CLI |
| 2 | Refactor + thêm `editorial_mystery/` | TODO | Template phức tạp nhất, dịp tổng kết lại shared/theme |
| 3+ | `news_analysis/` + template khác | TODO | Tốc độ tăng sau khi core ổn định |

---

## Locked decisions

1. **Font:** **Roboto** (cả serif role + sans role), load qua `@remotion/google-fonts/Roboto` với `subsets: ['vietnamese', 'latin']`, weights 400/500/700. Lý do: hệ thống Georgia/Inter fallback vỡ diacritic tiếng Việt ("đầu" → "đâ`u"). Spec section 19 đề xuất Fraunces+Inter, đã thay vì Vietnamese support.
2. **Voice config:** `hn_male_phuthang_stor80dt_48k-fhg` (HN - Anh Khôi, **storytelling** variant — đã đổi từ news65dt vì user feedback giọng news quá flat). 1 giọng cho mọi template, đổi speed:
   - bulletin: **0.95** (đã giảm từ 1.05 cho dễ nghe)
   - editorial_mystery: 0.92 (chưa test)
   - news_analysis: 1.0 (chưa test)
3. **Scene ID format:** `s01`, `s02`, ... (2-digit zero-padded).
4. **video_id format:** `YYYY-MM-DD_<topic>_<template>`.
5. **Aspect ratio:** 9:16 (1080x1920) cho mọi template Phase 1-3.
6. **Theme tokens base:** `remotion/src/shared/theme/tokens.ts`.
7. **Python toolchain:** Portable Python 3.12.10 embed (`python/` folder) + uv. Bootstrap: `pyinstaller.bat` ở root, deps: `libinstaller.bat`. Pattern copy từ `d:/twan_projects/notebook-runner/` nhưng **đã bỏ** launcher/env-encrypt/zip/GUI vì solo dev. .bat files ở **project root**, không trong `scripts/`.
8. **Data input format = JSON** (không Excel/CSV).
9. **ffmpeg portable:** `imageio-ffmpeg` PyPI bundle binary trong `python/Lib/site-packages/imageio_ffmpeg/binaries/`. Không system install. pydub workaround: `from_file(format='mp3', codec='mp3')` thay `from_mp3()` để skip ffprobe (imageio-ffmpeg không có ffprobe).
10. **BGM mix:** volume 0.18 (~-15dB dưới narration), fade-in 0.5s, fade-out 1s. File `remotion/public/music/bulletin_bgm.mp3` 9.2MB.
11. **Vbee API:** ASYNC ONLY — POST `/api/v1/tts` → poll GET `/api/v1/tts/{request_id}` đến `status=SUCCESS`. `audio_link` expire 3 phút (download ngay). callback_url field bắt buộc, dùng placeholder `https://example.com/callback`. Env: `VBEE_TOKEN` (JWT) + `VBEE_APPID` (UUID) trong `.env` root. Không có voice nào trả `has_emphasis` field → emphasis_intensity param không khả dụng. SSML không nhắc tới trong doc.
12. **Cross-platform subprocess:** trong `lib/render.py` dùng `shutil.which('npx.cmd') or shutil.which('npx')` vì Windows Python subprocess không tự thêm `.cmd` extension.

---

## Architectural boundaries

- Python (`lib/`, `notebooks/`) **KHÔNG** chạm `remotion/src/`.
- TypeScript (`remotion/`) **KHÔNG** chạm `lib/` hay `notebooks/`.
- Interface duy nhất giữa 2 phía: `remotion/public/runs/<video_id>/script.json` + `audio/*.mp3` + (BGM chung) `remotion/public/music/<file>.mp3`.
- Schema source of truth: Pydantic ở `lib/schema.py`. Mirror TS hiện viết tay tại `remotion/src/templates/bulletin/schema.ts`. Phase 2: tự động hoá qua `scripts/sync_schema.py` (cần `json2ts` CLI từ npm `json-schema-to-typescript`).

---

## Test suite snapshot

```
pytest -v                   # 33 tests pass, 1 live deselected
pytest -v -m live           # 1 live (real Vbee call, ~1 credit)
```

Phân bố:
- `tests/test_cache.py`: 6 (hash cache key, scene/voice/speed sensitivity)
- `tests/test_audio.py`: 3 (pydub trim/normalize/duration via imageio-ffmpeg)
- `tests/test_vbee.py`: 5 mock + 1 live (async polling, error paths)
- `tests/test_schema.py`: 6 (Pydantic discriminated union, defaults)
- `tests/test_validator.py`: 8 (parse Claude output, content sanity)
- `tests/test_render.py`: 5 (subprocess wrapper, npx resolution)

---

## Workflow cheatsheet

### Setup mới (cài 1 lần)
```cmd
pyinstaller.bat                 :: Python embed 3.12.10 + uv into python/
copy .env.example .env          :: paste VBEE_TOKEN, VBEE_APPID
libinstaller.bat                :: uv pip install -e .
cd remotion && npm install      :: ~195 packages
```

### Làm video mới (mỗi lần)
```cmd
:: Hiện tại notebook đang trỏ video_id = 2026-05-12_W19_banking. Copy + đổi:
copy notebooks\_template_bulletin.ipynb notebooks\runs\<new_id>.ipynb
:: Mở .ipynb, đổi VIDEO_ID/WEEK/TOPIC ở Cell 1, paste data thật vào SAMPLE_DATA (Cell 2)
:: và RAW_FROM_CLAUDE (Cell 3, từ Claude.ai Project)
:: Run cells 1-8 tuần tự
python\python.exe -m jupyter lab notebooks\runs\<new_id>.ipynb
```

### Test
```cmd
python\python.exe -m pytest -v
```

### Render thủ công (debug)
```cmd
cd remotion
npx remotion render src/Root.tsx bulletin ../outputs/<id>/render.mp4 --props='{"scriptPath":"runs/<id>/script.json"}'
:: hoặc preview interactive:
npm start
```

---

## Resume from here

Khi mở session mới, thứ tự đề xuất:

### Hướng A — Polish bulletin (visual/audio tinh chỉnh)
Nếu muốn lặp video bulletin chất lượng cao trước khi mở rộng:
- Tinh chỉnh `narration_text` polish (thêm dấu chấm/gạch ngang để Vbee có nhịp ngắt tự nhiên hơn)
- Visual: thêm chart cho `QuickRankScene` (bar chart), gradient cho `BackgroundLayer`, brand footer
- Audio: sidechain compression (BGM tự ducking khi narration nói)
- Subtitle in-code (Phase 4 trong spec section 18 — WhisperX + KaraokeSubtitle)

### Hướng B — Mở rộng template (`editorial_mystery`)
Spec section 2 + 6 + 9 đã liệt kê 7 scene types: PaperScreenshot, ConceptBadge, MagazineSpread, FormulaCard, PullQuote, EditorPick, DatasheetCompare. Workflow:
1. Thêm scene types vào `lib/schema.py` (data classes mới)
2. Thêm validator rules nếu cần
3. Viết notebook `_template_editorial_mystery.ipynb` (copy từ bulletin, đổi VOICE speed=0.92, đổi scene structure)
4. Viết Remotion components `remotion/src/templates/editorial_mystery/`
5. Thêm composition vào `Root.tsx`
6. Refactor `shared/` nếu cần (chart components, paper texture primitive)

### Hướng C — Wire `lib/data_card.py` với data thật
User cần cung cấp JSON sample (kiểu schema họ muốn). Sau đó:
1. Define Pydantic model cho input data trong `lib/data_card.py`
2. Implement `build(json_path: Path) -> str` → markdown card
3. Update Cell 2 trong notebook để gọi `data_card.build(data_json)` thay `SAMPLE_DATA` inline
4. Test với data thật

### Hướng D — Auto-sync schema TS
Cần `json2ts` CLI:
```cmd
cd remotion && npm install -D json-schema-to-typescript
```
Sau đó implement `scripts/sync_schema.py` gọi `pydantic2ts.generate_typescript_defs` với `json2ts_cmd` trỏ về local `node_modules/.bin/json2ts.cmd`. Xoá manual TS types trong `remotion/src/templates/bulletin/schema.ts`.

### Hướng E — Polish prompts/style_guide
3 file `prompts/<template>/style_guide.md` hiện là stub TODO. Khi đăng ký Claude.ai Project, cần fill tone/length/pacing/word-replacement rules thực tế.

---

## Cost tracker

Phiên 2026-05-11–12 đã dùng:
- Vbee: ~12 credit (1 POC + 4 first synthesis + 4 retry sau khi đổi voice/speed + 1 live test + buffer)
- Pixabay/YouTube Audio Library: free, không tốn
- Claude Max: subscription đã trả

Target tháng: $1-12 Vbee.

---

## Activity log

### 2026-05-12 (session 2)
- **Toolchain pivot**: portable Python 3.12.10 embed + uv (pattern từ `d:/twan_projects/notebook-runner/`). Tạo `pyinstaller.bat` + `libinstaller.bat` ở root. Bỏ launcher/env-encrypt/zip/GUI vì solo dev.
- `scripts/` chỉ chứa Python code (`poc_vbee.py`, `sync_schema.py`).
- Fix `pyproject.toml`: `pydantic2ts` → `pydantic-to-typescript` (PyPI name khác module name).
- Phase 0 POC: chạy `poc_vbee.py` qua portable Python → 1 audio sample MP3 ok.
- Copy `scripts/poc_output.mp3` → `tests/fixtures/sample.mp3` làm fixture.
- Thêm `pytest`, `requests-mock`, `imageio-ffmpeg`, `@remotion/google-fonts` deps.
- VS Code `.vscode/settings.json` trỏ Pylance về `python\python.exe` portable.
- **Pivot bỏ subagent-driven** cho task verbatim — overhead quá lớn so với value (xem auto-memory feedback_subagent_overhead.md).
- **Phase 1 Python lib backend DONE**: `lib/{schema,validator,render,cache,audio,vbee}.py`. 33 unit tests + 1 live.
- **Notebook `_template_bulletin.ipynb`** 8 cells, sample data + sample Claude response inline.
- **Remotion bulletin template DONE**: 11 file Composition + 4 scenes + shared theme/primitives. Roboto Vietnamese subset qua `@remotion/google-fonts`. BGM volume 0.18, fade-in/out.
- **Iteration 1 audio**: voice news → stor (storytelling), speed 1.05 → 0.95, BGM 0.12 → 0.18.
- **Fix npx Windows**: `lib/render.py` dùng `shutil.which('npx.cmd')` thay literal `'npx'`. Test mới `test_find_npx_raises_when_missing`.
- **E2E render**: `outputs/2026-05-12_W19_banking/render.mp4` 1.5MB, 24.6s, video+audio ổn.
- Spec file moved: `vbse_video_pipeline.md` (root) → `docs/video_pipeline.md`. Bulk update references via sed.

### 2026-05-11 (session 1)
- Scaffold folder structure theo spec section 2.
- Tạo Vbee TTS integration plan tại `docs/superpowers/plans/2026-05-11-vbee-tts-integration.md`.
- Tạo stub files lib/ + Remotion src/ + prompts/ + scripts/.
- Tạo config: `pyproject.toml`, `remotion/package.json`, `remotion/tsconfig.json`, `.env.example`, `.gitignore`.
- Notebook blueprints stub (markdown-only).
- Đọc Vbee Postman doc → confirm API async-only, voice code thật cho "Anh Khôi", lưu `docs/vbee_api_collection.json`.
- Quyết định: polling (no webhook), env keys `VBEE_TOKEN`+`VBEE_APPID`, callback_url placeholder.
- Memory file khởi tạo.
