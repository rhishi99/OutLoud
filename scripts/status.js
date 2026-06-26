#!/usr/bin/env node
/**
 * Status line provider for OutLoud (formerly claude-code-voice).
 *
 * Shows " OutLoud" + state:  muted | auto | /speak (on-demand)
 * Reflects live autoSpeak config + OUTLOUD_MUTE.
 *
 * IMPORTANT: This is text-only. Status line badges are NOT clickable.
 * Use hotkey (/speak / Ctrl+Alt+S) or type /speak in the prompt.
 *
 * Usage (add to ~/.claude/settings.json):
 *
 * {
 *   "statusLine": {
 *     "command": "node \"/absolute/path/to/claude-code-voice/scripts/status.js\""
 *   }
 * }
 *
 * The output of this script appears in Claude Code's status bar / footer.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function getVoiceDir() {
  const home = os.homedir();
  return process.platform === 'win32'
    ? path.join(home, 'AppData', 'Roaming', 'claude-code-voice')
    : path.join(home, '.config', 'claude-code-voice');
}

function getLastFile() {
  return path.join(getVoiceDir(), 'last-response.txt');
}

function getConfig() {
  const p = path.join(getVoiceDir(), 'config.json');
  try {
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch {}
  return {};
}

function getState() {
  const mute = (process.env.OUTLOUD_MUTE || '').toString().trim();
  if (mute === '1' || mute.toLowerCase() === 'true') return 'muted';
  const cfg = getConfig();
  if (cfg.autoSpeak) return 'auto';
  return 'ondemand';
}

function getHint() {
  const state = getState();
  let label = 'OutLoud';
  if (state === 'muted') {
    label = ' OutLoud [muted]';
  } else if (state === 'auto') {
    label = ' auto';
  } else {
    label = ' /speak';
  }

  try {
    const f = getLastFile();
    if (fs.existsSync(f)) {
      const size = fs.statSync(f).size;
      if (size > 0) {
        return `${label}`;
      }
    }
  } catch {}
  return label;
}

process.stdout.write(getHint());
process.exit(0);
