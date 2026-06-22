// ─── SIDEBAR MOBILE TOGGLE ───────────────────────────────────
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
if (menuToggle && sidebar) {
  menuToggle.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', open);
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
      sidebar.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// ─── AVATAR INITIALS FROM SESSION ───────────────────────────
const avatarEl = document.getElementById('avatar-initials');
if (avatarEl) {
  const nameEl = document.querySelector('meta[name="user-name"]');
  if (nameEl) avatarEl.textContent = nameEl.content.charAt(0).toUpperCase();
}

// ─── NOTIFICATION BADGE ─────────────────────────────────────
async function loadNotifCount() {
  try {
    const res = await fetch('/api/notifications/unread-count');
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById('notif-badge');
    const dot = document.getElementById('notif-dot');
    if (data.count > 0) {
      if (badge) { badge.textContent = data.count > 99 ? '99+' : data.count; badge.style.display = 'inline'; }
      if (dot) dot.style.display = 'block';
    }
  } catch {}
}
loadNotifCount();

// ─── KPI COUNTER ANIMATION ───────────────────────────────────
function animateCount(el) {
  const target = parseInt(el.getAttribute('data-count') || el.textContent, 10);
  if (isNaN(target)) return;
  let start = 0;
  const duration = 800;
  const startTime = performance.now();
  const step = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(start + (target - start) * ease).toLocaleString('fr-FR');
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
document.querySelectorAll('.kpi-value[data-count]').forEach(animateCount);

// ─── AUTO-CLOSE FLASH MESSAGES ───────────────────────────────
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => flash.remove(), 5000);
});

// ─── FORM VALIDATION ─────────────────────────────────────────
document.querySelectorAll('form[novalidate]').forEach(form => {
  form.addEventListener('submit', (e) => {
    let valid = true;
    form.querySelectorAll('[required]').forEach(field => {
      const error = field.parentElement.querySelector('.field-error');
      if (!field.value.trim()) {
        valid = false;
        field.setAttribute('aria-invalid', 'true');
        field.style.borderColor = 'var(--color-error)';
        if (error) error.textContent = 'Ce champ est obligatoire.';
      } else {
        field.setAttribute('aria-invalid', 'false');
        field.style.borderColor = '';
        if (error) error.textContent = '';
      }
    });
    if (!valid) e.preventDefault();
  });
});

// ─── SCORE BAR COLORS ────────────────────────────────────────
document.querySelectorAll('.score-fill[data-score]').forEach(el => {
  const score = parseInt(el.dataset.score, 10);
  if (score >= 70) el.style.background = 'var(--color-success)';
  else if (score >= 40) el.style.background = 'var(--color-warning)';
  else el.style.background = 'var(--color-error)';
});

// ─── KEYBOARD TRAP IN MODALS ─────────────────────────────────
document.querySelectorAll('[role="dialog"]').forEach(modal => {
  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modal.classList.add('hidden');
    }
    if (e.key === 'Tab') {
      const focusable = modal.querySelectorAll('button,input,select,textarea,a[href]');
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
});