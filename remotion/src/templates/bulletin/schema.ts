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

export type HeadlineData = {
  headline: string;
  category: string;
  issue_label?: string | null;
};

export type RankItem = {
  rank: number;
  label: string;
  value: number;
  change_pct?: number | null;
};

export type QuickRankData = {
  title: string;
  items: RankItem[];
};

export type KPIData = {
  metric: string;
  current_value: number;
  previous_value: number;
  unit: string;
  delta?: number | null;
};

export type OutroData = {
  cta: string;
  handle?: string | null;
};

type SceneBase = {
  id: string;
  narration_text: string;
  audio_path?: string | null;
  duration: number;
};

export type HeadlineScene = SceneBase & { type: 'headline'; data: HeadlineData };
export type QuickRankScene = SceneBase & { type: 'quick_rank'; data: QuickRankData };
export type KPIScene = SceneBase & { type: 'kpi'; data: KPIData };
export type OutroScene = SceneBase & { type: 'outro'; data: OutroData };

export type Scene = HeadlineScene | QuickRankScene | KPIScene | OutroScene;

export type Script = {
  video_id: string;
  template: 'bulletin' | 'editorial_mystery' | 'news_analysis';
  meta: Meta;
  scenes: Scene[];
};
