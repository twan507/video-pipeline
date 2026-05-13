import { AbsoluteFill } from 'remotion';
import { baseTokens } from '../theme/tokens';

/**
 * Wrapper đặt content trong vùng 600x600 ở giữa master 1080x1080.
 * Content trong SafeFrame sẽ visible khi crop video về 9:16 / 16:9 / 1:1 / 4:5.
 * Bên ngoài SafeFrame (vùng padding 240px mỗi cạnh) chỉ thấy ở format 1:1.
 */
export const SafeFrame: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => {
  const sz = baseTokens.safeZone;
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div
        style={{
          width: sz.inner,
          height: sz.inner,
          paddingLeft: sz.paddingX,
          paddingRight: sz.paddingX,
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          ...style,
        }}
      >
        {children}
      </div>
    </AbsoluteFill>
  );
};
