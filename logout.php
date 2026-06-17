<?php

/**
 * logout.php
 *
 * Log out the current user and redirect to login.
 */

session_start();
session_destroy();
header('Location: login.php');
exit;
