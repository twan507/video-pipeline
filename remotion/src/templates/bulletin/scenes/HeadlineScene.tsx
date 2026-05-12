import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { HeadlineData } from '../schema';

const theme = themes.bulletin;

export const HeadlineScene: React.FC<{ data: HeadlineData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, 15], [40, 0], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        paddingLeft: baseTokens.safeZone.paddingX,
        paddingRight: baseTokens.safeZone.paddingX,
        paddingTop: baseTokens.safeZone.top,
        paddingBottom: baseTokens.safeZone.bottom,
        justifyContent: 'center',
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 36,
          fontWeight: 700,
          color: theme.accent,
          letterSpacing: 4,
          textTransform: 'uppercase',
          marginBottom: 24,
        }}
      >
        {data.category}
      </div>
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 96,
          fontWeight: 700,
          color: theme.fg,
          lineHeight: 1.1,
          marginBottom: 32,
        }}
      >
        {data.headline}
      </div>
      {data.issue_label && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 28,
            color: theme.secondary,
          }}
        >
          {data.issue_label}
        </div>
      )}
    </AbsoluteFill>
  );
};
