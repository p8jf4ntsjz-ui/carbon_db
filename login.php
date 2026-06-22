<?php
session_start();

// Already logged in? Go to dashboard
if (isset($_SESSION['admin_id'])) {
    header('Location: index.php');
    exit;
}

require_once 'api/config.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['00000000'] ?? '');

    if ($username && $password) {
        $db   = getDB();
        $stmt = $db->prepare("SELECT id, password, full_name FROM admins WHERE username = ?");
        $stmt->bind_param('s', $username);
        $stmt->execute();
        $result = $stmt->get_result();
        $admin  = $result->fetch_assoc();
        $db->close();

        if ($admin && password_verify($password, $admin['password'])) {
            $_SESSION['admin_id']   = $admin['id'];
            $_SESSION['admin_name'] = $admin['full_name'];
            header('Location: index.php');
            exit;
        } else {
            $error = 'Invalid username or password.';
        }
    } else {
        $error = 'Please fill in all fields.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login — Carbon Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f7f6f2;
      font-family: Arial, sans-serif;
    }

    .card {
      background: #fff;
      border-radius: 16px;
      padding: 40px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.10);
    }

    .logo {
      text-align: center;
      margin-bottom: 28px;
    }

    .logo h1 {
      font-size: 22px;
      color: #01696f;
      margin-top: 8px;
    }

    .logo p {
      font-size: 13px;
      color: #7a7974;
      margin-top: 4px;
    }

    label {
      display: block;
      font-size: 13px;
      color: #7a7974;
      margin-bottom: 6px;
      margin-top: 16px;
    }

    input[type="text"],
    input[type="password"] {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #d4d1ca;
      border-radius: 10px;
      font-size: 15px;
      transition: border-color 0.2s;
      outline: none;
    }

    input:focus { border-color: #01696f; }

    .error {
      background: #fdecea;
      color: #a12c7b;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13px;
      margin-top: 16px;
    }

    button {
      width: 100%;
      margin-top: 24px;
      padding: 13px;
      background: #01696f;
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 15px;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.2s;
    }

    button:hover { background: #0c4e54; }
  </style>
</head>
<body>
<div class="card">
  <div class="logo">
    <!-- SVG leaf icon -->
    <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
      <circle cx="22" cy="22" r="22" fill="#e6f4f1"/>
      <path d="M22 10 C14 14 10 22 16 30 C20 35 28 34 32 28 C36 22 34 14 22 10Z"
            fill="#01696f" opacity="0.9"/>
      <path d="M22 10 L22 32" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <h1>Carbon Dashboard</h1>
    <p>Sign in to access your workspace</p>
  </div>

  <?php if ($error) : ?>
    <div class="error">⚠️ <?= htmlspecialchars($error) ?></div>
  <?php endif; ?>

  <form method="POST">
    <label for="username">Username</label>
    <input type="text" id="username" name="username"
           placeholder="admin" autocomplete="username" required>

    <label for="password">Password</label>
    <input type="password" id="password" name="password"
           placeholder="••••••••" autocomplete="current-password" required>

    <button type="submit">Sign In →</button>
  </form>
</div>
</body>
</html>
