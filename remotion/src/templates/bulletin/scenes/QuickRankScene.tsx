import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { QuickRankData } from '../schema';

const theme = themes.bulletin;

export const QuickRankScene: React.FC<{ data: QuickRankData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        paddingLeft: baseTokens.safeZone.paddingX,
        paddingRight: baseTokens.safeZone.paddingX,
        paddingTop: baseTokens.safeZone.top,
        paddingBottom: baseTokens.safeZone.bottom,
      }}
    >
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 42,
          fontWeight: 700,
          color: theme.accent,
          marginBottom: 64,
          opacity: titleOpacity,
        }}
      >
        {data.title}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
        {data.items.map((item, idx) => {
          const itemStart = 15 + idx * 10;
          const itemOpacity = interpolate(frame, [itemStart, itemStart + 15], [0, 1], { extrapolateRight: 'clamp' });
          const itemX = interpolate(frame, [itemStart, itemStart + 15], [-40, 0], { extrapolateRight: 'clamp' });
          const changeColor =
            item.change_pct == null
              ? theme.secondary
              : item.change_pct >= 0
                ? theme.positive
                : theme.negative;
          return (
            <div
              key={item.rank}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 40,
                opacity: itemOpacity,
                transform: `translateX(${itemX}px)`,
              }}
            >
              <div
                style={{
                  fontFamily: baseTokens.font.serif,
                  fontSize: 96,
                  fontWeight: 700,
                  color: theme.accent,
                  minWidth: 100,
                  textAlign: 'center',
                }}
              >
                {item.rank}
              </div>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontFamily: baseTokens.font.sans,
                    fontSize: 64,
                    fontWeight: 700,
                    color: theme.fg,
                    lineHeight: 1.1,
                  }}
                >
                  {item.label}
                </div>
                <div
                  style={{
                    fontFamily: baseTokens.font.sans,
                    fontSize: 36,
                    color: theme.secondary,
                    marginTop: 8,
                  }}
                >
                  {item.value.toLocaleString('vi-VN')}
                  {item.change_pct != null && (
                    <span style={{ color: changeColor, marginLeft: 16, fontWeight: 700 }}>
                      {item.change_pct >= 0 ? '+' : ''}
                      {item.change_pct.toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
