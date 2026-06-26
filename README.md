<div align="center">

# 🔊 claude-code-voice

### Give Claude Code (and Grok Build) a voice — hear your AI's output instead of reading it.

A lightweight, on-demand text-to-speech speaker plugin. High-quality neural voice via **edge-tts + playsound** (no media-player popup), with native/`pyttsx3` fallbacks. **Zero extra LLM tokens** — it only speaks text that was already generated.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-7c3aed)](https://docs.claude.com/en/docs/claude-code)
[![Built with Grok Build](https://img.shields.io/badge/Built%20with-Grok%20Build-1d4ed8)](https://grok.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20WSL-blue)](#-requirements)

</div>

---

## 🚀 Built with Grok Build

This project was **designed and built end-to-end with [Grok Build](https://grok.com)** — full credit to Grok for the architecture, the iterative build loop, the multi-agent docs sweep, and the live tooling. The entire build journey (every milestone, every fix) is captured in an interactive timeline:

- 📈 **[`build-journey.html`](build-journey.html)** — the Grok Build story, milestone by milestone
- 🎛️ **[`voice-plugin-visualizer.html`](voice-plugin-visualizer.html)** — live architecture + interactive config console

> Open either file in a browser to see how it came together.

---

## ✨ Features

- 🎙️ **Natural neural voice** — `edge-tts` (Microsoft `en-US-AriaNeural` by default) for genuinely human-sounding output.
- 🔇 **No popup** — `playsound` plays the MP3 directly. No media player hijacking your screen.
- 💸 **Zero extra tokens** — the speaker reads text Claude/Grok *already* produced. It never calls an LLM.
- ⌨️ **Multiple triggers** — hotkey, `/speak` slash command, CLI, or status-line badge.
- 🪝 **Automatic capture** — a Stop hook quietly saves the last response so it's ready to speak on demand.
- 🧩 **Real plugin** — proper `.claude-plugin/` structure, hooks, commands, and skills.
- 🤖 **Multi-agent** — one shared backend powers both **Claude Code** (hook-based) and **Grok Build** (direct invoke).
- 🔁 **Pluggable engines** — `edge-tts`, `native` (OS built-in, offline, zero deps), `pyttsx3`. `kokoro` (offline neural) is paused/experimental.
- ♿ **Accessibility-first** — listen while you work; great for eyes-off and screen-reader-adjacent workflows.

---

## 📦 Quick Start

### Option A — Install as a Claude Code plugin

```bash
/plugin marketplace add rhishi99/claude-code-voice
/plugin install speaker@speaker
```

### Option B — Clone & set up locally (incl. WSL)

```bash
git clone https://github.com/rhishi99/claude-code-voice.git
cd claude-code-voice

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/speaker.py --set engine edge-tts --set voice "en-US-AriaNeural"
```

### Add the status-line badge (recommended)

Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "command": "node \"/path/to/claude-code-voice/scripts/status.js\""
  }
}
```

Restart Claude Code after adding it.

---

## 🎧 Usage

1. Ask Claude (or Grok) something.
2. Hear the last response any of these ways:
   - Press your hotkey (e.g. `Ctrl+Alt+S`)
   - Type `/speak`
   - Run it directly:
     ```bash
     python scripts/speaker.py --last
     ```
3. Speak arbitrary text:
   ```bash
   python scripts/speaker.py "This is a very natural voice"
   /speak Some custom text here
   ```

> Large code blocks are spoken as `[code block]` so you're not read a wall of syntax.

---

## 🗣️ Engines

| Engine | Quality | Install | Offline | Best for |
|--------|---------|---------|---------|----------|
| **edge-tts** *(default)* | Excellent | `pip install edge-tts playsound==1.2.2` | No | Natural listening |
| native | Basic (fast) | None (built-in) | Yes | Zero dependencies |
| pyttsx3 | Good | `pip install pyttsx3` | Yes | Better native control |
| kokoro *(paused/experimental)* | Very good (local neural) | contributions welcome | Yes | Fully offline neural |

Change engine/voice anytime:

```bash
python scripts/speaker.py --set engine edge-tts
python scripts/speaker.py --set voice en-GB-SoniaNeural
python scripts/speaker.py --config        # view current settings
```

---

## 🔧 Requirements

Minimal:

```
edge-tts
playsound==1.2.2
```

- All playback is **local** after install. `edge-tts` needs internet to synthesize.
- The `native` engine works fully offline with **zero extra packages**.
- Config lives at `%APPDATA%\claude-code-voice\config.json` (Windows) or `~/.config/claude-code-voice/config.json`. See [`config.example.json`](config.example.json).

---

## 🧠 How it works

- **Claude Code:** a Stop hook (`hooks/save-last.js`) writes cleaned text to `last-response.txt` after every final response. `/speak` or your hotkey plays it.
- **Grok Build:** no Stop hook, so Grok invokes the speaker scripts directly (see [`skills/grok-voice/SKILL.md`](skills/grok-voice/SKILL.md)).
- Both share the same `config.json`, engines, and capture file — one backend, two agents.
- **Nothing auto-speaks.** Audio only plays when you (or a hotkey/`/speak`) ask for it.

See the [interactive visualizer](voice-plugin-visualizer.html) for the full flow diagram.

---

## 🤝 Contributing

PRs and issues welcome — especially:

- Reviving **kokoro** for fully-offline neural voice.
- A native speaker **button** inside the Grok Build / Claude Code UI.
- More voices, engines, and platform testing (macOS / Linux / WSL).

Fork, branch, and open a PR. Keep it lightweight.

---

## 📜 License

[MIT](LICENSE) © claude-code-voice contributors. **Built with Grok Build.**

<div align="center">

`claude-code` · `tts` · `edge-tts` · `voice` · `accessibility` · `grok` · `developer-tools` · `cli` · `neural-voice`

</div>
