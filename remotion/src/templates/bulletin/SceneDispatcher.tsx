import type { Scene } from './schema';
import { HeadlineScene } from './scenes/HeadlineScene';
import { QuickRankScene } from './scenes/QuickRankScene';
import { KPIScene } from './scenes/KPIScene';
import { OutroScene } from './scenes/OutroScene';

export const SceneDispatcher: React.FC<{ scene: Scene }> = ({ scene }) => {
  switch (scene.type) {
    case 'headline':
      return <HeadlineScene data={scene.data} />;
    case 'quick_rank':
      return <QuickRankScene data={scene.data} />;
    case 'kpi':
      return <KPIScene data={scene.data} />;
    case 'outro':
      return <OutroScene data={scene.data} />;
    default: {
      const _exhaustive: never = scene;
      throw new Error(`Unknown scene type: ${JSON.stringify(_exhaustive)}`);
    }
  }
};
