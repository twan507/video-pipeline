# VBSE Video Pipeline v2 — Architecture & Workflow

Pipeline sản xuất video phân tích tài chính dạng dọc 9:16 cho TikTok/Reels/YouTube Shorts, đa dạng style (bản tin, khám phá doanh nghiệp, phân tích tin tức), workflow notebook-centric, tối thiểu chi phí ngoài Claude Max subscription đã có.

## 1. Nguyên tắc thiết kế

Pipeline xoay quanh 4 nguyên tắc cố định:

**Notebook là cockpit.** Mọi orchestration chạy trong Jupyter notebook. Mỗi cell rõ một việc, state visible, debug dễ. Logic phức tạp tách sang `lib/` Python module, notebook chỉ import và gọi. Notebook không chứa business logic.

**LLM dùng qua Claude.ai chat (text-only).** Không Agent SDK, không tool use, không API programmatic. Tận dụng Max subscription đã trả qua Claude.ai Projects. Workflow là copy-paste có hỗ trợ: notebook output data card, người dùng paste vào Claude trong project tương ứng, copy JSON về paste lại notebook.

**1 Remotion project duy nhất, nhiều composition.** Mọi template chia sẻ chung node_modules, shared components, theme tokens. Mỗi template = 1 folder dưới `src/templates/`, 1 composition entry, scene components riêng.

**Schema source of truth là Pydantic.** Viết schema Python, generate TypeScript types tự động cho Remotion. Tránh duplicate Zod + Pydantic dễ drift.

## 2. Cấu trúc thư mục

```
projects/video/
├── notebooks/
│   ├── _template_bulletin.ipynb            # blueprint copy khi làm video mới
│   ├── _template_editorial_mystery.ipynb
│   ├── _template_news_analysis.ipynb
│   └── runs/
│       └── 2026-05-11_VNM_weekly.ipynb     # copy từ blueprint
│
├── lib/                                    # Python module, import vào notebook
│   ├── __init__.py
│   ├── schema.py                           # Pydantic models = SOURCE OF TRUTH
│   ├── data_card.py                        # build markdown card từ Excel/CSV
│   ├── vbee.py                             # TTS client
│   ├── audio.py                            # trim silence, normalize, duration
│   ├── validator.py                        # human-readable errors
│   ├── cache.py                            # audio cache theo hash narration
│   └── render.py                           # subprocess wrapper gọi Remotion CLI
│
├── prompts/                                # đính kèm Claude.ai Projects
│   ├── bulletin/
│   │   ├── style_guide.md                  # tone, length, pacing
│   │   ├── schema.ts                       # generated từ Pydantic
│   │   └── examples/
│   │       ├── 2026-W18_market_recap.json
│   │       └── 2026-W19_market_recap.json
│   ├── editorial_mystery/
│   └── news_analysis/
│
├── remotion/                               # 1 PROJECT DUY NHẤT
│   ├── package.json
│   ├── tsconfig.json
│   ├── remotion.config.ts
│   ├── src/
│   │   ├── Root.tsx                        # register MỌI composition
│   │   ├── shared/                         # dùng cross-template
│   │   │   ├── theme/
│   │   │   │   ├── tokens.ts               # base color/spacing/typography
│   │   │   │   └── themes.ts               # bulletin/editorial/dark variants
│   │   │   ├── components/
│   │   │   │   ├── BarChart.tsx
│   │   │   │   ├── LineChart.tsx
│   │   │   │   ├── Ranking.tsx
│   │   │   │   ├── KPICard.tsx
│   │   │   │   ├── KaraokeSubtitle.tsx
│   │   │   │   └── BrandFooter.tsx
│   │   │   └── primitives/
│   │   │       ├── Frame.tsx
│   │   │       ├── SafeZone.tsx
│   │   │       └── BackgroundLayer.tsx
│   │   └── templates/
│   │       ├── bulletin/
│   │       │   ├── Composition.tsx
│   │       │   ├── schema.ts               # GENERATED, không sửa tay
│   │       │   ├── SceneDispatcher.tsx
│   │       │   └── scenes/
│   │       │       ├── HeadlineScene.tsx
│   │       │       ├── QuickRankScene.tsx
│   │       │       ├── KPIScene.tsx
│   │       │       └── OutroScene.tsx
│   │       ├── editorial_mystery/
│   │       │   ├── Composition.tsx
│   │       │   ├── schema.ts
│   │       │   ├── SceneDispatcher.tsx
│   │       │   └── scenes/
│   │       │       ├── PaperScreenshotScene.tsx
│   │       │       ├── ConceptBadgeScene.tsx
│   │       │       ├── MagazineSpreadScene.tsx
│   │       │       ├── FormulaCardScene.tsx
│   │       │       ├── PullQuoteScene.tsx
│   │       │       ├── EditorPickScene.tsx
│   │       │       └── DatasheetCompareScene.tsx
│   │       └── news_analysis/
│   └── public/
│       ├── fonts/                          # Fraunces, Inter (Google Fonts)
│       ├── music/
│       │   ├── library.json                # metadata: file, mood, bpm, length
│       │   └── *.mp3
│       ├── textures/                       # paper, fold, grain
│       └── runs/                           # input mỗi video
│           └── 2026-05-11_VNM_weekly/
│               ├── script.json
│               └── audio/
│                   ├── s01.mp3
│                   └── s02.mp3
│
├── scripts/
│   └── sync_schema.py                      # Pydantic → TS, chạy khi sửa schema
│
├── outputs/                                # render output + artifact đầy đủ
│   └── 2026-05-11_VNM_weekly/
│       ├── data_card.md
│       ├── script_v1.json
│       ├── script_v2.json
│       ├── script_final.json
│       ├── claude_chat_url.txt
│       ├── render.mp4
│       └── manifest.json                   # metadata run này
│
├── .env                                    # VBEE_API_KEY
└── pyproject.toml
```

## 3. Pipeline 6 bước

Mọi template chạy qua cùng pipeline. Khác nhau ở schema, prompt, scene components.

| Bước | Cell notebook | Output | Auto/Manual |
|---|---|---|---|
| 1 | Load data → build data card | `outputs/<id>/data_card.md` | Auto |
| 2 | Display data card | Copy ra clipboard | Manual: paste vào Claude.ai |
| 3 | Paste script JSON từ Claude | Raw string trong cell | Manual: copy từ Claude |
| 4 | Parse + validate | `outputs/<id>/script_v1.json` hoặc errors | Auto, loop nếu fail |
| 5 | Enrich audio (Vbee + cache) + postprocess | `remotion/public/runs/<id>/audio/*.mp3` | Auto |
| 6 | Trigger Remotion render | `outputs/<id>/render.mp4` | Auto |

Bước 2-3 là manual. Phần còn lại tự động.

## 4. Notebook layout chi tiết

Notebook blueprint cho mỗi template type. Khi làm video mới: copy blueprint → đổi inputs (video_id, week, ticker, topic) → run cells.

```python
# Cell 1: Imports + config
import sys; sys.path.insert(0, '..')
from lib import schema, data_card, vbee, audio, validator, render, cache
from pathlib import Path
import json, pyperclip

PROJECT_ROOT = Path("../..").resolve()
TEMPLATE = "editorial_mystery"

# Inputs - đổi mỗi video mới
VIDEO_ID = "2026-05-11_VNM_weekly"
WEEK = 19
TICKER = "VNM"
TOPIC = "Phân tích KQKD Q1/2026 của Vinamilk"

# Setup paths
OUTPUT_DIR = PROJECT_ROOT / "outputs" / VIDEO_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RUN_DIR = PROJECT_ROOT / "remotion" / "public" / "runs" / VIDEO_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)
```

```python
# Cell 2: Build data card
card_md = data_card.build(week=WEEK, ticker=TICKER)
(OUTPUT_DIR / "data_card.md").write_text(card_md)
pyperclip.copy(card_md)
print(f"Data card đã copy clipboard ({len(card_md)} chars)")
print("---")
print(card_md[:500] + "...")
```

```python
# Cell 3: PASTE script JSON từ Claude (raw string giữa """ """)
raw_response = """
{
  "video_id": "2026-05-11_VNM_weekly",
  "meta": {...},
  "scenes": [...]
}
"""
```

```python
# Cell 4: Parse + validate, loop nếu fail
try:
    script_dict = validator.parse_claude_output(raw_response)
    script = schema.Script.model_validate(script_dict)
    errors = validator.check_data_integrity(script, card_md)
    
    if errors:
        print(validator.format_errors_for_claude(errors))
        pyperclip.copy(validator.format_errors_for_claude(errors))
        raise ValueError("Validate fail - errors đã copy clipboard, paste cho Claude fix")
    
    (OUTPUT_DIR / "script_final.json").write_text(script.model_dump_json(indent=2))
    print("Validated OK, scenes:", len(script.scenes))
except Exception as e:
    print("LỖI:", e)
```

```python
# Cell 5: Enrich audio + postprocess
script = schema.Script.model_validate_json((OUTPUT_DIR / "script_final.json").read_text())
audio_dir = RUN_DIR / "audio"
audio_dir.mkdir(exist_ok=True)

for scene in script.scenes:
    audio_path = cache.audio_path(scene, audio_dir)
    if not audio_path.exists():
        vbee.synthesize(scene.narration_text, audio_path, voice="anh_khoi", speed=0.95)
        audio.trim_silence(audio_path)
        audio.normalize_peak(audio_path)
    scene.audio_path = f"audio/{audio_path.name}"
    scene.duration = audio.get_duration(audio_path)

# Lưu script.json vào public/runs/<id>/ cho Remotion đọc
(RUN_DIR / "script.json").write_text(script.model_dump_json(indent=2))
print(f"Audio ready: {sum(1 for s in script.scenes if s.audio_path)} scenes")
print(f"Total duration: {sum(s.duration for s in script.scenes):.1f}s")
```

```python
# Cell 6: Render Remotion
output_path = render.render_video(
    template=TEMPLATE,
    video_id=VIDEO_ID,
    project_root=PROJECT_ROOT,
)
print(f"Render xong: {output_path}")
```

```python
# Cell 7: Preview inline
from IPython.display import Video
Video(str(output_path), width=360)
```

```python
# Cell 8: Lưu manifest run này
manifest = {
    "video_id": VIDEO_ID,
    "template": TEMPLATE,
    "topic": TOPIC,
    "week": WEEK,
    "ticker": TICKER,
    "scenes_count": len(script.scenes),
    "total_duration_sec": sum(s.duration for s in script.scenes),
    "claude_chat_url": "https://claude.ai/chat/...",  # paste URL chat
    "created_at": "2026-05-11T20:00:00+07:00",
}
(OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
```

## 5. Claude.ai Projects setup

Đây là cách tận dụng Max subscription tối ưu. Tạo **1 Project trong Claude.ai cho mỗi template**.

Naming: `Video — Bulletin`, `Video — Editorial Mystery`, `Video — News Analysis`.

Mỗi Project đính kèm:

1. **`style_guide.md`**: tone, target length, pacing, ngôn từ tránh, cách đọc số bằng chữ.
2. **`schema.ts`**: TypeScript types generated từ Pydantic (paste qua mỗi lần regenerate).
3. **3-5 file examples**: `script.json` đã chạy thành công, làm few-shot reference.
4. **System instructions** (Project Instructions trong Claude.ai):

```
Bạn là biên kịch video tài chính cho VBSE.

Mỗi lần user paste data card + topic, bạn trả về EXACTLY một JSON object 
match schema đính kèm. Không markdown wrapper, không preamble, không 
commentary. Chỉ JSON từ { đến }.

Quy tắc bắt buộc:
- Mọi số trong scene.data PHẢI copy từ data card, không tính lại không bịa.
- narration_text: đọc tự nhiên, số đọc bằng chữ (mười tám phần trăm).
- Đa dạng scene_type theo schema, tránh dùng cùng 1 type 3 lần liên tiếp.
- Hook 5 giây đầu: câu gợi tò mò hoặc số shock.
- Tổng narration phù hợp target length của template (xem style_guide.md).
- Tham khảo examples/ để hiểu pattern.

Khi nhận thông báo lỗi validation, fix các điểm chỉ ra và trả lại JSON 
đầy đủ (không partial patch).
```

Context được preserve cross-session. Mỗi video chỉ paste data card + topic, không phải resend schema + examples mỗi lần. Tiết kiệm token + thời gian.

Khi sửa schema: chạy `python scripts/sync_schema.py`, re-upload `schema.ts` mới vào Project (replace file cũ).

## 6. Schema source of truth (Pydantic → TypeScript)

Viết schema 1 lần bằng Pydantic, generate TypeScript types tự động cho Remotion.

```python
# lib/schema.py
from pydantic import BaseModel, Field
from typing import Literal, Union, Optional

class Meta(BaseModel):
    title: str
    voice: str = "anh_khoi"
    speed: float = 0.95
    fps: int = 30
    width: int = 1080
    height: int = 1920
    created_at: str

# Bulletin template scenes
class HeadlineData(BaseModel):
    headline: str
    category: str
    issue_label: Optional[str] = None

class HeadlineScene(BaseModel):
    id: str
    type: Literal["headline"]
    data: HeadlineData
    narration_text: str
    audio_path: Optional[str] = None
    duration: Optional[float] = None

# Editorial mystery template scenes
class ConceptBadgeData(BaseModel):
    badge_label: str
    title: str
    subtitle: Optional[str] = None

class ConceptBadgeScene(BaseModel):
    id: str
    type: Literal["concept_badge"]
    data: ConceptBadgeData
    narration_text: str
    audio_path: Optional[str] = None
    duration: Optional[float] = None

# (... các scene khác)

Scene = Union[HeadlineScene, ConceptBadgeScene, ...]

class Script(BaseModel):
    video_id: str
    template: str  # "bulletin" | "editorial_mystery" | "news_analysis"
    meta: Meta
    scenes: list[Scene] = Field(discriminator="type")
```

```python
# scripts/sync_schema.py
from pydantic2ts import generate_typescript_defs

# Generate cho mỗi template (filter scenes phù hợp)
generate_typescript_defs(
    "lib.schema",
    "../remotion/src/templates/editorial_mystery/schema.ts",
    json2ts_cmd="json2ts",
)
# Tương tự cho bulletin, news_analysis
```

Trong Remotion, Composition import schema generated:

```ts
// remotion/src/templates/editorial_mystery/Composition.tsx
import type {Script} from './schema';

export const EditorialMysteryComposition: React.FC<{script: Script}> = ({script}) => {
  // Type-safe access, IDE autocomplete
};
```

Sửa Pydantic → chạy `sync_schema.py` → TypeScript update tự động. Không drift.

## 7. Validator UX

Validator có 3 layer:

**Layer 1: Schema (Pydantic).** Catch missing fields, wrong types, invalid enum values. Pydantic tự handle.

**Layer 2: Data integrity.** Check số trong scene.data match data card. Quan trọng để chống LLM bịa số.

**Layer 3: Content sanity.** narration_text độ dài hợp lý, có hook ở scene đầu, không lặp scene type liên tiếp.

Output errors phải **paste vào Claude là Claude hiểu ngay**:

```python
# lib/validator.py
def format_errors_for_claude(errors: list[ValidationError]) -> str:
    lines = ["LỖI VALIDATION - sửa các điểm sau rồi trả JSON đầy đủ lại:\n"]
    for e in errors:
        lines.append(f"- scenes[{e.scene_idx}] ({e.scene_type} \"{e.scene_title}\"):")
        lines.append(f"    {e.message}")
        if e.suggestion:
            lines.append(f"    Gợi ý: {e.suggestion}")
    return "\n".join(lines)
```

Ví dụ output:

```
LỖI VALIDATION - sửa các điểm sau rồi trả JSON đầy đủ lại:

- scenes[2] (chart "Doanh thu quý theo năm"):
    series "2025" tại Q3 đang là 11800, phải là 11600 theo data card.
- scenes[4] (kpi_card "Tỷ suất lợi nhuận gộp"):
    thiếu trường "delta". Schema yêu cầu trường này.
    Gợi ý: delta = current_value - previous_value = -9.4 điểm phần trăm.
- scenes[1] (bullet_list):
    narration nhắc "tồn kho tăng gấp đôi rưỡi" nhưng data card không có 
    metric tồn kho. Có vẻ LLM tự bịa, vui lòng bỏ hoặc thay bằng metric 
    có trong data card.
```

Copy text này vào Claude trong cùng chat → Claude fix → paste lại Cell 3. Vòng lặp 2-3 round trip là max.

## 8. Audio enrichment

### Vbee TTS client

```python
# lib/vbee.py
import requests, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class VbeeClient:
    BASE_URL = "https://vbee.vn/api/v1"  # verify endpoint thực tế khi có API key
    
    def __init__(self):
        self.api_key = os.environ["VBEE_API_KEY"]
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def synthesize(self, text: str, output_path: Path, voice="anh_khoi", speed=0.95):
        # POC trước: gọi 1 lần check endpoint sync hay async,
        # response format, voice slug chính xác.
        response = self.session.post(
            f"{self.BASE_URL}/synthesize",
            json={"text": text, "voice": voice, "speed": speed},
        )
        response.raise_for_status()
        # Sync case: response trả MP3 binary trực tiếp
        output_path.write_bytes(response.content)
        # Async case: response trả {"job_id": "..."} → poll status
        # → download khi done
```

**Bắt buộc POC Vbee 1 buổi trước khi viết tích hợp:**
- Endpoint sync hay async (job_id + polling)
- Voice slug chính xác (`anh_khoi` có thể là alias UI, API có thể dùng slug khác)
- Rate limit per minute, per day
- SSML support (cần để xử lý số, ngắt câu, nhấn)
- Pricing per character thực tế

### Cache theo hash

```python
# lib/cache.py
import hashlib

def audio_cache_key(scene, voice: str, speed: float) -> str:
    key = f"{scene.narration_text}|{voice}|{speed}"
    h = hashlib.sha256(key.encode()).hexdigest()[:12]
    return f"{scene.id}_{h}.mp3"

def audio_path(scene, audio_dir: Path, voice="anh_khoi", speed=0.95) -> Path:
    return audio_dir / audio_cache_key(scene, voice, speed)
```

Sửa narration scene 3 → re-run Cell 5 → chỉ gen lại MP3 scene 3. Các scene khác cache hit, skip API call.

### Postprocess audio

```python
# lib/audio.py
from pydub import AudioSegment, silence
from mutagen.mp3 import MP3

def trim_silence(path: Path, threshold_db=-40, padding_ms=100):
    """Vbee đôi khi có silence padding cuối, gây cảm giác đứng máy."""
    audio = AudioSegment.from_mp3(path)
    chunks = silence.split_on_silence(
        audio, min_silence_len=300, silence_thresh=threshold_db, keep_silence=padding_ms
    )
    if chunks:
        result = sum(chunks[1:], chunks[0])
        result.export(path, format="mp3", bitrate="128k")

def normalize_peak(path: Path, target_dbfs=-1.0):
    audio = AudioSegment.from_mp3(path)
    change = target_dbfs - audio.max_dBFS
    audio.apply_gain(change).export(path, format="mp3", bitrate="128k")

def get_duration(path: Path) -> float:
    return round(MP3(path).info.length, 3)
```

Hai bước này chạy sau mỗi lần synthesize. Sync drift giảm rõ.

## 9. Remotion: 1 project, multi-composition

### Root.tsx register tất cả compositions

```tsx
// remotion/src/Root.tsx
import {Composition, staticFile} from 'remotion';
import {BulletinComposition} from './templates/bulletin/Composition';
import {EditorialMysteryComposition} from './templates/editorial_mystery/Composition';
import {NewsAnalysisComposition} from './templates/news_analysis/Composition';

type Props = {scriptPath: string; script?: any};

const loadScriptMetadata = async ({props}: {props: Props}) => {
  const script = await fetch(staticFile(props.scriptPath)).then(r => r.json());
  const totalSec = script.scenes.reduce((s: number, sc: any) => s + sc.duration, 0);
  return {
    durationInFrames: Math.ceil(totalSec * 30),
    props: {...props, script},
  };
};

export const RemotionRoot = () => (
  <>
    <Composition
      id="bulletin"
      component={BulletinComposition}
      defaultProps={{scriptPath: 'runs/_demo_bulletin/script.json'} as Props}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={1}
      calculateMetadata={loadScriptMetadata}
    />
    <Composition
      id="editorial_mystery"
      component={EditorialMysteryComposition}
      defaultProps={{scriptPath: 'runs/_demo_editorial/script.json'} as Props}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={1}
      calculateMetadata={loadScriptMetadata}
    />
    <Composition
      id="news_analysis"
      component={NewsAnalysisComposition}
      defaultProps={{scriptPath: 'runs/_demo_analysis/script.json'} as Props}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={1}
      calculateMetadata={loadScriptMetadata}
    />
  </>
);
```

### Composition mỗi template

```tsx
// remotion/src/templates/editorial_mystery/Composition.tsx
import {Sequence, Audio, staticFile} from 'remotion';
import {SceneDispatcher} from './SceneDispatcher';
import {BackgroundLayer} from '../../shared/primitives/BackgroundLayer';
import type {Script} from './schema';

type Props = {scriptPath: string; script: Script};

export const EditorialMysteryComposition: React.FC<Props> = ({script, scriptPath}) => {
  const baseDir = scriptPath.replace(/\/script\.json$/, '');
  let cursor = 0;
  
  return (
    <>
      <BackgroundLayer theme="editorial" />
      {script.scenes.map(scene => {
        const dur = Math.round(scene.duration * 30);
        const from = cursor;
        cursor += dur;
        return (
          <Sequence key={scene.id} from={from} durationInFrames={dur}>
            <SceneDispatcher scene={scene} />
            <Audio src={staticFile(`${baseDir}/${scene.audio_path}`)} />
          </Sequence>
        );
      })}
    </>
  );
};
```

### SceneDispatcher

```tsx
// remotion/src/templates/editorial_mystery/SceneDispatcher.tsx
import {PaperScreenshotScene} from './scenes/PaperScreenshotScene';
import {ConceptBadgeScene} from './scenes/ConceptBadgeScene';
import {MagazineSpreadScene} from './scenes/MagazineSpreadScene';
// ...

export const SceneDispatcher = ({scene}) => {
  switch (scene.type) {
    case 'paper_screenshot': return <PaperScreenshotScene data={scene.data} />;
    case 'concept_badge':    return <ConceptBadgeScene data={scene.data} />;
    case 'magazine_spread':  return <MagazineSpreadScene data={scene.data} />;
    case 'formula_card':     return <FormulaCardScene data={scene.data} />;
    case 'pullquote':        return <PullQuoteScene data={scene.data} />;
    case 'editor_pick':      return <EditorPickScene data={scene.data} />;
    case 'datasheet_compare': return <DatasheetCompareScene data={scene.data} />;
    default: throw new Error(`Unknown scene type: ${scene.type}`);
  }
};
```

### Animation pattern (mọi scene component dùng chung)

```tsx
const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
const y = interpolate(frame, [0, 20], [30, 0], {extrapolateRight: 'clamp'});
```

Không dùng `spring`, không dùng state phức tạp. Pattern đơn giản này đủ cho mọi animation từ fade, slide, count-up, bar grow.

### Theme system

```ts
// remotion/src/shared/theme/tokens.ts
export const baseTokens = {
  font: {
    serif: 'Fraunces, Georgia, serif',
    sans: 'Inter, system-ui, sans-serif',
  },
  spacing: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96],
  fps: 30,
  safeZone: {top: 200, bottom: 480, paddingX: 80},
};

// remotion/src/shared/theme/themes.ts
export const themes = {
  bulletin: {
    bg: '#FFFFFF',
    fg: '#0A0A0A',
    accent: '#DC2626',  // red, news vibe
    secondary: '#525252',
  },
  editorial: {
    bg: '#F0EAD8',
    fg: '#1A1A1A',
    accent: '#2563EB',
    gold: '#C9A227',
    paper: 'url(/textures/paper.png)',
  },
  dark: {  // dùng cho datasheet scene trong editorial
    bg: '#0F1419',
    fg: '#E5E7EB',
    accent: '#60A5FA',
    gold: '#F59E0B',
  },
};
```

Theme là prop per scene, override default. Component shared như `<Ranking>` nhận theme prop, render styling khác nhau.

## 10. Trigger render từ notebook

```python
# lib/render.py
import subprocess, json
from pathlib import Path

def render_video(template: str, video_id: str, project_root: Path) -> Path:
    remotion_dir = project_root / "remotion"
    script_rel = f"runs/{video_id}/script.json"
    output_path = project_root / "outputs" / video_id / "render.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "npx", "remotion", "render",
        "src/Root.tsx",
        template,
        str(output_path),
        "--props", json.dumps({"scriptPath": script_rel}),
        "--concurrency=4",
        "--crf=18",
        "--log=info",
    ]
    
    result = subprocess.run(cmd, cwd=remotion_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Remotion render failed:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )
    return output_path

def preview_studio(project_root: Path):
    """Bật Remotion Studio xem preview interactive."""
    remotion_dir = project_root / "remotion"
    subprocess.Popen(["npm", "start"], cwd=remotion_dir)
    print("Studio: http://localhost:3000")
```

## 11. Boundary giữa Python và TypeScript

Pattern rõ ràng:

```
Notebook + lib/ (Python orchestration)
        │
        │   GHI vào: remotion/public/runs/<video_id>/
        │     ├── script.json
        │     └── audio/*.mp3
        ▼
remotion/ (TypeScript render engine)
        │
        │   ĐỌC từ public/runs/<video_id>/
        │   Render
        ▼
outputs/<video_id>/render.mp4
```

Python **không bao giờ** chạm `remotion/src/`. TypeScript **không bao giờ** chạm `lib/` hay notebook. Giao diện duy nhất giữa 2 phía là `script.json` + audio files trong `public/runs/`.

## 12. Asset management

### Fonts

Đặt trong `remotion/public/fonts/`. Load qua CSS trong Composition:

```tsx
import {loadFont} from '@remotion/fonts';
import {continueRender, delayRender, staticFile} from 'remotion';

const [handle] = useState(() => delayRender());

useEffect(() => {
  Promise.all([
    loadFont('Fraunces', staticFile('fonts/Fraunces-Variable.ttf')),
    loadFont('Inter', staticFile('fonts/Inter-Variable.ttf')),
  ]).then(() => continueRender(handle));
}, []);
```

Khuyến nghị: **Fraunces** (serif headline, variable font, Google Fonts, free) + **Inter** (sans body, Google Fonts, free). Hai font này variable nên có thể đổi weight/optical-size trong runtime.

### Music

`remotion/public/music/library.json`:

```json
[
  {"file": "mystery_01.mp3", "mood": "mysterious", "bpm": 75, "length": 120, "source": "youtube_audio_library"},
  {"file": "neutral_news_01.mp3", "mood": "neutral", "bpm": 95, "length": 110, "source": "uppbeat"},
  {"file": "editorial_calm_01.mp3", "mood": "contemplative", "bpm": 70, "length": 180, "source": "youtube_audio_library"}
]
```

Mỗi template có default mood preference, RootComposition random pick từ subset phù hợp.

Sources free đáng dùng:
- **YouTube Audio Library**: kênh chính chủ, zero Content ID risk
- **Uppbeat free tier**: track có credit "no Content ID"
- **Pixabay Music**: cẩn trọng, một số track vẫn bị Content ID claim

Upgrade khi nghiêm túc: **Epidemic Sound Personal $7.99/mo** (industry standard, an toàn Content ID).

### Textures

`remotion/public/textures/`:
- `paper.png`: paper grain background cho editorial mode
- `fold_vertical.svg`: đường fold dọc giữa cho magazine spread
- `noise.png`: subtle film grain overlay

1 lần tạo trong Photoshop hoặc Procreate, dùng forever.

## 13. Naming conventions

**`video_id`**: format `YYYY-MM-DD_<ticker_or_topic>_<template_short>`. Ví dụ:
- `2026-05-11_VNM_weekly`
- `2026-05-12_market_recap_bulletin`
- `2026-05-13_SHB_M&A_news`

Format ngày trước → folder sort by date tự nhiên.

**Scene id**: `s01`, `s02`, ... — 2 chữ số, padding zero để sort đúng.

**Audio cache key**: `<scene_id>_<hash12>.mp3`. Đổi narration → hash đổi → file mới, file cũ ở lại làm cache.

**Branch git**: 1 branch chính `main`, không cần feature branch cho 1 dev cá nhân.

## 14. Chi phí ngoài Claude Max

Tổng cố định monthly:

| Component | Tool | Cost |
|---|---|---|
| LLM | Claude Max (sunk) | $0 thêm |
| TTS | Vbee studio tier | $1-12 |
| Music | YouTube Audio Library + Uppbeat free | $0 |
| Render | Local (laptop GPU) | $0 |
| Subtitle (Phase 1 skip) | CapCut Desktop free | $0 |
| Remotion | Free License cá nhân | $0 |
| Fonts | Google Fonts | $0 |

**Tổng: $1-12/tháng**.

Nâng cấp tùy chọn:
- Epidemic Sound Personal: $7.99/mo (music premium an toàn Content ID)
- Lambda render: $0.05-0.15/video, chỉ khi >10 video/ngày

## 15. Best practices với Claude Max subscription

Claude Code subscription không phải là token vô hạn. Có 5-hour window và weekly cap.

**Tận dụng Claude.ai Projects.** Project context được preserve cross-session, không phải resend schema + few-shot mỗi lần. Đây là cách tiết kiệm token chính.

**Không dùng API key trong env khi muốn dùng subscription.** Nếu `ANTHROPIC_API_KEY` set, Claude.ai web có thể không bị ảnh hưởng nhưng nếu sau này chuyển sang programmatic thì env sẽ override sang API billing. Để rõ ràng: workflow hiện tại không cần API key, chỉ dùng Claude.ai web.

**Off-peak hours.** Weekday 5-11am Pacific (tương đương 8pm-2am giờ VN) bị throttle nhanh hơn. Chạy heavy work ban ngày VN.

**Plan mode trước task lớn.** Nếu sau này refactor toàn pipeline, dùng Plan mode (Shift+Tab trong Claude.ai web) cho Claude vạch kế hoạch trước, tránh lan man.

**Sonnet cho task đơn giản.** Khi sửa typo, format JSON, paraphrase đơn giản — không cần Opus 4.7, switch sang Sonnet 4.6 trong Claude.ai. Tiết kiệm token đáng kể.

## 16. Phase build sequence

**Phase 0 (1 ngày): POC Vbee.** Lấy API key, test endpoint sync/async, voice slug, pricing, SSML support. Đây là blocker phải clear trước khi viết tích hợp.

**Phase 1 (1-2 tuần): Core + 1 template đơn giản (bulletin).**

Build:
- `lib/` Python module (schema, data_card, vbee, audio, validator, render, cache)
- `remotion/` project setup, Root.tsx, shared theme/components
- Template `bulletin/` với 4-5 scene types đơn giản
- 1 Claude.ai Project + style_guide + 1 example
- Notebook blueprint cho bulletin
- Chạy E2E 1 video thật

Output: pipeline chạy end-to-end với 1 template. Mọi bug pipeline core đã catch.

**Phase 2 (1-2 tuần): Refactor + thêm `editorial_mystery`.**

Đây là template phức tạp nhất (style sample). Đến đây mới biết:
- Component nào nên đẩy sang `shared/`
- Theme system cần generalize tới mức nào
- Audio sync drift có vấn đề gì

Refactor architecture lần cuối. Sau Phase 2, core stable.

**Phase 3+: thêm `news_analysis`, template khác.**

Tốc độ tăng dần. Template thứ 3 build ~3-5 ngày vì core không sửa, shared components đủ dùng.

## 17. Quick reference

```bash
# Setup 1 lần
cd projects/video
python -m venv .venv && source .venv/bin/activate
pip install -e .                            # lib/ as package
cd remotion && npm install && cd ..
cp .env.example .env                        # điền VBEE_API_KEY

# Sửa Pydantic schema → regenerate TS
python scripts/sync_schema.py
# Re-upload schema.ts vào Claude.ai Projects (manual)

# Làm video mới
cp notebooks/_template_editorial_mystery.ipynb notebooks/runs/2026-05-11_VNM_weekly.ipynb
jupyter lab notebooks/runs/2026-05-11_VNM_weekly.ipynb
# Run cells theo thứ tự 1-8

# Preview Remotion Studio (interactive dev)
cd remotion && npm start                    # localhost:3000

# Render từ CLI (notebook tự gọi qua subprocess)
cd remotion
npx remotion render src/Root.tsx editorial_mystery out.mp4 \
  --props='{"scriptPath":"runs/2026-05-11_VNM_weekly/script.json"}'
```

## 18. Roadmap mở rộng

Khi pipeline stable và muốn scale:

- **Subtitle in-code.** Thêm WhisperX (hoặc PhoWhisper alignment) vào enrich step, render karaoke subtitle trực tiếp trong Remotion. Schema thêm field `narration_words: WordTimestamp[]` optional.
- **Multi-aspect cùng 1 script.** Composition register thêm 16:9 và 1:1 variants, dispatch component layout responsive.
- **Music tự động pick.** LLM trong brainstorm chọn `meta.mood`, RootComposition random pick từ library subset.
- **AI-generated music.** Khi cần signature mỗi video, upgrade lên Mubert API hoặc Stable Audio (~$50-100/mo).
- **Lambda render.** Khi >10 video/ngày, deploy Remotion Lambda. Phải benchmark scene có heavy GPU effect trước.
- **Programmatic LLM.** Khi >5 video/tuần và manual copy-paste thành bottleneck, upgrade sang Anthropic API direct với prompt caching. Cost ~$0.50-1/video.

Mọi mở rộng đều **additive** — schema cũ vẫn chạy, không breaking change.

## 19. Decisions cần lock trước Phase 1

Những thứ thay đổi sau sẽ rework đau, lock ngay:

1. **Font stack**: Fraunces (serif) + Inter (sans) làm default cho mọi template. Lock 1 lần, không đổi giữa template.
2. **Voice config base**: 1 giọng Vbee duy nhất, đổi `speed` per template (mystery 0.92, bulletin 1.05, analysis 1.0). Đảm bảo consistency brand audio.
3. **Schema scene ID format**: `s01`, `s02` (2-digit zero-padded). Đừng đổi sang `scene_1`, `intro`, v.v. sau này.
4. **video_id format**: `YYYY-MM-DD_<topic>_<template>`. Đổi định dạng sau = phải migrate folder.
5. **Aspect ratio Phase 1**: 9:16 (1080x1920) cho mọi video. 16:9 và 1:1 để roadmap.
6. **Theme tokens base**: spacing scale, font weights, safe zones. Lock trong `shared/theme/tokens.ts`.

Còn lại (scene types, prompt phrasing, animation timing) đều flexible, sửa được.

---

## 20. Implementation status snapshot (2026-05-13)

> Spec ở trên là thiết kế gốc. Thực tế triển khai có nhiều thay đổi — chi tiết tại `memory.md` ở project root.

### Đã làm
- **Toolchain**: portable Python 3.12.10 + uv (`pyinstaller.bat`, `libinstaller.bat` ở project root). Node 24. ffmpeg portable qua `imageio-ffmpeg`. Roboto font qua `@remotion/google-fonts`.
- **lib/**: `schema.py`, `validator.py`, `vbee.py`, `cache.py`, `audio.py`, `render.py` — 34 unit tests + 1 live test pass.
- **Notebook**: `_template_bulletin.ipynb` 8 cells. Cell 2 sample data dạng JSON đầy đủ (VN Index OHLC + foreign trading + sectors), Cell 3 RAW_FROM_CLAUDE 5 scenes rich highlights.
- **Remotion bulletin template**: Composition + 4 scene types (Intro, Metric, Ranking, Outro) + SafeFrame primitive + shared theme + Root.tsx.
- **E2E render thực tế**: `outputs/2026-05-12_daily_eod/render.mp4` 2.9MB 58.5s, 5 scenes, 1080x1080 vuông, narration Vbee + BGM mix.

### Scene types (final, renamed 2026-05-12)
| Type | Mục đích | Layout chính |
|---|---|---|
| `intro` | Cover/opening | Header (category + headline) + highlights (bullets/stats sync narration) + issue_label footer |
| `metric` | Single big metric | Metric label + count-up value + delta animated + optional context_note |
| `ranking` | List 3-5 items | Title + summary_text + items (rank/label/value/value_suffix/change_pct/appear_at_sec) |
| `outro` | Closing | date_label + cta + next_topic + handle |

### Decisions thay đổi so với section 19
| Item | Spec gốc | Thực tế | Lý do |
|---|---|---|---|
| Font | Fraunces (serif) + Inter (sans) | **Roboto** cho cả 2 role, load qua `@remotion/google-fonts` subset `vietnamese` | Fraunces+Inter system fallback vỡ diacritic ("đầu" → "đâ`u") |
| Voice | `anh_khoi` (alias) | `s_hochiminh_female_vyquangcao_advertise_vc` (Vy quảng cáo, SG female, **advertise** style) | Sau 4 lần iterate: news/storytelling voices flat by design; advertise voice cloning có vibe vui hào hứng |
| Speed bulletin | 1.05 | **1.0** | Iterate 1.05→0.95→1.0 final |
| Data input format | Excel/CSV (`lib/data_card.py`) | **JSON** inline | User chọn JSON. data_card.py chưa implement vì notebook Cell 2 đã đủ |
| Vbee API | "POC sync hay async" | **Async only** + polling | Postman doc confirm |
| Aspect ratio | 9:16 (1080x1920) | **1:1 vuông (1080x1080)** + 600x600 safe area | User muốn đa nền tảng — square master crop được 9:16 + 16:9 + 1:1 + 4:5 không mất content |
| Scene type names | `headline`/`quick_rank`/`kpi`/`outro` | **`intro`/`ranking`/`metric`/`outro`** | User yêu cầu rename cho gọn/semantic |

### Schema rich data fields (additive, optional)
- `IntroData.highlights[]` (text + appear_at_sec + style: stat/bullet) — bullets/stats hiện sync narration
- `MetricData.context_note` — caption text dưới delta
- `RankingData.summary_text` — sub-title dưới main title
- `OutroData.date_label` — date stamp đầu outro
- `RankItem.value` Optional + `value_suffix` (vd "tỷ", "điểm")
- `RankItem.appear_at_sec` — sync với narration

### Validator
- `MAX_NARRATION_CHARS_PER_SCENE` = 500 (bumped từ 300 vì intro rich >300 chars OK)
- `MIN_NARRATION_CHARS_PER_SCENE` = 5
- Layer 2 (data integrity) vẫn stub — cần user format data thật trước

### Vbee TTS notes (verified qua API query)
- 950+ voices vi-VN (VBEE + COMMUNITY ownership). API yêu cầu `voice_ownership` param (400 nếu thiếu).
- Không voice nào trả `has_emphasis: true` → `emphasis_intensity` param không khả dụng.
- SSML không hỗ trợ.
- Control ngữ điệu duy nhất qua punctuation: `,`/`.`/`!`/`?`/em-dash `—`. Đuôi "nhé!" cho rising tone.
- Voice cloning suffix `_vc` từ ownership COMMUNITY. Style suffix quyết định vibe: `_news_vc` flat/serious, `_stor_vc` storytelling, `_advertise_vc` energetic, `_talk_vc` conversational.

### Defer / chưa làm
- `lib/data_card.py` — Cell 2 trong notebook đã làm việc tương đương, defer module hoá đến khi có nhu cầu
- `scripts/sync_schema.py` — cần `json2ts` CLI từ npm `json-schema-to-typescript`. Hiện TS schema viết tay tại `remotion/src/templates/bulletin/schema.ts`
- Template `editorial_mystery` — Phase 2 (chưa start)
- Template `news_analysis` — Phase 3+ (chưa start)
- Subtitle in-code, audio ducking, programmatic LLM — roadmap

Resume detailed steps tại `memory.md` section "Resume from here".
