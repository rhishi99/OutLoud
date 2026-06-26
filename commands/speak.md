---
description: OutLoud speaker control. /speak [text|last|on|off|stop]
argument-hint: "[text to speak | last | on | off | stop]"
---

You are controlling the OutLoud (speaker) plugin.

Supported forms (parse args after /speak):

- /speak                  -> speak last saved response (via backend)
- /speak last             -> same (explicit)
- /speak "some words"     -> speak the provided text immediately
- /speak on               -> enable autoSpeak (auto-narration after Stop). Run: python scripts/speaker.py --autospeak on   OR --set autoSpeak true. Confirm.
- /speak off              -> disable autoSpeak. Run python scripts/speaker.py --autospeak off. Confirm state.
- /speak stop             -> best-effort stop current playback. Run: python scripts/speaker.py --stop

Implementation:
1. For "on"/"off": use terminal to execute `python scripts/speaker.py --autospeak on` (or off). Then tell user the result and current status.
2. For "stop": run `python scripts/speaker.py --stop`. Report "attempted stop".
3. For last / text: remind user (or execute if allowed) to use hotkey or the speak script: `python scripts/speaker.py --last` or pass text.
   Respond briefly: "🔊 Playing last response via OutLoud..."

Always respect:
- OUTLOUD_MUTE=1 disables all speech.
- Config (autoSpeak etc) is live via the python speaker.py --config tool.

If no previous capture: "No output captured yet. Ask something then use hotkey or /speak."

Never dump the full assistant text into chat unless user asks to copy it. Keep responses short + actionable. Use the real CLI for toggles so config persists.
