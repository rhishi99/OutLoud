<#
OutLoud root convenience wrapper (smart engine dispatcher) [formerly claude-code-voice]

It checks your config.json and routes to the right backend:
- native → fast built-in (scripts/speak.ps1)  [lightweight fallback]
- everything else (default: edge-tts) → python scripts/speaker.py (with playsound for clean playback)

Best usage (recommended):
  .\speak.ps1 -Text "your text here"
  .\speak.ps1 --last
  .\speak.ps1 -Text "hello" --engine edge-tts

You can also just pass text positionally for simple cases.
#>

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$configPath = if ($env:APPDATA) { Join-Path $env:APPDATA 'claude-code-voice\config.json' } else { Join-Path $HOME '.config/claude-code-voice/config.json' }

$engine = "edge-tts"
if (Test-Path $configPath) {
    try {
        $cfg = Get-Content $configPath -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($cfg -and $cfg.engine) { $engine = $cfg.engine }
    } catch { }
}

$python = Join-Path $here 'scripts\speaker.py'
$native = Join-Path $here 'scripts\speak.ps1'

# If engine != native (default is now edge-tts), use Python backend
$wantPython = ($engine -ne 'native') -or ($args -match '--engine')

if ($wantPython -and (Test-Path $python)) {
    & python $python @args
    exit $LASTEXITCODE
}

& $native @args
