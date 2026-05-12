import { Audio, interpolate, Sequence, staticFile } from 'remotion';
import { BackgroundLayer } from '../../shared/primitives/BackgroundLayer';
import { baseTokens } from '../../shared/theme/tokens';
import { SceneDispatcher } from './SceneDispatcher';
import type { Script } from './schema';

type Props = { scriptPath: string; script?: Script };

const BGM_VOLUME = 0.18;
const FADE_IN_FRAMES = 15;
const FADE_OUT_FRAMES = 30;

export const BulletinComposition: React.FC<Props> = ({ script, scriptPath }) => {
  if (!script) return null;

  const baseDir = scriptPath.replace(/\/script\.json$/, '');
  const totalFrames = script.scenes.reduce(
    (sum, s) => sum + Math.round(s.duration * baseTokens.fps),
    0,
  );
  const fadeOutStart = totalFrames - FADE_OUT_FRAMES;

  const bgmVolume = (frame: number) => {
    if (frame < FADE_IN_FRAMES) {
      return interpolate(frame, [0, FADE_IN_FRAMES], [0, BGM_VOLUME]);
    }
    if (frame > fadeOutStart) {
      return interpolate(frame, [fadeOutStart, totalFrames], [BGM_VOLUME, 0], {
        extrapolateRight: 'clamp',
      });
    }
    return BGM_VOLUME;
  };

  let cursor = 0;

  return (
    <>
      <BackgroundLayer theme="bulletin" />
      <Audio src={staticFile('music/bulletin_bgm.mp3')} volume={bgmVolume} />
      {script.scenes.map((scene) => {
        const dur = Math.round(scene.duration * baseTokens.fps);
        const from = cursor;
        cursor += dur;
        const audioSrc = scene.audio_path
          ? staticFile(`${baseDir}/${scene.audio_path}`)
          : null;
        return (
          <Sequence key={scene.id} from={from} durationInFrames={dur}>
            <SceneDispatcher scene={scene} />
            {audioSrc && <Audio src={audioSrc} />}
          </Sequence>
        );
      })}
    </>
  );
};
