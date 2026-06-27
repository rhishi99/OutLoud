---
description: Force setup check and instructions for OutLoud. Validates environment and prints "setup completed" if ready.
argument-hint: ""
---

You are running the dedicated OutLoud setup command.

**Always invoke using the full plugin path** (Claude Code will expand ${CLAUDE_PLUGIN_ROOT}):

- WSL / Linux / macOS (preferred):
  `bash "${CLAUDE_PLUGIN_ROOT}/speak.sh" --setup`

- Direct:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" --setup`

- Windows:
  `python "${CLAUDE_PLUGIN_ROOT}/scripts/speaker.py" --setup`

Instructions:
1. Immediately run the exact --setup command above using the full path.
2. Wait for the output.
3. If it prints "✅ OutLoud setup completed successfully!":
   - Tell the user setup is good.
   - Show the summary it printed.
   - Suggest trying `/speak last` or `/speak on`.
4. If it prints setup instructions or errors:
   - Copy the exact terminal commands it suggests (apt + pip).
   - Tell the user to run them in their terminal (WSL users must run inside WSL).
   - Ask them to run `/speaker:setup` again after.
5. Keep the response short and actionable. Do not invent extra steps.

Always use the full ${CLAUDE_PLUGIN_ROOT} form so it works from any project.

This command is designed to be run on first install and whenever the user wants to re-validate their environment.