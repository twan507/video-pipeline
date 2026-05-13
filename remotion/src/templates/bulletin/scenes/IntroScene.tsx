import { interpolate, useCurrentFrame } from 'remotion';
import { SafeFrame } from '../../../shared/primitives/SafeFrame';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { IntroData, IntroHighlight } from '../schema';

const theme = themes.bulletin;

const Highlight: React.FC<{ h: IntroHighlight; frame: number }> = ({ h, frame }) => {
  const start = Math.round(h.appear_at_sec * 30);
  const opacity = interpolate(frame, [start, start + 18], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [start, start + 18], [16, 0], { extrapolateRight: 'clamp' });

  if (h.style === 'stat') {
    return (
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 64,
          fontWeight: 700,
          color: theme.accent,
          lineHeight: 1.1,
          opacity,
          transform: `translateY(${y}px)`,
        }}
      >
        {h.text}
      </div>
    );
  }
  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        alignItems: 'flex-start',
        fontFamily: baseTokens.font.sans,
        fontSize: 22,
        color: theme.fg,
        lineHeight: 1.3,
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      <span style={{ color: theme.accent, fontWeight: 700, flexShrink: 0 }}>▸</span>
      <span>{h.text}</span>
    </div>
  );
};

export const IntroScene: React.FC<{ data: IntroData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const headerOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const headerY = interpolate(frame, [0, 15], [40, 0], { extrapolateRight: 'clamp' });

  return (
    <SafeFrame style={{ justifyContent: 'space-between' }}>
      <div style={{ opacity: headerOpacity, transform: `translateY(${headerY}px)` }}>
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 20,
            fontWeight: 700,
            color: theme.accent,
            letterSpacing: 3,
            textTransform: 'uppercase',
            marginBottom: 12,
          }}
        >
          {data.category}
        </div>
        <div
          style={{
            fontFamily: baseTokens.font.serif,
            fontSize: 52,
            fontWeight: 700,
            color: theme.fg,
            lineHeight: 1.1,
          }}
        >
          {data.headline}
        </div>
      </div>

      {data.highlights && data.highlights.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 24 }}>
          {data.highlights.map((h, idx) => (
            <Highlight key={idx} h={h} frame={frame} />
          ))}
        </div>
      )}

      {data.issue_label && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 18,
            color: theme.secondary,
            marginTop: 16,
          }}
        >
          {data.issue_label}
        </div>
      )}
    </SafeFrame>
  );
};
