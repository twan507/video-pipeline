import { interpolate, useCurrentFrame } from 'remotion';
import { SafeFrame } from '../../../shared/primitives/SafeFrame';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { OutroData } from '../schema';

const theme = themes.bulletin;

export const OutroScene: React.FC<{ data: OutroData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const ctaOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const teaserOpacity = interpolate(frame, [18, 36], [0, 1], { extrapolateRight: 'clamp' });
  const handleOpacity = interpolate(frame, [36, 54], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <SafeFrame style={{ justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
      {data.date_label && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 16,
            color: theme.secondary,
            letterSpacing: 3,
            textTransform: 'uppercase',
            marginBottom: 24,
            opacity: ctaOpacity,
          }}
        >
          {data.date_label}
        </div>
      )}
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 52,
          fontWeight: 700,
          color: theme.fg,
          marginBottom: 28,
          lineHeight: 1.15,
          opacity: ctaOpacity,
        }}
      >
        {data.cta}
      </div>

      {data.next_topic && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 8,
            marginBottom: 32,
            opacity: teaserOpacity,
          }}
        >
          <div
            style={{
              fontFamily: baseTokens.font.sans,
              fontSize: 16,
              color: theme.secondary,
              letterSpacing: 3,
              textTransform: 'uppercase',
            }}
          >
            Số tiếp theo
          </div>
          <div
            style={{
              fontFamily: baseTokens.font.sans,
              fontSize: 32,
              fontWeight: 700,
              color: theme.accent,
            }}
          >
            {data.next_topic}
          </div>
        </div>
      )}

      {data.handle && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 32,
            color: theme.accent,
            fontWeight: 700,
            opacity: handleOpacity,
          }}
        >
          {data.handle}
        </div>
      )}
    </SafeFrame>
  );
};
