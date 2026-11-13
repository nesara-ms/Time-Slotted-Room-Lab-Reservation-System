document.addEventListener('DOMContentLoaded', () => {
  // Auto-submit the filter form when date or type changes
  const form = document.getElementById('calendar-filter');
  ['cal-date', 'cal-type'].forEach(id => {
    const el = document.getElementById(id);
    if (el && form) el.addEventListener('change', () => form.submit());
  });

  // Highlight the current hour column when viewing today
  const table = document.getElementById('calendar-table');
  if (table && table.dataset.today === '1') {
    const hour = String(new Date().getHours());
    table.querySelectorAll('[data-hour]').forEach(el => {
      if (el.dataset.hour === hour || el.dataset.hour === hour.padStart(2, '0')) {
        el.classList.add(el.tagName === 'TH' ? 'now' : 'now-col');
      }
    });
  }

  // Tooltip with booking details
  const tip = document.createElement('div');
  tip.className = 'tooltip';
  document.body.appendChild(tip);

  const show = (cell) => {
    const info = cell.dataset.info;
    if (!info) return;
    tip.textContent = info.split(' | ').join('\n');
    tip.style.whiteSpace = 'pre-line';
    const r = cell.getBoundingClientRect();
    tip.style.left = Math.max(8, Math.min(r.left, window.innerWidth - 290)) + 'px';
    tip.style.top = (r.bottom + 6) + 'px';
    tip.classList.add('show');
  };
  const hide = () => tip.classList.remove('show');

  document.querySelectorAll('.slot[data-info]').forEach(cell => {
    if (!cell.dataset.info) return;
    cell.addEventListener('mouseenter', () => show(cell));
    cell.addEventListener('mouseleave', hide);
    cell.addEventListener('click', () => { show(cell); setTimeout(hide, 2500); });
  });
});