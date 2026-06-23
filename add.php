<?php $page = 'add'; ?>
<!DOCTYPE html>
<html lang="fr" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ajouter — Carbon Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/app.js" defer></script>
</head>
<body>
<div id="sidebar-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:199;"></div>
<div class="app-layout">

  <aside class="sidebar" id="sidebar">
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <span class="logo-text">CarbonTrack<span>Empreinte carbone</span></span>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section">
        <ul class="nav-list">
          <li><a href="index.php" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            Tableau de bord</a></li>
          <li><a href="add.php" class="nav-link active">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
            Ajouter une émission</a></li>
          <li><a href="list.php" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/></svg>
            Toutes les émissions</a></li>
          <li><a href="stats.php" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Statistiques</a></li>
        </ul>
      </div>
    </nav>
    <div class="sidebar-footer">
      <button class="btn-theme" id="theme-btn" aria-label="Changer le thème"></button>
      <span style="flex:1;font-size:var(--text-xs);color:var(--color-text-muted)">Thème</span>
    </div>
  </aside>

  <div class="main-content">
    <header class="topbar">
      <button class="menu-btn" id="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="sidebar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <span class="topbar-title">Ajouter une émission</span>
      <div class="topbar-right">
        <span class="topbar-time" id="topbar-time"></span>
        <div class="topbar-avatar">U</div>
      </div>
    </header>

    <main class="page-content">
      <div class="page-header">
        <div class="page-header-left">
          <h2>Nouvelle émission</h2>
          <p>Enregistrez une activité et son impact carbone</p>
        </div>
        <div class="page-header-right">
          <a href="index.php" class="btn btn-ghost">← Retour</a>
        </div>
      </div>

      <div class="form-panel" style="max-width:700px">
        <form id="add-form" novalidate>
          <div class="form-grid">
            <div class="form-group">
              <label for="f-category">Catégorie *</label>
              <select id="f-category" name="category" required>
                <option value="">— Sélectionner —</option>
                <option value="transport">🚗 Transport</option>
                <option value="energy">⚡ Énergie</option>
                <option value="food">🥗 Alimentation</option>
                <option value="waste">🗑️ Déchets</option>
                <option value="shopping">🛍️ Achats</option>
                <option value="other">📦 Autre</option>
              </select>
            </div>
            <div class="form-group">
              <label for="f-sub">Sous-catégorie</label>
              <input type="text" id="f-sub" name="subcategory" placeholder="ex : Voiture, Électricité…">
            </div>
            <div class="form-group">
              <label for="f-amount">Quantité kg CO₂e *</label>
              <input type="number" id="f-amount" name="amount" min="0.01" step="0.01" placeholder="45.20" required>
            </div>
            <div class="form-group">
              <label for="f-date">Date *</label>
              <input type="date" id="f-date" name="date" required>
            </div>
            <div class="form-group full">
              <label for="f-notes">Notes</label>
              <textarea id="f-notes" name="notes" placeholder="Description optionnelle…"></textarea>
            </div>
          </div>
          <div class="form-actions">
            <button type="reset" class="btn btn-ghost">Réinitialiser</button>
            <button type="submit" class="btn btn-primary">Ajouter l'entrée</button>
          </div>
        </form>
      </div>

      <!-- Référentiel rapide -->
      <div class="card" style="max-width:700px;margin-top:var(--space-6)">
        <div class="card-header"><h3>Référentiel kg CO₂e</h3></div>
        <div class="card-body">
          <table>
            <thead><tr><th>Activité</th><th>Valeur estimée</th></tr></thead>
            <tbody>
              <tr><td>Voiture essence (100 km)</td><td class="font-mono">21 kg CO₂e</td></tr>
              <tr><td>Vol Paris–Tunis</td><td class="font-mono">180 kg CO₂e</td></tr>
              <tr><td>1 kg de bœuf</td><td class="font-mono">27 kg CO₂e</td></tr>
              <tr><td>1 kWh électricité (FR)</td><td class="font-mono">0.05 kg CO₂e</td></tr>
              <tr><td>1 kWh gaz naturel</td><td class="font-mono">0.23 kg CO₂e</td></tr>
              <tr><td>Smartphone neuf</td><td class="font-mono">70 kg CO₂e</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</div>
<div class="toast-container" id="toast-container" aria-live="polite"></div>
</body>
</html>