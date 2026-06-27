---
description: OutLoud speaker control. Primary command: /speak (or /speaker:speak)
argument-hint: "[last | on | off | stop | your text]"
---

You control the OutLoud speaker.

**Invocation rule (critical for WSL/Linux/mac + any project):**
Always run using the installed plugin path (Claude Code substitutes it):
- Preferred on WSL/Linux/mac: `bash "${CLAUDE_PLUGIN_ROOT}/speak.sh" --last` or `--autospeak on`
- Fallback: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" --last`
- Windows: `python "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" ...`

Supported:
- /speak          → speak last response
- /speak last
- /speak "text"   → speak this
- /speak on       → auto-narration after replies
- /speak off
- /speak stop

Behavior:
- If the Bash command fails with "python" / module not found / command not found:
  1. Run the speaker command anyway so the user sees the exact error.
  2. Tell the user to run `/speaker:setup` (it will print the exact commands needed).
  3. "Run the commands it gives, then try /speak again."
- For on/off: run the full-path --autospeak command, confirm, then show current state with --config if possible.
- For last/text: run or tell the user the exact command. Keep reply short: "🔊 Speaking last response..."

Rules:
- Respect OUTLOUD_MUTE=1
- Never paste the full previous response text unless asked.
- If nothing captured yet: "Ask me something first, then use /speak last."
- Prefer the speak.sh wrapper on non-Windows for easier python3 handling.

Keep every reply very short. The plugin itself now drives most of the setup instructions.
