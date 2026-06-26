---
description: Speak the most recent Claude response aloud using the speaker plugin.
argument-hint: "[optional text to speak instead]"
---

You are controlling the speaker plugin.

1. If the user gave extra text after /speak, speak exactly that.
2. Otherwise, tell the user to trigger the speaker:
   - Run the provided speaker script/hotkey (recommended), or
   - Say "speak it" again and we will use the last captured output.

The last response is already captured automatically by the plugin's Stop hook into a file that the speak CLI reads.

Respond briefly like: "🔊 Playing last response via speaker..."

If there was no previous output captured yet, say "No output captured yet. Ask me something and then use the speaker hotkey or /speak."

Never output the full text yourself unless the user explicitly asks you to paste it for copying.
