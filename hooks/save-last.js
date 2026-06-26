#!/usr/bin/env node
/**
 * Stop hook for OutLoud (claude-code-voice) speaker plugin.
 * Captures the last assistant response text and writes it to a well-known location
 * so that the speaker CLI / hotkey / /speak can play it on demand.
 *
 * Supports autoSpeak (opt-in auto-narration) AFTER save:
 * - NON-BLOCKING: spawns detached speaker process (playback never holds hook)
 * - Respects OUTLOUD_MUTE=1 (CI/pair safety)
 * - Applies autoSpeak* config: skip code, max chars, mode (full/summary/first-paragraph)
 * - Reuses exact same speaker backend (speaker.py or speak.ps1)
 *
 * Supports both:
 * - Direct "last_assistant_message" style (some versions)
 * - transcript_path jsonl (standard)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

function getVoiceDir() {
  const home = os.homedir();
  const dir = process.platform === 'win32'
    ? path.join(home, 'AppData', 'Roaming', 'claude-code-voice')
    : path.join(home, '.config', 'claude-code-voice');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function getLastFile() {
  return path.join(getVoiceDir(), 'last-response.txt');
}

function getConfigPath() {
  return path.join(getVoiceDir(), 'config.json');
}

function loadConfig() {
  const defaults = {
    engine: "edge-tts",
    voice: "en-US-AriaNeural",
    rate: 1.0,
    volume: 1.0,
    strip_code: true,
    max_chars: 6500,
    autoSpeak: false,
    autoSpeakMaxChars: 1200,
    autoSpeakSkipCodeBlocks: true,
    autoSpeakMode: "full"
  };
  try {
    const p = getConfigPath();
    if (fs.existsSync(p)) {
      const user = JSON.parse(fs.readFileSync(p, 'utf8'));
      return { ...defaults, ...user };
    }
  } catch {}
  return defaults;
}

function processForAutoSpeak(text, cfg) {
  if (!text) return '';
  let t = text;

  const skip = !!cfg.autoSpeakSkipCodeBlocks;
  if (skip) {
    t = t.replace(/```[\s\S]*?```/g, '');
    t = t.replace(/`([^`]+)`/g, '$1');
  } else {
    t = t.replace(/```[\s\S]*?```/g, '[code block]');
    t = t.replace(/`([^`]+)`/g, '$1');
  }

  // strip images/links
  t = t.replace(/!\[[^\]]*\]\([^)]*\)/g, '');
  t = t.replace(/\[[^\]]*\]\([^)]*\)/g, '$1');

  // normalize ws
  t = t.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();

  const maxC = Number(cfg.autoSpeakMaxChars || 1200);
  const mode = cfg.autoSpeakMode || 'full';

  if (t.length <= maxC) return t;

  if (mode === 'first-paragraph') {
    const parts = t.split(/\n\s*\n/);
    let cand = parts[0] || t;
    if (cand.length > maxC) cand = cand.slice(0, maxC).split(' ').slice(0, -1).join(' ') + '...';
    return cand.trim();
  } else if (mode === 'summary') {
    // naive sentences
    const sentences = t.split(/(?<=[.!?])\s+/);
    if (sentences.length <= 2) {
      return t.slice(0, maxC).trim();
    }
    const first = sentences[0];
    const last = sentences[sentences.length - 1];
    let s = (first + ' ... ' + last).trim();
    if (s.length > maxC) s = s.slice(0, maxC).split(' ').slice(0, -1).join(' ') + '...';
    return s;
  } else {
    // full capped
    return t.slice(0, maxC).split(' ').slice(0, -1).join(' ') + '...';
  }
}

function isMuted() {
  const v = (process.env.OUTLOUD_MUTE || '').toString().trim();
  return v === '1' || v.toLowerCase() === 'true';
}

function spawnDetachedSpeak(text) {
  // Reuse the SAME backend path used by /speak and hotkeys.
  // Prefer python speaker.py "text" (handles all engines + config).
  // Detached + unref so hook returns instantly (<1s).
  const dir = getVoiceDir();
  const pythonSpeaker = path.join(dir, '..', '..'); // not reliable; use repo relative via env or absolute from known
  // Simpler robust: use 'python' + scripts/speaker.py relative to plugin root if available, fallback to system python + speaker.py
  // But plugin root not passed; we use the installed-in-path convention + direct python call with full path guess.
  // Most reliable cross: shell out python -m with full path to speaker.py from known locations.

  // Strategy: try several locations for speaker.py, then spawn detached.
  const candidates = [
    // when running from repo root context
    path.join(__dirname, '..', 'scripts', 'speaker.py'),
    // common
    path.join(process.cwd(), 'scripts', 'speaker.py'),
  ];

  let speakerPy = null;
  for (const c of candidates) {
    try { if (fs.existsSync(c)) { speakerPy = c; break; } } catch {}
  }
  if (!speakerPy) {
    // last resort: rely on PATH python having it in cwd or user will have it working for manual too
    speakerPy = path.join(getVoiceDir(), '..', 'speaker.py'); // unlikely
  }

  // Build command: python "<speakerPy>" "<text>"
  const cmd = process.platform === 'win32' ? 'python' : 'python3';
  const args = speakerPy && fs.existsSync(speakerPy) ? [speakerPy, text] : ['-c', `import subprocess,sys;print("speaker backend not locatable")`];

  try {
    const child = spawn(cmd, args, {
      detached: true,
      stdio: 'ignore',
      windowsHide: true,
      shell: false,
    });
    child.unref();
  } catch (e) {
    // never throw from hook
  }
}

function cleanForSpeech(text) {
  if (!text) return '';
  // Remove code fences but keep a note so user knows
  let t = text.replace(/```[\s\S]*?```/g, '[code block]');
  // Remove images / links noise
  t = t.replace(/!\[[^\]]*\]\([^)]*\)/g, '');
  t = t.replace(/\[[^\]]*\]\([^)]*\)/g, '$1');
  // Collapse excessive whitespace/newlines
  t = t.replace(/\n{3,}/g, '\n\n').trim();
  // Truncate if insanely long for speech (user can re-trigger for parts)
  const MAX = 8000;
  if (t.length > MAX) t = t.slice(0, MAX) + ' ... [truncated for speech]';
  return t;
}

function extractLastAssistantFromTranscript(transcriptPath) {
  try {
    if (!transcriptPath || !fs.existsSync(transcriptPath)) return null;
    const lines = fs.readFileSync(transcriptPath, 'utf8').trim().split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i].trim();
      if (!line) continue;
      let evt;
      try { evt = JSON.parse(line); } catch { continue; }

      // Common shapes seen across versions
      if (evt.type === 'assistant' && evt.message && evt.message.content) {
        const parts = evt.message.content;
        const textParts = parts
          .filter(p => p && (p.type === 'text' || p.text) && (p.text || p.content))
          .map(p => p.text || p.content || '');
        const full = textParts.join('\n').trim();
        if (full) return full;
      }

      if (evt.message && evt.message.role === 'assistant' && Array.isArray(evt.message.content)) {
        const txt = evt.message.content.map(c => c.text || '').join('\n').trim();
        if (txt) return txt;
      }

      // Some transcripts wrap it as completion or result
      if (evt.result && typeof evt.result === 'string' && evt.result.length > 20) {
        return evt.result;
      }
    }
  } catch (e) {
    // silent fail, hook must not break session
  }
  return null;
}

function main() {
  let input = '';
  try {
    input = fs.readFileSync(0, 'utf8'); // stdin
  } catch {}

  let data = {};
  try { data = JSON.parse(input || '{}'); } catch {}

  let text = null;

  // Preferred direct payload if the runtime gives it
  if (data.last_assistant_message) {
    if (typeof data.last_assistant_message === 'string') text = data.last_assistant_message;
    else if (data.last_assistant_message.content) {
      text = (data.last_assistant_message.content || [])
        .map(c => c.text || c).join('\n');
    }
  }

  if (!text && data.transcript_path) {
    text = extractLastAssistantFromTranscript(data.transcript_path);
  }

  // Fallback: sometimes "completion" or "response"
  if (!text && data.completion) text = data.completion;
  if (!text && data.response) text = data.response;

  if (text) {
    const cleaned = cleanForSpeech(text);
    const target = getLastFile();
    fs.writeFileSync(target, cleaned, 'utf8');

    // === autoSpeak: NON-BLOCKING fire-and-forget ===
    // After save (so /speak last always has full), optionally speak a processed slice.
    // Hook must return <10s always. Playback is detached.
    if (!isMuted()) {
      const cfg = loadConfig();
      if (cfg.autoSpeak) {
        const toSpeak = processForAutoSpeak(cleaned, cfg);
        if (toSpeak && toSpeak.trim().length > 3) {
          // Spawn detached using exact same speaker backend as /speak + hotkey
          spawnDetachedSpeak(toSpeak);
        }
      }
    }
  }

  // Always exit 0 so we never block Claude Code
  process.exit(0);
}

main();
