<?php

require_once 'config.php';

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$db   = getDB();
$body = json_decode(file_get_contents('php://input'), true);
$type = $body['type'] ?? 'analyze';

$trend = $db->query(
    "SELECT DATE_FORMAT(date,'%Y-%m') as month, SUM(amount) as total"
    . " FROM emissions WHERE date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)"
    . " GROUP BY month ORDER BY month"
)->fetch_all(MYSQLI_ASSOC);
$cats = $db->query(
    "SELECT category, SUM(amount) as total, COUNT(*) as entries"
    . " FROM emissions WHERE YEAR(date)=YEAR(NOW())"
    . " GROUP BY category ORDER BY total DESC"
)->fetch_all(MYSQLI_ASSOC);
$cur = (float)$db->query(
    "SELECT COALESCE(SUM(amount), 0) as t FROM emissions"
    . " WHERE MONTH(date)=MONTH(NOW()) AND YEAR(date)=YEAR(NOW())"
)->fetch_assoc()['t'];
$prev = (float)$db->query(
    "SELECT COALESCE(SUM(amount), 0) as t FROM emissions"
    . " WHERE MONTH(date)=MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH))"
    . " AND YEAR(date)=YEAR(DATE_SUB(NOW(), INTERVAL 1 MONTH))"
)->fetch_assoc()['t'];
$tgt = (float)($db->query(
    "SELECT target_kg FROM monthly_targets"
    . " WHERE year=YEAR(NOW()) AND month=MONTH(NOW())"
)->fetch_assoc()['target_kg'] ?? 900);
$db->close();

$change_pct = $prev > 0 ? round((($cur - $prev) / $prev) * 100, 1) : 0;
$top_cat    = $cats[0]['category'] ?? 'unknown';
$top_val    = round((float)($cats[0]['total'] ?? 0), 1);
$on_track   = $cur <= $tgt;
$remaining  = round($tgt - $cur, 1);

if ($type === 'analyze') {
    $insights = [];
    $score = 100;

    if ($change_pct > 10) {
        $insights[] = "Spike detected: emissions rose {$change_pct}% vs last month.";
        $score -= 20;
    } elseif ($change_pct < -5) {
        $insights[] = "Great progress: emissions dropped " . abs($change_pct) . "% vs last month.";
        $score += 5;
    } else {
        $insights[] = "Stable month-over-month trend: {$change_pct}%.";
    }

    if (!$on_track) {
        $insights[] = "Target exceeded by " . round($cur - $tgt, 1) . " kg CO2e.";
        $score -= 25;
    } else {
        $insights[] = "On track with {$remaining} kg left before target.";
    }

    $insights[] = "Top category is {$top_cat} at {$top_val} kg CO2e.";
    $score = max(0, min(100, $score));

    echo json_encode([
        'type' => 'analysis',
        'score' => $score,
        'insights' => $insights
    ]);
}
