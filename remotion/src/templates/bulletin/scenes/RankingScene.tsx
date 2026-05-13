import { interpolate, useCurrentFrame } from 'remotion';
import { SafeFrame } from '../../../shared/primitives/SafeFrame';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { RankingData } from '../schema';

const theme = themes.bulletin;

export const RankingScene: React.FC<{ data: RankingData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const summaryOpacity = interpolate(frame, [10, 25], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <SafeFrame style={{ justifyContent: 'flex-start', paddingTop: 32 }}>
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 26,
          fontWeight: 700,
          color: theme.accent,
          marginBottom: data.summary_text ? 8 : 32,
          opacity: titleOpacity,
        }}
      >
        {data.title}
      </div>
      {data.summary_text && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 20,
            color: theme.fg,
            fontWeight: 700,
            marginBottom: 28,
            opacity: summaryOpacity,
          }}
        >
          {data.summary_text}
        </div>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        {data.items.map((item, idx) => {
          // Sync với narration: dùng appear_at_sec từ script nếu có,
          // fallback spread 3s/item bắt đầu sau 0.5s.
          const itemStart =
            item.appear_at_sec != null
              ? Math.round(item.appear_at_sec * 30)
              : 15 + idx * 90;
          const itemOpacity = interpolate(frame, [itemStart, itemStart + 20], [0, 1], { extrapolateRight: 'clamp' });
          const itemX = interpolate(frame, [itemStart, itemStart + 20], [-40, 0], { extrapolateRight: 'clamp' });
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
                gap: 24,
                opacity: itemOpacity,
                transform: `translateX(${itemX}px)`,
              }}
            >
              <div
                style={{
                  fontFamily: baseTokens.font.serif,
                  fontSize: 56,
                  fontWeight: 700,
                  color: theme.accent,
                  minWidth: 60,
                  textAlign: 'center',
                }}
              >
                {item.rank}
              </div>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontFamily: baseTokens.font.sans,
                    fontSize: 38,
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
                    fontSize: 22,
                    color: theme.secondary,
                    marginTop: 4,
                  }}
                >
                  {item.value != null && (
                    <span style={{ color: item.value < 0 ? theme.negative : theme.secondary, fontWeight: item.value < 0 ? 700 : 400 }}>
                      {item.value.toLocaleString('vi-VN')}
                      {item.value_suffix ? ` ${item.value_suffix}` : ''}
                    </span>
                  )}
                  {item.change_pct != null && (
                    <span style={{ color: changeColor, marginLeft: 12, fontWeight: 700 }}>
                      {item.change_pct >= 0 ? '+' : ''}
                      {item.change_pct.toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </SafeFrame>
  );
};
