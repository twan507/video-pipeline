import { interpolate, useCurrentFrame } from 'remotion';
import { SafeFrame } from '../../../shared/primitives/SafeFrame';
import { baseTokens } from '../../../shared/theme/tokens';
import { themes } from '../../../shared/theme/themes';
import type { MetricData } from '../schema';

const theme = themes.bulletin;

export const MetricScene: React.FC<{ data: MetricData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const valueProgress = interpolate(frame, [10, 45], [0, 1], { extrapolateRight: 'clamp' });
  const noteOpacity = interpolate(frame, [40, 60], [0, 1], { extrapolateRight: 'clamp' });
  const animatedValue =
    data.previous_value + (data.current_value - data.previous_value) * valueProgress;
  const delta = data.delta ?? data.current_value - data.previous_value;
  const deltaColor = delta >= 0 ? theme.positive : theme.negative;
  // Khi unit là "%" → delta tính theo điểm phần trăm ("đpt").
  // Còn lại (điểm, tỷ, ...) → dùng nguyên unit cho delta.
  const deltaUnit = data.unit === '%' ? 'đpt' : data.unit;

  return (
    <SafeFrame style={{ justifyContent: 'center', alignItems: 'center', textAlign: 'center', opacity }}>
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 24,
          color: theme.secondary,
          marginBottom: 24,
        }}
      >
        {data.metric}
      </div>
      <div
        style={{
          fontFamily: baseTokens.font.serif,
          fontSize: 140,
          fontWeight: 700,
          color: theme.fg,
          lineHeight: 1,
          marginBottom: 16,
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {animatedValue.toFixed(1)}
        <span style={{ fontSize: 56, color: theme.secondary }}>{data.unit}</span>
      </div>
      <div
        style={{
          fontFamily: baseTokens.font.sans,
          fontSize: 30,
          fontWeight: 700,
          color: deltaColor,
        }}
      >
        {delta >= 0 ? '▲' : '▼'} {delta >= 0 ? '+' : ''}
        {delta.toFixed(1)}
        {deltaUnit ? ` ${deltaUnit}` : ''}
      </div>
      {data.context_note && (
        <div
          style={{
            fontFamily: baseTokens.font.sans,
            fontSize: 18,
            color: theme.secondary,
            marginTop: 20,
            opacity: noteOpacity,
            textAlign: 'center',
          }}
        >
          {data.context_note}
        </div>
      )}
    </SafeFrame>
  );
};
