@echo off
setlocal enabledelayedexpansion

set "repo=%~dp0"
set "config=%APPDATA%\claude-code-voice\config.json"
set "engine=native"

if exist "%config%" (
  for /f "tokens=2 delims=:," %%a in ('findstr /i "engine" "%config%"') do (
    set "engine=%%~a"
    set "engine=!engine:"=!"
    set "engine=!engine: =!"
  )
)

if /i not "%engine%"=="native" (
  if exist "%repo%scripts\speaker.py" (
    python "%repo%scripts\speaker.py" %*
    exit /b
  )
)
rem Default engine (edge-tts) uses python path for clean playsound playback

powershell -ExecutionPolicy Bypass -File "%repo%speak.ps1" %*
endlocal
