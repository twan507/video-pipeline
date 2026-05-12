export const themes = {
  bulletin: {
    bg: '#FFFFFF',
    fg: '#0A0A0A',
    accent: '#DC2626',
    secondary: '#525252',
    positive: '#16A34A',
    negative: '#DC2626',
  },
} as const;

export type ThemeName = keyof typeof themes;
