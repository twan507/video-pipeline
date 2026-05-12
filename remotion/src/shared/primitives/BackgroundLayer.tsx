import { AbsoluteFill } from 'remotion';
import { themes, type ThemeName } from '../theme/themes';

export const BackgroundLayer: React.FC<{ theme: ThemeName }> = ({ theme }) => {
  const t = themes[theme];
  return <AbsoluteFill style={{ backgroundColor: t.bg }} />;
};
