#!/usr/bin/env node
/**
 * Stop hook for claude-code-voice speaker plugin.
 * Captures the last assistant response text and writes it to a well-known location
 * so that the speaker CLI / hotkey / /speak can play it on demand.
 *
 * Supports both:
 * - Direct "last_assistant_message" style (some versions)
 * - transcript_path jsonl (standard)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

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
    // Optional debug marker
    // console.error(`[speaker] saved ${cleaned.length} chars`);
  }

  // Always exit 0 so we never block Claude Code
  process.exit(0);
}

main();
