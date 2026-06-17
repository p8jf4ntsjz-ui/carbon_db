<?php
require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/api/config.php';

use PhpOffice\PhpSpreadsheet\IOFactory;

$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['excel'])) {
    $tmp  = $_FILES['excel']['tmp_name'];
    $name = $_FILES['excel']['name'];
    $ext  = strtolower(pathinfo($name, PATHINFO_EXTENSION));

    if (!in_array($ext, ['xlsx', 'xls', 'csv'])) {
        $message = "âŒ Only .xlsx, .xls, or .csv files allowed.";
    } else {
        $spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($tmp);
        $rows        = $spreadsheet->getActiveSheet()->toArray();
        $db          = getDB();
        $inserted    = 0;

        foreach (array_slice($rows, 1) as $row) {
            $category    = trim($row[0] ?? '');
            $subcategory = trim($row[1] ?? '');
            $amount      = floatval($row[2] ?? 0);
            $date        = trim($row[3] ?? '');
            $notes       = trim($row[4] ?? '');

            if (empty($category) || empty($date) || $amount <= 0) {
                continue;
            }

            if (strpos($date, '/') !== false) {
                $d    = DateTime::createFromFormat('d/m/Y', $date);
                $date = $d ? $d->format('Y-m-d') : $date;
            }

            $cat  = $db->real_escape_string($category);
            $sub  = $db->real_escape_string($subcategory);
            $note = $db->real_escape_string($notes);
            $dt   = $db->real_escape_string($date);

            $db->query("INSERT INTO emissions (category, subcategory, amount, date, notes)
                        VALUES ('$cat', '$sub', $amount, '$dt', '$note')");
            $inserted++;
        }

        $db->close();
        $message = "âœ… Successfully imported <strong>$inserted</strong> rows!";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Import Excel Data</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f0;
           display: flex; align-items: center; justify-content: center;
           min-height: 100vh; padding: 24px; }
    .card { background: white; border-radius: 16px; padding: 40px;
            max-width: 500px; width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    h2 { margin-bottom: 8px; }
    p  { color: #888; font-size: 14px; margin-bottom: 24px; }
    .drop-zone { border: 2px dashed #01696f; border-radius: 12px;
                 padding: 40px; text-align: center; color: #01696f;
                 cursor: pointer; margin-bottom: 20px; transition: background 0.2s; }
    .drop-zone:hover { background: #f0fafa; }
    input[type="file"] { display: none; }
    button { width: 100%; padding: 14px; background: #01696f; color: white;
             border: none; border-radius: 10px; font-size: 16px;
             font-weight: 600; cursor: pointer; }
    button:hover { background: #0c4e54; }
    .message { margin-top: 20px; padding: 14px; border-radius: 10px;
               background: #f0faf5; color: #065f46; font-size: 14px; }
    .columns { background: #f8f8f8; border-radius: 10px; padding: 16px;
               margin-bottom: 20px; font-size: 13px; }
    .columns code { background: #e5e5e5; padding: 2px 6px;
                    border-radius: 4px; font-size: 12px; }
    a { color: #01696f; font-size: 14px; display: inline-block; margin-top: 16px; }
  </style>
</head>
<body>
<div class="card">
  <h2>ðŸ“‚ Import Excel / CSV</h2>
  <p>Upload your emissions data file to import into the database.</p>

  <div class="columns">
    <strong>Required column order in your file:</strong><br><br>
    <code>A: category</code> &nbsp;
    <code>B: subcategory</code> &nbsp;
    <code>C: amount</code> &nbsp;
    <code>D: date (YYYY-MM-DD)</code> &nbsp;
    <code>E: notes</code>
  </div>

  <form method="POST" enctype="multipart/form-data">
    <label for="fileInput">
      <div class="drop-zone" id="dropLabel">
        ðŸ“ Click to choose your .xlsx or .csv file
        <br><small>or drag and drop here</small>
      </div>
    </label>
    <input type="file" id="fileInput" name="excel" accept=".xlsx,.xls,.csv" required
           onchange="document.getElementById('dropLabel').innerHTML = 'âœ… ' + this.files[0].name">
    <button type="submit">Import Data â†’</button>
  </form>

  <?php if ($message) : ?>
    <div class="message"><?= $message ?></div>
  <?php endif; ?>

  <a href="index.php">â† Back to Dashboard</a>
</div>
</body>
</html>