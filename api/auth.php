<?php

/**
 * api/auth.php
 *
 * Include at the top of every protected page.
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

if (!isset($_SESSION['admin_id'])) {
    header('Location: /carbon_db/login.php');
    exit;
}
