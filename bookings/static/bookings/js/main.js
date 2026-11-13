document.addEventListener('DOMContentLoaded', () => {
  // Mobile navigation toggle
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // Dismiss alerts (click the x, or auto-hide success messages)
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => btn.parentElement.remove());
  });
  document.querySelectorAll('.messages .alert-success').forEach(el => {
    setTimeout(() => el.remove(), 5000);
  });

  // Confirmation prompts: <form data-confirm="Are you sure?">
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});