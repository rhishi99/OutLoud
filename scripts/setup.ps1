<#
OutLoud Setup (edge-tts + playsound default)  [formerly claude-code-voice]

Prints config, statusLine, hotkey examples, and helps install natural voices.
#>

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$statusScript = (Join-Path $repoRoot 'scripts/status.js')
$pythonSpeaker = (Join-Path $repoRoot 'scripts/speaker.py')
$exampleConfig = (Join-Path $repoRoot 'config.example.json')

$voiceDir = if ($env:APPDATA) {
    Join-Path $env:APPDATA 'claude-code-voice'
} else {
    Join-Path $HOME '.config/claude-code-voice'
}

if (-not (Test-Path $voiceDir)) {
    New-Item -ItemType Directory -Path $voiceDir -Force | Out-Null
    Write-Host "Created $voiceDir" -ForegroundColor Green
}

# Copy example config if none exists
$configPath = Join-Path $voiceDir 'config.json'
if (-not (Test-Path $configPath) -and (Test-Path $exampleConfig)) {
    Copy-Item $exampleConfig $configPath
    Write-Host "Created default config.json from example" -ForegroundColor Green
}

Write-Host ''
Write-Host '=== OutLoud setup (configurable TTS) ===' -ForegroundColor Cyan
Write-Host ''

Write-Host '1. Status line (🔊 icon in Claude Code):' -ForegroundColor Yellow
Write-Host ''
Write-Host ('{')
Write-Host ('  "statusLine": {')
Write-Host ('    "command": "node \"' + $statusScript + '\""')
Write-Host ('  }')
Write-Host ('}')
Write-Host ''

Write-Host '2. Recommended hotkey (PowerToys Keyboard Manager or AutoHotkey):' -ForegroundColor Yellow
$psNative = 'powershell -ExecutionPolicy Bypass -File "' + (Join-Path $repoRoot 'scripts/speak.ps1') + '" -Last'
Write-Host ('   Ctrl+Alt+S  ->  ' + $psNative)
Write-Host '   (or point it at speaker.py for your chosen engine)'
Write-Host ''

Write-Host '3. Quick tests:' -ForegroundColor Yellow
Write-Host ('   python "' + $pythonSpeaker + '" "Hello from the configurable speaker"')
Write-Host ('   python "' + $pythonSpeaker + '" --last')
Write-Host ('   python "' + $pythonSpeaker + '" --engine edge-tts "This is a very natural voice"')
Write-Host ''

Write-Host '4. Change engine (examples):' -ForegroundColor Yellow
Write-Host ('   python "' + $pythonSpeaker + '" --set engine edge-tts')
Write-Host ('   python "' + $pythonSpeaker + '" --set voice en-US-AriaNeural')
Write-Host ('   python "' + $pythonSpeaker + '" --config     # view current settings')
Write-Host ''

Write-Host '5. Install natural voices (recommended for best experience):' -ForegroundColor Yellow
Write-Host '   pip install edge-tts playsound      # edge-tts + playsound = clean neural playback (no media popup)'
Write-Host '   pip install pyttsx3                 # lightweight improved native fallback'
Write-Host '   # kokoro support is paused (experimental; contributions welcome for fully offline neural)'
Write-Host ''

Write-Host '6. Claude Code plugin install:' -ForegroundColor Yellow
Write-Host '   /plugin marketplace add rhishi99/OutLoud'
Write-Host '   /plugin install speaker@speaker'
Write-Host ''

Write-Host 'The Stop hook ONLY saves text. Speaking is on-demand (hotkey/CLI). No extra LLM tokens ever.' -ForegroundColor Green
Write-Host 'Restart Claude Code after adding statusLine.'

