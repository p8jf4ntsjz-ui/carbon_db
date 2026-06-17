<?php

// ============================================================
//  FILE: api/import.php â€” CSV / Excel bulk import
//  POST multipart/form-data with field "file"
// ============================================================

require_once 'config.php';
setCorsHeaders();

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || empty($_FILES['file'])) {
    echo json_encode(['error' => 'POST a file with field name "file"']);
    exit;
}

$file = $_FILES['file'];
$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
$valid_cats = ['transport', 'energy', 'food', 'waste', 'shopping'];
$rows = [];

if ($ext === 'csv') {
    $handle = fopen($file['tmp_name'], 'r');
    fgetcsv($handle);

    while (($row = fgetcsv($handle)) !== false) {
        $rows[] = array_map('trim', $row);
    }

    fclose($handle);
} elseif (in_array($ext, ['xlsx', 'xls'], true)) {
    $autoload = __DIR__ . '/../vendor/autoload.php';

    if (!file_exists($autoload)) {
        echo json_encode(['error' => 'Excel needs PhpSpreadsheet. Run: composer require phpoffice/phpspreadsheet']);
        exit;
    }

    require_once $autoload;

    $sheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($file['tmp_name'])
        ->getActiveSheet()
        ->toArray();
    array_shift($sheet);
    $rows = $sheet;
} else {
    echo json_encode(['error' => 'Only .csv, .xlsx, .xls supported.']);
    exit;
}

$db = getDB();
$inserted = 0;
$skipped = 0;
$errors = [];

foreach ($rows as $i => $row) {
    $category = strtolower(trim($row[0] ?? ''));
    $subcategory = trim($row[1] ?? '');
    $amount = (float)($row[2] ?? 0);
    $date = trim($row[3] ?? '');
    $notes = trim($row[4] ?? '');

    if (!$category && !$date) {
        $skipped++;
        continue;
    }

    if (!in_array($category, $valid_cats, true)) {
        $errors[] = 'Row ' . ($i + 2) . ': unknown category "' . $category . '"';
        $skipped++;
        continue;
    }

    if ($amount < 0 || empty($date)) {
        $errors[] = 'Row ' . ($i + 2) . ': invalid amount or missing date';
        $skipped++;
        continue;
    }

    if (strpos($date, '/') !== false) {
        $p = explode('/', $date);

        if (count($p) === 3) {
            $date = strlen($p[2]) === 4
                ? "{$p[2]}-{$p[1]}-{$p[0]}"
                : "{$p[0]}-{$p[1]}-{$p[2]}";
        }
    }

    $cat = $db->real_escape_string($category);
    $sub = $db->real_escape_string($subcategory);
    $nt = $db->real_escape_string($notes);
    $dt = $db->real_escape_string($date);

    $db->query(
        "INSERT INTO emissions (category,subcategory,amount,date,notes) "
        . "VALUES ('$cat','$sub',$amount,'$dt','$nt')"
    );

    $inserted++;
}

$db->close();

echo json_encode([
    'success' => true,
    'inserted' => $inserted,
    'skipped' => $skipped,
    'errors' => $errors,
    'message' => "Imported {$inserted} rows. Skipped {$skipped}.",
]);
