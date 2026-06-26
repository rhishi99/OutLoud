---
description: Configure the speaker plugin (engine, voice, rate, etc.)
argument-hint: "[show | engine edge-tts | voice af_heart | rate 1.1 | help]"
---

You are helping the user configure the local speaker plugin for better voice output.

Current tools:
- The speaker reads from the same last-response.txt used by the Stop hook.
- Config lives at the user's claude-code-voice/config.json (or %APPDATA%). (Product rebranded to OutLoud; internal folder kept for compatibility.)

When user asks to configure:
1. Read current state if needed by telling them to run `python scripts/speaker.py --config`
2. Use simple instructions:
   - "set engine to edge-tts" → tell user to run `python scripts/speaker.py --set engine edge-tts`
   - Provide good voice recommendations based on engine.
3. Always remind: "This is only changing how the output is read aloud. No extra tokens."

Good defaults to suggest:
- Recommended: engine=edge-tts, voice=en-US-AriaNeural (install: pip install edge-tts playsound)
- Lightweight: engine=native or pyttsx3 (no internet, built-in OS voices)

Offer to speak a test phrase after config changes.

Keep responses short and actionable.
