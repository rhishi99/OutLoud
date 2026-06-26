# claude-code-voice 🔊

**On-demand speaker for Claude Code (lightweight, local TTS).**

Hear the AI's last response spoken aloud — zero extra LLM tokens. Use hotkey, /speak, or CLI.

**Recommended:** edge-tts + playsound for clean neural playback (no media player popup).

Lightweight fallback: native (built-in).

## Quick Start (WSL / Linux - End User after ship)

1. Clone
   git clone https://github.com/<your-username>/claude-code-voice.git
   cd claude-code-voice

2. Setup (one time)
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python scripts/speaker.py --set engine edge-tts --set voice "en-US-AriaNeural"

3. (Optional) Make easy wrapper
   # Create speak.sh as above if not present
   chmod +x speak.sh

## Claude Code Plugin Install (in WSL Claude Code)

After clone and setup above:

 /plugin marketplace add <your-username>/claude-code-voice
 /plugin install speaker@speaker

Restart or reload Claude Code.

Add status line to ~/.claude/settings.json (adjust path to your clone or installed plugin dir):

`json
{
  "statusLine": {
    "command": "node \"/path/to/claude-code-voice/scripts/status.js\""
  }
}
`

## Usage

- Ask Claude something.
- Press your hotkey or type /speak to hear the last output.
- Or run in terminal: ./.venv/bin/python scripts/speaker.py --last

## Hotkey (from Windows host for WSL)

Use PowerToys or similar to run:
wsl -d <YourDistro> -e bash -c "cd /mnt/e/vibe-code-projects/claude-code-voice; ./.venv/bin/python scripts/speaker.py --last"

## Config

See config.example.json

## Requirements (minimal)

edge-tts
playsound==1.2.2

## Notes for WSL

- Audio in WSL may require pulseaudio or similar setup.
- For best, use the venv python.
- All local, no extra tokens.
- Plugin uses the scripts from the installed location.

For full details see the original README, but this is the minimal to make it working.
