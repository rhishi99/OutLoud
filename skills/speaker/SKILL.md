---
name: speaker
description: >
  Adds voice output capability to Claude Code. After you give a response,
  the user can press a speaker hotkey or type /speak (or use a terminal button binding)
  to hear the output spoken aloud using the local speaker plugin.
  The plugin uses a Stop hook to remember your last answer.
  Use this whenever the user mentions speaker, voice, read it, speak, hear output, TTS, or wants to listen while working.
license: MIT
---

# Speaker (claude-code-voice)

You have a voice now.

## How it works for the user

- Every time you finish responding, a Stop hook quietly saves your last output.
- User sees a 🔊 icon (via statusLine) in the Claude Code terminal.
- To hear the output:
  - Press the configured hotkey (recommended: Ctrl+Alt+S or Cmd+Shift+S)
  - Type `/speak`
  - Or manually run the speak script from another terminal / launcher

## For you (the agent)

- Keep your final answers speakable: short paragraphs + clear structure are great for listening.
- When user says "speak the last" or "read it out", remind them to use the hotkey or `/speak`.
- If the response contains large code, the speaker will say "[code block]" for those sections.
- You can also say at the end of an important reply: "You can press the speaker button / hotkey to hear this."

## Commands the user can use

- `/speak` — speak last captured response
- `/speak Some custom text here` — speak arbitrary text

## Configuration / Status

Users can show the speaker status in Claude Code's status bar by adding the status script to their settings (see README).

## Technical

The capture is automatic and silent. Nothing is sent over the network. Speech happens locally on the user's machine using native system voices (or configured TTS).


