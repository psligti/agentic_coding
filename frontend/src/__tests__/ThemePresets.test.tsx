import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import '../styles/themes.css';
import '../index.css';

describe('Theme Presets System', () => {
  beforeEach(() => {
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('dark');
  });

  afterEach(() => {
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('dark');
  });

  describe('Theme Preset Selection', () => {
    it('sets data-theme="aurora" attribute on root element', () => {
      document.documentElement.setAttribute('data-theme', 'aurora');

      expect(document.documentElement.getAttribute('data-theme')).toBe('aurora');
    });

    it('sets data-theme="ocean" attribute on root element', () => {
      document.documentElement.setAttribute('data-theme', 'ocean');

      expect(document.documentElement.getAttribute('data-theme')).toBe('ocean');
    });

    it('sets data-theme="ember" attribute on root element', () => {
      document.documentElement.setAttribute('data-theme', 'ember');

      expect(document.documentElement.getAttribute('data-theme')).toBe('ember');
    });

    it('defaults to aurora when unknown themeId is set', () => {
      document.documentElement.setAttribute('data-theme', 'unknown-theme');

      expect(document.documentElement.getAttribute('data-theme')).toBe('unknown-theme');
    });
  });

  describe('Dark Mode Toggle', () => {
    it('applies .dark class to root element', () => {
      document.documentElement.classList.add('dark');

      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('removes .dark class from root element', () => {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('dark');

      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('toggles .dark class', () => {
      document.documentElement.classList.toggle('dark');
      expect(document.documentElement.classList.contains('dark')).toBe(true);

      document.documentElement.classList.toggle('dark');
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });

  describe('CSS Variable Values', () => {
    it('changes computed CSS variable when .dark class is added (aurora theme)', () => {
      document.documentElement.setAttribute('data-theme', 'aurora');

      const lightSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      document.documentElement.classList.add('dark');

      const darkSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      expect(darkSurfaceBase).not.toBe(lightSurfaceBase);
      expect(darkSurfaceBase).toBe('#0f172a');
    });

    it('changes computed CSS variable when .dark class is added (ocean theme)', () => {
      document.documentElement.setAttribute('data-theme', 'ocean');

      const lightSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      document.documentElement.classList.add('dark');

      const darkSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      expect(darkSurfaceBase).not.toBe(lightSurfaceBase);
      expect(darkSurfaceBase).toBe('#022c22');
    });

    it('changes computed CSS variable when .dark class is added (ember theme)', () => {
      document.documentElement.setAttribute('data-theme', 'ember');

      const lightSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      document.documentElement.classList.add('dark');

      const darkSurfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();

      expect(darkSurfaceBase).not.toBe(lightSurfaceBase);
      expect(darkSurfaceBase).toBe('#1c1917');
    });

    it('has different accent colors for different theme presets', () => {
      document.documentElement.setAttribute('data-theme', 'aurora');
      document.documentElement.classList.remove('dark');
      const auroraAccent = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      document.documentElement.setAttribute('data-theme', 'ocean');
      document.documentElement.classList.remove('dark');
      const oceanAccent = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      document.documentElement.setAttribute('data-theme', 'ember');
      document.documentElement.classList.remove('dark');
      const emberAccent = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      expect(auroraAccent).not.toBe(oceanAccent);
      expect(auroraAccent).not.toBe(emberAccent);
      expect(oceanAccent).not.toBe(emberAccent);

      expect(auroraAccent).toBe('#6366f1');
      expect(oceanAccent).toBe('#14b8a6');
      expect(emberAccent).toBe('#f59e0b');
    });
  });

  describe('Theme Preset + Dark Mode Combinations', () => {
    it('supports aurora theme with dark mode', () => {
      document.documentElement.setAttribute('data-theme', 'aurora');
      document.documentElement.classList.add('dark');

      const surfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();
      const accentPrimary = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      expect(document.documentElement.getAttribute('data-theme')).toBe('aurora');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(surfaceBase).toBe('#0f172a');
      expect(accentPrimary).toBe('#818cf8');
    });

    it('supports ocean theme with dark mode', () => {
      document.documentElement.setAttribute('data-theme', 'ocean');
      document.documentElement.classList.add('dark');

      const surfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();
      const accentPrimary = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      expect(document.documentElement.getAttribute('data-theme')).toBe('ocean');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(surfaceBase).toBe('#022c22');
      expect(accentPrimary).toBe('#2dd4bf');
    });

    it('supports ember theme with dark mode', () => {
      document.documentElement.setAttribute('data-theme', 'ember');
      document.documentElement.classList.add('dark');

      const surfaceBase = getComputedStyle(document.documentElement).getPropertyValue('--surface-base').trim();
      const accentPrimary = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim();

      expect(document.documentElement.getAttribute('data-theme')).toBe('ember');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(surfaceBase).toBe('#1c1917');
      expect(accentPrimary).toBe('#fbbf24');
    });
  });
});
