$files = @(
  'c:\xampp\htdocs\carbon_db\api\ai_agent.php',
  'c:\xampp\htdocs\carbon_db\api\emissions.php',
  'c:\xampp\htdocs\carbon_db\upload.php'
)
foreach ($f in $files) {
  if (-not (Test-Path $f)) { Write-Output "Missing: $f"; continue }
  $b = [System.IO.File]::ReadAllBytes($f)
  if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) {
    [System.IO.File]::WriteAllBytes($f, $b[3..($b.Length-1)])
    Write-Output "Removed BOM: $f"
  } else {
    Write-Output "No BOM: $f"
  }
}
