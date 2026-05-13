// Manual TypeScript types mirroring lib/schema.py.
// TODO Phase 2: auto-generate via scripts/sync_schema.py.

export type Meta = {
  title: string;
  voice: string;
  speed: number;
  fps: number;
  width: number;
  height: number;
  created_at: string;
};

export type IntroHighlight = {
  text: string;
  appear_at_sec: number;
  style?: 'stat' | 'bullet';
};

export type IntroData = {
  headline: string;
  category: string;
  issue_label?: string | null;
  highlights?: IntroHighlight[] | null;
};

export type RankItem = {
  rank: number;
  label: string;
  value?: number | null;
  value_suffix?: string | null;
  change_pct?: number | null;
  appear_at_sec?: number | null;
};

export type RankingData = {
  title: string;
  summary_text?: string | null;
  items: RankItem[];
};

export type MetricData = {
  metric: string;
  current_value: number;
  previous_value: number;
  unit: string;
  delta?: number | null;
  context_note?: string | null;
};

export type OutroData = {
  cta: string;
  handle?: string | null;
  next_topic?: string | null;
  date_label?: string | null;
};

type SceneBase = {
  id: string;
  narration_text: string;
  audio_path?: string | null;
  duration: number;
};

export type IntroScene = SceneBase & { type: 'intro'; data: IntroData };
export type RankingScene = SceneBase & { type: 'ranking'; data: RankingData };
export type MetricScene = SceneBase & { type: 'metric'; data: MetricData };
export type OutroScene = SceneBase & { type: 'outro'; data: OutroData };

export type Scene = IntroScene | RankingScene | MetricScene | OutroScene;

export type Script = {
  video_id: string;
  template: 'bulletin' | 'editorial_mystery' | 'news_analysis';
  meta: Meta;
  scenes: Scene[];
};
