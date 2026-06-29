import { colors, spacing, radius, shadows } from '../src/config/theme/theme';
import { useSidebarStore } from '../src/store/sidebarStore';

describe('Design System Integrity Tests', () => {
  test('Centralized colors tokens exist and contain light/dark definitions', () => {
    expect(colors.brand.primary.light).toBe('#3b82f6');
    expect(colors.brand.primary.dark).toBe('#60a5fa');
    expect(colors.semantic.light.background).toBe('#f8fafc');
    expect(colors.semantic.dark.background).toBe('#0f172a');
  });

  test('Spacing tokens define layout padding scales', () => {
    expect(spacing.xs).toBe('0.25rem');
    expect(spacing.layout.padding).toBe('1.5rem');
  });

  test('Radius tokens map rounded scales', () => {
    expect(radius.sm).toBe('4px');
    expect(radius.xl).toBe('16px');
  });

  test('Shadow tokens contain glassmorphism presets', () => {
    expect(shadows.glass).toContain('rgba(31, 38, 135, 0.07)');
  });

  test('Zustand Sidebar store expands and collapses correctly', () => {
    // Initial state
    expect(useSidebarStore.getState().isOpen).toBe(true);
    
    // Toggle
    useSidebarStore.getState().toggle();
    expect(useSidebarStore.getState().isOpen).toBe(false);
    
    // Reset
    useSidebarStore.getState().setOpen(true);
    expect(useSidebarStore.getState().isOpen).toBe(true);
  });
});
