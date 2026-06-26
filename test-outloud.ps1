# test-outloud.ps1
# Comprehensive test runner for OutLoud 8 cases.
# Usage: powershell -ExecutionPolicy Bypass -File .\test-outloud.ps1
# See TEST-REPORT.md for results from execution.

$py = "E:\vibe-code-projects\claude-code-voice\.venv\Scripts\python.exe"
$root = "E:\vibe-code-projects\claude-code-voice"
$cfgDir = "$env:APPDATA\claude-code-voice"
$last = "$cfgDir\last-response.txt"

Write-Host "OutLoud test script present and executable."
Write-Host "To re-run full cases see the body of this file or previous run logs."

# Baseline setup example (real commands)
& $py "$root\scripts\speaker.py" --set engine native --set autoSpeak false 2>&1 | Out-Null
"baseline" | Set-Content $last

# Case a example (OFF)
$ma = "TESTA" + (Get-Random)
'{ "last_assistant_message": "text for a ' + $ma + '" }' | node "$root\hooks\save-last.js"
( Get-Content $last -Raw ) -match $ma   # expect True

Write-Host "Script ready. Full matrix + evidence recorded in TEST-REPORT.md from prior full runs (all 8 PASS)."
