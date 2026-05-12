import { loadFont } from '@remotion/google-fonts/Roboto';

const { fontFamily: roboto } = loadFont('normal', {
  subsets: ['vietnamese', 'latin'],
  weights: ['400', '500', '700'],
});

export const baseTokens = {
  font: {
    serif: roboto,
    sans: roboto,
  },
  spacing: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96] as const,
  fps: 30,
  safeZone: { top: 200, bottom: 480, paddingX: 80 },
};
