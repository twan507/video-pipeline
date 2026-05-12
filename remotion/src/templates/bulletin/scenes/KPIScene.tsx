import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { KPIData } from '../schema';

const theme = themes.bulletin;

export const KPIScene: React.FC<{ data: KPIData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const valueProgress = interpolate(frame, [10, 45], [0, 1], { extrapolateRight: 'clamp' });
  const animatedValue =
    data.previous_value + (data.current_value - data.previous_value) * valueProgress;
  const delta = data.delta ?? data.current_value - data.previous_value;
  const deltaColor = delta >= 0 ? theme.positive : theme.negative;

  return (
    <AbsoluteFill
      style={{
        paddingLeft: baseTokens.safeZone.paddingX,
        paddingRight: baseTokens.safeZone.paddingX,
        paddingTop: baseTokens.safeZone.top,
        paddingBottom: baseTokens.safeZone.bottom,
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 40,
          color: theme.secondary,
          marginBottom: 48,
        }}
      >
        {data.metric}
      </div>
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 240,
          fontWeight: 700,
          color: theme.fg,
          lineHeight: 1,
          marginBottom: 32,
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {animatedValue.toFixed(1)}
        <span style={{ fontSize: 96, color: theme.secondary }}>{data.unit}</span>
      </div>
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 48,
          fontWeight: 700,
          color: deltaColor,
        }}
      >
        {delta >= 0 ? '▲' : '▼'} {delta >= 0 ? '+' : ''}
        {delta.toFixed(1)} đpt
      </div>
    </AbsoluteFill>
  );
};
