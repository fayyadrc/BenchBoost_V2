import { useState, useEffect } from 'react';

type Theme = 'dark' | 'light';

const THEME_KEY = 'fpl_theme';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem(THEME_KEY) as Theme) || 'dark';
    }
    return 'dark';
  });

  const isDark = theme === 'dark';

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem(THEME_KEY, newTheme);
  };

  // Apply theme to document
  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  return { theme, isDark, toggleTheme };
}
