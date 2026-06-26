#!/usr/bin/env node
/**
 * Cross-platform thin wrapper for claude-speaker CLI.
 * On Windows: delegates to speak.ps1 using PowerShell (native TTS)
 * On other platforms: prints instructions or can be extended.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const args = process.argv.slice(2);
const repoRoot = path.resolve(__dirname, '..');

if (process.platform === 'win32') {
  const ps1 = path.join(repoRoot, 'scripts', 'speak.ps1');
  const psArgs = ['-ExecutionPolicy', 'Bypass', '-File', ps1, ...args];
  const result = spawnSync('powershell', psArgs, { stdio: 'inherit' });
  process.exit(result.status ?? 0);
} else {
  // Future: call a python or node TTS here. For now helpful message.
  console.log('🔊 claude-speaker on non-Windows:');
  console.log('The last response is saved at:');
  const voiceDir = path.join(os.homedir(), '.config', 'claude-code-voice');
  console.log(path.join(voiceDir, 'last-response.txt'));
  console.log('');
  console.log('Use your OS TTS on that file, e.g.:');
  console.log('  say "$(cat ~/.config/claude-code-voice/last-response.txt)"   # macOS');
  console.log('  espeak -f ~/.config/claude-code-voice/last-response.txt      # Linux');
  process.exit(0);
}
