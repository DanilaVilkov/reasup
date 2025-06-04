// theme-toggle.js
// Логика переключения светлой/тёмной темы и сохранения выбора в localStorage

(function() {
  const root = document.documentElement;
  const toggleButton = document.getElementById('theme-toggle');
  const iconSun = document.getElementById('icon-sun');
  const iconMoon = document.getElementById('icon-moon');

  // Устанавливаем тему при загрузке страницы
  function initTheme() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
      root.classList.toggle('dark', storedTheme === 'dark');
    } else {
      // Если нет сохранённого значения, ориентируемся на системные настройки
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    }
    updateIcons();
  }

  // Меняем иконки в кнопке в зависимости от текущей темы
  function updateIcons() {
    if (root.classList.contains('dark')) {
      iconSun.classList.remove('block');
      iconSun.classList.add('hidden');
      iconMoon.classList.remove('hidden');
      iconMoon.classList.add('block');
    } else {
      iconMoon.classList.remove('block');
      iconMoon.classList.add('hidden');
      iconSun.classList.remove('hidden');
      iconSun.classList.add('block');
    }
  }

  // Переключаем тему по клику
  function toggleTheme() {
    const isDark = root.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateIcons();
  }

  document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    // Вешаем обработчик на кнопку
    if (toggleButton) {
      toggleButton.addEventListener('click', toggleTheme);
    }
  });
})();
