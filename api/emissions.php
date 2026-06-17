<?php

require_once 'config.php';

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$db = getDB();
$action = $_GET['action'] ?? 'list';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if ($action === 'summary') {
        $cur = $db->query(
            "SELECT SUM(amount) as t FROM emissions"
            . " WHERE MONTH(date)=MONTH(NOW()) AND YEAR(date)=YEAR(NOW())"
        )->fetch_assoc();
        $prev = $db->query(
            "SELECT SUM(amount) as t FROM emissions"
            . " WHERE MONTH(date)=MONTH(DATE_SUB(NOW(),INTERVAL 1 MONTH))"
            . " AND YEAR(date)=YEAR(DATE_SUB(NOW(),INTERVAL 1 MONTH))"
        )->fetch_assoc();
        $ytd = $db->query(
            "SELECT SUM(amount) as t FROM emissions WHERE YEAR(date)=YEAR(NOW())"
        )->fetch_assoc();
        $tgt = $db->query(
            "SELECT target_kg FROM monthly_targets"
            . " WHERE year=YEAR(NOW()) AND month=MONTH(NOW())"
        )->fetch_assoc();
        echo json_encode([
            'current_month'  => (float)($cur['t'] ?? 0),
            'previous_month' => (float)($prev['t'] ?? 0),
            'year_to_date'   => (float)($ytd['t'] ?? 0),
            'monthly_target' => (float)($tgt['target_kg'] ?? 900)
        ]);
    } elseif ($action === 'trend') {
        $r = $db->query(
            "SELECT DATE_FORMAT(date,'%Y-%m') as month, SUM(amount) as total_kg"
            . " FROM emissions WHERE date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)"
            . " GROUP BY month ORDER BY month"
        );
        echo json_encode($r->fetch_all(MYSQLI_ASSOC));
    } elseif ($action === 'by_category') {
        $r = $db->query(
            "SELECT category, SUM(amount) as total_kg FROM emissions"
            . " WHERE YEAR(date)=YEAR(NOW())"
            . " GROUP BY category ORDER BY total_kg DESC"
        );
        echo json_encode($r->fetch_all(MYSQLI_ASSOC));
    } elseif ($action === 'list') {
        $r = $db->query("SELECT * FROM emissions ORDER BY date DESC LIMIT 20");
        echo json_encode($r->fetch_all(MYSQLI_ASSOC));
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $d = json_decode(file_get_contents('php://input'), true);
    $cat = $db->real_escape_string($d['category']);
    $sub = $db->real_escape_string($d['subcategory'] ?? '');
    $amt = (float)$d['amount'];
    $date = $db->real_escape_string($d['date']);
    $note = $db->real_escape_string($d['notes'] ?? '');
    $db->query(
        "INSERT INTO emissions (category,subcategory,amount,date,notes)"
        . " VALUES ('$cat','$sub',$amt,'$date','$note')"
    );
    echo json_encode(['success' => true, 'id' => $db->insert_id]);
}

$db->close();
