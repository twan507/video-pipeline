import type { Scene } from './schema';
import { IntroScene } from './scenes/IntroScene';
import { RankingScene } from './scenes/RankingScene';
import { MetricScene } from './scenes/MetricScene';
import { OutroScene } from './scenes/OutroScene';

export const SceneDispatcher: React.FC<{ scene: Scene }> = ({ scene }) => {
  switch (scene.type) {
    case 'intro':
      return <IntroScene data={scene.data} />;
    case 'ranking':
      return <RankingScene data={scene.data} />;
    case 'metric':
      return <MetricScene data={scene.data} />;
    case 'outro':
      return <OutroScene data={scene.data} />;
    default: {
      const _exhaustive: never = scene;
      throw new Error(`Unknown scene type: ${JSON.stringify(_exhaustive)}`);
    }
  }
};
