<?php $page = 'list'; ?>
<!DOCTYPE html>
<html lang="fr" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Émissions — Carbon Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/app.js" defer></script>
</head>
<body>
<div id="sidebar-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:199;"></div>
<div class="app-layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-logo">
      <div class="logo-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12"/><polyline points="12 6 12 12 16 14"/></svg></div>
      <span class="logo-text">CarbonTrack<span>Empreinte carbone</span></span>
    </div>
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li><a href="index.php" class="nav-link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>Tableau de bord</a></li>
        <li><a href="add.php" class="nav-link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>Ajouter</a></li>
        <li><a href="list.php" class="nav-link active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/></svg>Toutes les émissions</a></li>
        <li><a href="stats.php" class="nav-link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>Statistiques</a></li>
      </ul>
    </nav>
    <div class="sidebar-footer">
      <button class="btn-theme" id="theme-btn" aria-label="Thème"></button>
      <span style="flex:1;font-size:var(--text-xs);color:var(--color-text-muted)">Thème</span>
    </div>
  </aside>

  <div class="main-content">
    <header class="topbar">
      <button class="menu-btn" id="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="sidebar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <span class="topbar-title">Toutes les émissions</span>
      <div class="topbar-right">
        <span class="topbar-time" id="topbar-time"></span>
        <div class="topbar-avatar">U</div>
      </div>
    </header>

    <main class="page-content">
      <div class="page-header">
        <div class="page-header-left">
          <h2>Toutes les émissions</h2>
          <p>Historique complet de vos activités</p>
        </div>
        <div class="page-header-right">
          <a href="add.php" class="btn btn-primary">+ Nouvelle entrée</a>
        </div>
      </div>

      <div class="filter-bar">
        <select class="filter-select" id="filter-category" aria-label="Catégorie">
          <option value="">Toutes les catégories</option>
          <option value="transport">Transport</option>
          <option value="energy">Énergie</option>
          <option value="food">Alimentation</option>
          <option value="waste">Déchets</option>
          <option value="shopping">Achats</option>
          <option value="other">Autre</option>
        </select>
        <input type="date" class="filter-select" id="filter-from" aria-label="Du">
        <input type="date" class="filter-select" id="filter-to" aria-label="Au">
        <button class="btn btn-ghost btn-sm" id="btn-filter">Filtrer</button>
        <button class="btn btn-outline btn-sm" id="btn-reset-filter">Réinitialiser</button>
      </div>

      <div class="card">
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Date</th><th>Catégorie</th><th>Sous-catégorie</th>
                <th>Émissions</th><th>Notes</th><th></th>
              </tr>
            </thead>
            <tbody id="recent-tbody">
              <tr><td colspan="6" style="text-align:center;padding:var(--space-8);color:var(--color-text-muted)">Chargement…</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</div>
<div class="toast-container" id="toast-container" aria-live="polite"></div>
<script>
  document.getElementById('btn-filter')?.addEventListener('click', () => {
    const cat  = document.getElementById('filter-category').value;
    const from = document.getElementById('filter-from').value;
    const to   = document.getElementById('filter-to').value;
    currentFilter = { category: cat, from, to };
    loadRecentTable();
  });
  document.getElementById('btn-reset-filter')?.addEventListener('click', () => {
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-from').value = '';
    document.getElementById('filter-to').value = '';
    currentFilter = {};
    loadRecentTable();
  });
</script>
</body>
</html>