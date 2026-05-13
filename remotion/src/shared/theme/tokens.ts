import { loadFont } from '@remotion/google-fonts/Roboto';

const { fontFamily: roboto } = loadFont('normal', {
  subsets: ['vietnamese', 'latin'],
  weights: ['400', '500', '700'],
});

// Master frame: 1080x1080 vuông để crop đa nền tảng.
// Critical safe area (600x600 ở giữa) = visible khi crop về 9:16 hoặc 16:9.
// Vùng ngoài critical safe = decorative/background, chỉ thấy ở format 1:1.
export const baseTokens = {
  font: {
    serif: roboto,
    sans: roboto,
  },
  spacing: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96] as const,
  fps: 30,
  master: { width: 1080, height: 1080 },
  safeZone: {
    // Hộp 600x600 giữa master 1080x1080. Tất cả text/số quan trọng phải nằm trong này.
    inner: 600,
    margin: 240, // (1080 - 600) / 2
    paddingX: 32, // padding bên trong inner safe để text không sát mép
  },
};
