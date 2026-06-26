#!/usr/bin/env node
/**
 * Status line provider for claude-code-voice.
 *
 * Shows a speaker icon + hint.
 *
 * Usage (add to ~/.claude/settings.json):
 *
 * {
 *   "statusLine": {
 *     "command": "node /absolute/path/to/claude-code-voice/scripts/status.js"
 *   }
 * }
 *
 * On Windows the path will be something like:
 * C:\\Users\\You\\...\\claude-code-voice\\scripts\\status.js
 *
 * The output of this script appears in Claude Code's status bar / footer.
 * Clicking isn't directly supported, so we also print a short hint.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function getLastFile() {
  const home = os.homedir();
  const dir = process.platform === 'win32'
    ? path.join(home, 'AppData', 'Roaming', 'claude-code-voice')
    : path.join(home, '.config', 'claude-code-voice');
  return path.join(dir, 'last-response.txt');
}

function getHint() {
  try {
    const f = getLastFile();
    if (fs.existsSync(f)) {
      const size = fs.statSync(f).size;
      if (size > 0) {
        const secs = Math.max(3, Math.round(size / 80)); // rough speak time
        return `🔊 last ~${secs}s  (hotkey or /speak)`;
      }
    }
  } catch {}
  return '🔊 ready  (/speak or hotkey)';
}

process.stdout.write(getHint());
process.exit(0);
