import { colors } from './colors';
import { spacing } from './spacing';
import { typography } from './typography';
import { radius } from './radius';
import { shadows } from './shadows';
import { animations } from './animations';

export const theme = {
  colors,
  spacing,
  typography,
  radius,
  shadows,
  animations,
};

export type ThemeTokensType = typeof theme;
export { colors, spacing, typography, radius, shadows, animations };
