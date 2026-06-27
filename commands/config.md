---
description: Configure OutLoud (engine, voice, etc). Use /speaker:config or via /speak
argument-hint: "[show | engine edge-tts | voice en-US-AriaNeural | help]"
---

Configure the speaker.

**Always use the plugin path (Claude Code fills it in):**
- WSL/Linux/mac: `bash "${CLAUDE_PLUGIN_ROOT}/speak.sh" --config`
- Or: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" --config`
- Windows: `python "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" --config`

First action on any config request:
Run the --config command above (using the full path) and show the result to the user.

If it fails with missing python / package:
- Let the error print.
- Tell the user to run `/speaker:setup` (dedicated command that prints the exact fix commands or confirms completion).
- "After running those, try /speaker:setup or this command again."

Changing settings:
- engine edge-tts (recommended)
- voice "en-US-AriaNeural"
- rate 1.05
- Use: `... --set engine edge-tts` (full path)

Strong default: edge-tts + AriaNeural.

Native is only for no-internet cases.

After changes, re-run --config and offer a test speak.

Keep answers tiny. The plugin drives the setup now.
