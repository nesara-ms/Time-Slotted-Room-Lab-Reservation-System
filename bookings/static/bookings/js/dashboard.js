document.addEventListener('DOMContentLoaded', () => {
  const textEl = document.getElementById('greeting-text');
  const iconEl = document.getElementById('greeting-icon');
  if (!textEl || !iconEl) return;

  // Keeps the greeting in sync with the visitor's local time.
  function updateGreeting() {
    const hour = new Date().getHours();
    let text, icon;
    if (hour >= 5 && hour < 12) {
      text = 'Good Morning';   icon = '🌅';
    } else if (hour >= 12 && hour < 17) {
      text = 'Good Afternoon'; icon = '☀️';
    } else if (hour >= 17 && hour < 21) {
      text = 'Good Evening';   icon = '🌇';
    } else {
      text = 'Good Night';     icon = '🌙';
    }
    textEl.textContent = text;
    iconEl.textContent = icon;
  }

  updateGreeting();
  setInterval(updateGreeting, 60 * 1000);
});