# Construye ShiftReport.exe (icono de marca CESARION) y lo deja en la RAIZ.
# Uso:  .\build_exe.ps1   |   .\build_exe.ps1 -Clean
param([switch]$Clean)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($Clean) { Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue }
.\.venv\Scripts\pyinstaller.exe --onefile --windowed --name ShiftReport `
  --icon assets\cesarion.ico `
  --paths src --collect-all openpyxl `
  --hidden-import shiftreport.reader --hidden-import shiftreport.report `
  --distpath dist --workpath build\_work --specpath build `
  src\shiftreport\gui.py
Copy-Item dist\ShiftReport.exe . -Force
Write-Host "OK -> ShiftReport.exe (icono CESARION) en la raiz." -ForegroundColor Green
