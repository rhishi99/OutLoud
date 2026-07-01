---
name: grok-voice
description: >
  Complete voice/speaker skill for Grok Build. When enabled, Grok speaks
  its outputs aloud by invoking the local speaker backend (scripts/speak.ps1,
  speaker.py + engines). Default engine is edge-tts for natural neural voices.
  Full integration with the same scripts used by Claude Code speaker plugin
  and hotkeys. Activate with /grok-voice, "enable voice mode", or any speak request.
  End goal: button + optional auto-speak directly inside the Grok tool UI.
license: MIT
---

# OutLoud / Grok Voice (for Grok Build)

This is the **complete skill** that turns on voice output mode inside Grok Build.

It lets **me (Grok)** speak key parts of my responses using the exact same local TTS backend that powers the Claude Code speaker plugin. No extra LLM tokens are ever used — the speaker only reads text I already generated.

The project is fully multi-agent: Claude Code (via Stop hook + /speak) + Grok Build (direct invocation) share `config.json`, engines, `last-response.txt`, and the speaker scripts.

## How to Enable

1. Make sure this skill file is in context:
   - Reference `skills/grok-voice/SKILL.md` (recommended), or
   - Copy/symlink it into your Grok skills folder if your setup supports global skills.

2. Activate in chat (any of these):
   - "enable grok-voice"
   - "turn on voice mode"
   - "/grok-voice"
   - "/grok-voice on"
   - Simply start using speak language: "speak the summary", "read that with voice", "use the speaker"

3. Once enabled for the session:
   - I will speak suitable outputs (final answers, summaries, results, confirmations, test phrases).
   - You can always force it with explicit requests even if not globally enabled for the chat.
   - Disable anytime: "disable voice", "normal mode", "text only, no speaking".

Voice mode is conversation-scoped and does not modify any files. It changes how I behave with audio.

## How I (Grok) Will Speak Outputs When Enabled

When grok-voice is active:

- I produce my normal text response first.
- Then (or for specific requested content) I invoke the speaker to read a cleaned, listener-friendly version aloud.
- Suitable moments: end of major sections, final results, "here is the answer", test feedback, status, or when you say "speak it".
- I keep spoken text concise and well-structured (short paragraphs, clear lists). Large code blocks become "[code block]" (or are omitted from speech).
- You hear it immediately via local audio playback. I report "🔊 Speaking..." in text so you know it's happening.
- Explicit requests always work:
  - "speak this exact sentence using the speaker"
  - "read the previous result aloud"
  - "say a test phrase"
- I can also re-speak saved last output using `-Last` when appropriate.

All of this is zero-token speech — just local playback of what was already written.

## Configuring the Engine (edge-tts default)

Configuration lives in:

- Windows: `%APPDATA%\claude-code-voice\config.json`
- macOS/Linux: `~/.config/claude-code-voice/config.json`

**Default engine: `edge-tts`** (with voice `en-US-AriaNeural`).

This is the recommended high-quality option (Microsoft neural voices, very natural). Requires one-time:

```powershell
pip install edge-tts playsound==1.2.2
```

Other engines (all supported, zero extra LLM cost):

| Engine    | Quality          | Install                          | Offline | Best for                  |
|-----------|------------------|----------------------------------|---------|---------------------------|
| edge-tts  | Excellent (default) | `pip install edge-tts playsound==1.2.2` | No      | Natural listening         |
| native    | Basic (fast)     | None (built-in)                  | Yes     | Zero deps                 |
| pyttsx3   | Good             | `pip install pyttsx3`            | Yes     | Better native control     |
| kokoro (paused/experimental)    | Very good (local neural) | `pip install kokoro (paused/experimental) sounddevice numpy` + espeak-ng | Yes | Fully offline neural |

**How to configure (tell me or run yourself):**

- "set engine to native"
- "use edge-tts with voice en-GB-SoniaNeural"
- "configure kokoro (paused/experimental) voice af_heart"
- "show speaker config"

I (or you) will execute (when cwd is the OutLoud repo):

```powershell
python scripts/speaker.py --set engine edge-tts
python scripts/speaker.py --set voice en-US-AriaNeural
python scripts/speaker.py --set rate 1.05
python scripts/speaker.py --config
```

(When using via the Claude Code plugin the commands automatically use the full plugin path with CLAUDE_PLUGIN_ROOT.)

You can also override live:

"speak this using native" or "use kokoro (paused/experimental) for the summary"

See `commands/config.md` (becomes /speaker:config) and README for more.

Run the setup helper for full guidance:

```powershell
powershell -File scripts/setup.ps1
```

## Integration with the Speaker Scripts

Grok Build has no built-in Stop hook, so integration is **direct invocation** from me using terminal execution tools.

### Primary entry points I use

1. **Smart root dispatcher** (best — auto routes based on config.json):

   From the project root:

   ```powershell
   .\speak.ps1 -Text "Text to speak here"
   .\speak.ps1 -Last
   .\speak.ps1 -Text "hello" --engine edge-tts --voice en-US-JennyNeural
   ```

   The root `speak.ps1` + `speak.cmd` inspect config and:
   - `engine == "native"` â†’ calls `scripts/speak.ps1` (pure SAPI, no Python)
   - otherwise â†’ `python scripts/speaker.py ...`

2. **Direct Python driver** (full featured, what most engines use):

   ```powershell
   python scripts/speaker.py "Clean text to speak"
   python scripts/speaker.py --last
   python scripts/speaker.py --engine edge-tts "Natural voice demo"
   ```

   `speaker.py` handles:
   - Loading `config.json` (or defaulting to edge-tts)
   - Text cleaning (markdown, code blocks â†’ "[code block]", truncation)
   - All four engines + playback logic (playsound for clean edge-tts, direct audio for kokoro (paused/experimental), etc.)
   - `--set`, `--config`, `--list-voices`, interactive mode

3. **Legacy / native-only**:

   ```powershell
   powershell -ExecutionPolicy Bypass -File "scripts\speak.ps1" -Text "..."
   ```

### Shared state with Claude Code

- `last-response.txt` (in `%APPDATA%\claude-code-voice` or `~/.config/...`) is written when I speak (and by the Claude Stop hook).
- Hotkeys (`Ctrl+Alt+S` etc.), status line (`🔊`), and `/speak` continue to work across both agents.
- Status badge script at `scripts/status.js`.

Grok always cleans for listening before passing text (or lets speaker.py do it). The call is made via the available terminal tool (e.g. `run_terminal_command`).

This design means you get instant audio feedback while editing speaker code inside Grok Build.

## Commands & Triggers You Can Use With Me

- "speak the summary"
- "read the test results aloud"
- "use the speaker for this answer"
- "enable grok-voice" / "/grok-voice"
- "speak this phrase using edge-tts"
- "re-speak the last thing"
- "configure the voice engine"
- "test speaker"

At the end of important replies I may add: "🔊 Press your hotkey or say 'speak it' to hear this."

## End Goal: Button / Auto Speak Inside the Tool

**Current state (this skill)**: Full voice capability is available inside Grok Build *today* because I (Grok) can directly call the speaker scripts on demand. This lets us develop, test, and dogfood the entire audio pipeline without leaving the agent.

**The end goal**: A native speaker button (🔊) + optional auto-speak toggle *built directly into the Grok Build tool / agent UI*, just like the hotkey + status line experience for Claude Code.

- A speaker button would instantly speak (or replay) the last agent output.
- Auto-speak mode could speak final answers / key results automatically after generation (user-controlled, respects config).
- Engine/voice settings would be configurable from inside the tool (via `/speaker:config` or `/speak`, agent settings UI), without manual JSON or CLI.
- Same backend would power both Claude Code (hook-based) and Grok Build (button/tool-based).

Everything is architected for that future: unified config, scripts, dispatchers, and capture file. This `grok-voice` skill is the development bridge that makes the button experience possible.

See the full vision in `voice-plugin-visualizer.html` and `README.md`.

## Quick Test Right Now

1. (Recommended) `pip install edge-tts playsound==1.2.2`
2. `powershell -File scripts/setup.ps1`
3. Tell me: **"enable grok-voice and speak a test of the current project"**

You should hear natural (or native) speech immediately.

## Development Workflow Tip

When working on `scripts/speaker.py`, hooks, or engines:

> "Using the speaker, confirm the change works and read the key diff line."

I will speak the result. This gives you audio regression testing live in the same session.

See root `README.md` (Grok Build section) for more examples and the full Claude Code plugin instructions.

---

This skill + the shared speaker scripts = voice for Grok Build right now, and the foundation for button/auto-speak inside the tool.


