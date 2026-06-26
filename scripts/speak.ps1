<#
.SYNOPSIS
  OutLoud Speaker (formerly claude-code-voice) - speaks the last captured response.

.DESCRIPTION
  Reads last-response.txt (from APPDATA\claude-code-voice or ~/.config) and speaks it
  using Windows built-in SAPI (System.Speech). No extra installs.

  Run this from a hotkey, button binding, or manually.

  For best "button" experience on Windows:
    - Use PowerToys Keyboard Manager or AutoHotkey to bind e.g. Ctrl+Alt+S
#>

param(
  [Parameter(Position=0)]
  [string]$Text,
  [switch]$NoClean,
  [switch]$Last,          # Force read from saved last-response (useful for testing)
  [int]$Rate = 0,
  [int]$Volume = 100
)

$ErrorActionPreference = 'SilentlyContinue'

# Support basic piping of text
if (-not $Text -and $input) {
  $Text = ($input | Out-String).Trim()
}

$voiceDir = if ($env:APPDATA) {
  Join-Path $env:APPDATA 'claude-code-voice'
} else {
  Join-Path $HOME '.config/claude-code-voice'
}

$lastFile = Join-Path $voiceDir 'last-response.txt'

function Get-SavedText {
  if (Test-Path $lastFile) {
    $raw = Get-Content $lastFile -Raw -Encoding UTF8
    if (-not $NoClean) {
      $raw = $raw -replace '```[\s\S]*?```', '[code block]'
    }
    return $raw.Trim()
  }
  return $null
}

$toSpeak = $null
if ($Last -or -not $Text) {
  $toSpeak = Get-SavedText
}
if (-not $toSpeak -and $Text) {
  $toSpeak = $Text
}

if (-not $toSpeak -or $toSpeak.Length -lt 3) {
  Write-Host 'No text provided and no saved last-response found.' -ForegroundColor Yellow
  Write-Host 'Usage examples:' -ForegroundColor DarkGray
  Write-Host '  .\speak.ps1 "Hello world"' -ForegroundColor DarkGray
  Write-Host '  .\speak.ps1 -Last' -ForegroundColor DarkGray
  Write-Host '  echo "some text" | .\speak.ps1   # (pipe support limited, use -Text)' -ForegroundColor DarkGray
  exit 1
}

Add-Type -AssemblyName System.Speech -ErrorAction Stop

$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synthesizer.Rate = [Math]::Max(-10, [Math]::Min(10, $Rate))
$synthesizer.Volume = [Math]::Max(0, [Math]::Min(100, $Volume))

try {
  Write-Host 'Speaker: speaking last response...' -ForegroundColor Cyan
  $synthesizer.Speak($toSpeak)
  Write-Host 'Done.' -ForegroundColor Green
} finally {
  $synthesizer.Dispose()
}
