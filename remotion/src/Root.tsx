import { Composition, registerRoot, staticFile } from 'remotion';
import { BulletinComposition } from './templates/bulletin/Composition';
import type { Script } from './templates/bulletin/schema';

type Props = { scriptPath: string; script?: Script };

const loadScriptMetadata = async ({ props }: { props: Props }) => {
  const script: Script = await fetch(staticFile(props.scriptPath)).then((r) => r.json());
  const totalSec = script.scenes.reduce((s, sc) => s + sc.duration, 0);
  return {
    durationInFrames: Math.ceil(totalSec * 30),
    props: { ...props, script },
  };
};

const RemotionRoot: React.FC = () => (
  <Composition
    id="bulletin"
    component={BulletinComposition}
    defaultProps={{ scriptPath: 'runs/2026-05-12_W19_banking/script.json' } as Props}
    fps={30}
    width={1080}
    height={1920}
    durationInFrames={1}
    calculateMetadata={loadScriptMetadata}
  />
);

registerRoot(RemotionRoot);
