<#
.SYNOPSIS
  Adds global Windows hotkeys for OutLoud. No AutoHotkey or PowerToys needed.

.DESCRIPTION
  Creates two Start Menu shortcuts with built-in Windows shortcut keys:
    Ctrl+Alt+S  speak the last Claude Code response
    Ctrl+Alt+X  stop playback
  Uses pythonw.exe when available so no console window flashes.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\install-hotkey.ps1
  powershell -ExecutionPolicy Bypass -File scripts\install-hotkey.ps1 -Remove
#>
param(
  [string]$SpeakKey = 'CTRL+ALT+S',
  [string]$StopKey = 'CTRL+ALT+X',
  [switch]$Remove
)

$ErrorActionPreference = 'Stop'
$menu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\OutLoud'
$speaker = Join-Path $PSScriptRoot 'speaker.py'

if ($Remove) {
  if (Test-Path $menu) { Remove-Item -Recurse -Force $menu }
  Write-Host 'OutLoud hotkeys removed.'
  return
}

$py = Get-Command pythonw -ErrorAction SilentlyContinue
$style = 7  # minimized, used only for the python.exe fallback
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { throw 'Python not found on PATH. Install Python 3, then rerun.' }

New-Item -ItemType Directory -Force $menu | Out-Null
$shell = New-Object -ComObject WScript.Shell

function New-HotkeyShortcut($name, $arguments, $key) {
  $lnk = $shell.CreateShortcut((Join-Path $menu "$name.lnk"))
  $lnk.TargetPath = $py.Source
  $lnk.Arguments = "`"$speaker`" $arguments"
  $lnk.WorkingDirectory = Split-Path $PSScriptRoot
  $lnk.Hotkey = $key
  $lnk.WindowStyle = $style
  $lnk.Description = "OutLoud: $name"
  $lnk.Save()
  Write-Host ("  {0,-12} -> {1}" -f $key, $name)
}

Write-Host 'OutLoud hotkeys installed:'
New-HotkeyShortcut 'Speak last response' '--last' $SpeakKey
New-HotkeyShortcut 'Stop speaking' '--stop' $StopKey
Write-Host "Shortcuts live in: $menu"
Write-Host 'If a key does nothing, sign out and back in once so Explorer registers it.'
