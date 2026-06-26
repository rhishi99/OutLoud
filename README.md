# claude-code-voice 🔊

**On-demand speaker for Claude Code + Grok Build testing.**

Hear the AI's last response spoken aloud — zero extra LLM tokens or calls. Use a hotkey, `/speak`, CLI, or ask the agent directly.

**Recommended default:** `edge-tts` with `playsound` for clean, high-quality Microsoft neural playback (no media player popup).  
**Lightweight fallbacks:** `native` (built-in, zero deps) and `pyttsx3`.

`kokoro` support exists in code but is paused for now (experimental; left for open-source contributors).

Ready for everyday local use and as a full Claude Code plugin.

## Quick Start (Local / Immediate Use)

```powershell
# 1. Recommended (clean neural)
pip install edge-tts playsound

# 2. Test
python scripts/speaker.py "This is claude-code-voice. Edge TTS + playsound gives clean playback."
.\speak.ps1 -Text "Native fallback works with no extra packages."

# 3. Configure (one time)
python scripts/speaker.py --set engine edge-tts --set voice en-US-AriaNeural
python scripts/speaker.py --config
```

Config file: `%APPDATA%\claude-code-voice\config.json` (or `~/.config/claude-code-voice/config.json`).

Run `.\scripts\setup.ps1` for printed statusLine, hotkey examples, and more.

## Features

- 🔊 Persistent status line badge (`🔊 last ~12s (hotkey or /speak)`)
- Stop hook auto-captures every final AI response (Claude Code)
- On-demand playback from hotkey / CLI / `/speak` / agent request
- Clean speech text (code blocks → "[code block]", links/images stripped)
- edge-tts default: natural voices + playsound for popup-free playback
- native + pyttsx3: instant, fully offline, private, lightweight
- Same engine backend for Claude Code and Grok Build
- Zero token cost — only reads output that was already generated
- Hotkey / button friendly on Windows (and cross-platform scripts)
- Plugin-ready: commands, skills, hooks, marketplace manifest

## Installation

### Claude Code Plugin (full integration)

```bash
/plugin marketplace add <your-username>/claude-code-voice
/plugin install speaker@speaker
```

Restart Claude Code sessions.

Add the status indicator (global `~/.claude/settings.json` or per-project):

```json
{
  "statusLine": {
    "command": "node \"<full-path-to-claude-code-voice>\\scripts\\status.js\""
  }
}
```

### Local Use & Grok Build (no plugin required)

Clone or use this folder directly. All scripts work standalone. The plugin files (`hooks/`, `commands/`, `skills/`, `.claude-plugin/`) are present for when you install into Claude Code.

## Speaking AI Output On Demand (Inside the Tools)

**Claude Code:**
- Finish a response → it's automatically captured.
- Press global hotkey → speaks last output.
- Type `/speak` (or `/speak arbitrary text`).
- Say things like "read that back", "speak the answer", "use the speaker" — the agent instructs you to use the hotkey/CLI.

**Inside Grok Build (dev & testing):**
- Ask directly: "Speak the project status with the speaker", "Read the last result using edge-tts", "Use voice for this summary".
- Grok uses the real local speaker (via `skills/grok-voice`).
- Shared capture file with the Claude hook.

Direct control (any terminal):
```powershell
python scripts/speaker.py --last
.\speak.ps1 -Last
python scripts/speaker.py --engine native "Quick native test"
```

## Configuration

```json
{
  "engine": "edge-tts",
  "voice": "en-US-AriaNeural",
  "rate": 1.0,
  "volume": 1.0
}
```

Change at any time:

```powershell
python scripts/speaker.py --set engine edge-tts --set voice en-US-AriaNeural
python scripts/speaker.py --set engine native
python scripts/speaker.py --list-voices --engine edge-tts
```

**Engines (current priorities):**

| Engine     | Install                          | Quality          | Notes |
|------------|----------------------------------|------------------|-------|
| `edge-tts` | `pip install edge-tts playsound` | Excellent neural | **Recommended**. Clean playback via playsound (no popup). Streams. |
| `native`   | Built-in                         | Basic (OS)       | Zero deps. Fastest & fully private. Default lightweight fallback. |
| `pyttsx3`  | `pip install pyttsx3`            | Better native    | Good control over system voices. Lightweight. |
| `kokoro`   | (heavy)                          | Local neural     | Paused (experimental). Code remains for contributors. |

The root `speak.ps1` / `speak.cmd` dispatch automatically based on config (native uses PowerShell SAPI directly; others use Python).

## Hotkey / "Speaker Button"

**Best on Windows:** PowerToys Keyboard Manager or AutoHotkey.

Example mapping:
```
Ctrl + Alt + S  →  powershell -ExecutionPolicy Bypass -File "...\claude-code-voice\scripts\speak.ps1" -Last
```

(Use the root `speak.ps1` wrapper for automatic engine selection.)

macOS/Linux: bind equivalent to call `python .../speaker.py --last` or equivalent OS TTS.

You can also run from any terminal or launcher.

## Grok Support

Full first-class support inside Grok Build for development:

- Direct real-speaker invocation (not simulated).
- `skills/grok-voice/SKILL.md` activates voice-aware behavior.
- Ask Grok to speak summaries, diffs, instructions, or test phrases while iterating.
- Identical backend + capture file used by the Claude Code plugin.
- Ideal for hearing results live before publishing the plugin.

## End Goal & Current Integration Status

**End goal:** First-class, on-demand voice output for AI coding agents (primarily Claude Code). Hear responses instead of reading long output. Local or free high-quality TTS, hotkey or in-tool triggered, zero extra token cost, clean UX (no popups).

**Current status — ready for use:**
- **Local use:** Fully working today. Scripts + hotkeys + Python engine dispatch. Run from anywhere.
- **Claude Code plugin:** Complete and installable. Includes Stop hook (`save-last.js`), `/speak` + config commands, statusLine provider, skills, and marketplace manifest.
- **Grok Build:** Deeply integrated for testing and daily use during development. Grok can trigger actual audio.
- **Playback UX:** edge-tts + playsound = clean experience. Native/pyttsx3 always available as instant fallbacks.
- **kokoro:** Deprioritized/paused (experimental quality varies; contributions welcome).
- Everything stays local and private. No keys, no cloud for the core path.

The project is in a stable, usable state for both local workflows and Claude Code plugin adoption.

## Other Notes

- Text is cleaned for listening before speaking.
- Long outputs are truncated for speech (re-trigger for more).
- Platform: Best on Windows. Scripts support macOS/Linux fallbacks.
- See `scripts/speaker.py` for engine details and `hooks/hooks.json` for the plugin hook contract.

## Credits

Built following successful patterns from ponytail and ECC plugins. Inspired by community efforts around local voice for coding agents.

MIT license.

---

**Get started:** Install the pip packages, bind a hotkey to speak the last response, add the status line, ask Claude/Grok something, then hit the speaker. You'll hear it immediately.
