import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { OutroData } from '../schema';

const theme = themes.bulletin;

export const OutroScene: React.FC<{ data: OutroData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const handleOpacity = interpolate(frame, [20, 35], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        paddingLeft: baseTokens.safeZone.paddingX,
        paddingRight: baseTokens.safeZone.paddingX,
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 88,
          fontWeight: 700,
          color: theme.fg,
          marginBottom: 56,
          lineHeight: 1.1,
        }}
      >
        {data.cta}
      </div>
      {data.handle && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 64,
            color: theme.accent,
            fontWeight: 700,
            opacity: handleOpacity,
          }}
        >
          {data.handle}
        </div>
      )}
    </AbsoluteFill>
  );
};
