#!/usr/bin/env python3
"""
claude-code-voice speaker.py

Configurable, natural-sounding TTS for Claude Code (and Grok Build) output.
"just a read out of claude code" — zero extra LLM tokens.

# Used from Grok/Claude Code plugin:
# - speak.cmd delegates to this when engine != native (for edge-tts etc.)
# - /speak command, hotkeys, and status line trigger speak via this or wrapper
# - Grok Build skills/grok-voice can invoke it directly for testing in this env

Supported engines (choose in config):
- edge-tts : Microsoft neural voices. Very natural. **DEFAULT**. Requires: pip install edge-tts
             (internet for audio, no API key, no cost for typical use)
- native   : OS built-in (SAPI / say / espeak). Zero deps. Fast fallback.
- pyttsx3  : Cross-platform native wrapper (better control).
- kokoro   : Fully local neural (excellent quality for size). EXPERIMENTAL and OPTIONAL.
             Requires heavy deps: pip install kokoro sounddevice numpy (+ espeak-ng)
             **Can (and should) be skipped** unless you specifically want fully offline neural.
             Not required for the plugin to work. Falls back cleanly if missing.

Usage (same as before):
  python scripts/speaker.py "Text to speak"
  python scripts/speaker.py --last
  python scripts/speaker.py -                    # read from stdin
  python scripts/speaker.py --engine edge-tts --voice en-US-AriaNeural "Hello"

The Stop hook only saves text. Speaking is always on-demand (hotkey / CLI / /speak).
No extra tokens are consumed by the LLM.

Config file (auto-created):
  Windows: %APPDATA%/claude-code-voice/config.json
  macOS/Linux: ~/.config/claude-code-voice/config.json

Example config:
{
  "engine": "edge-tts",        // edge-tts | native | pyttsx3 | kokoro
  "voice": "en-US-AriaNeural", // engine-specific voice id or name
  "rate": 1.0,                 // 0.5 - 2.0
  "volume": 1.0,
  "language": "en",
  "strip_code": true,
  "max_chars": 6500
}

# Bundling note (for plugin distribution or standalone exe):
#   python -m pip install pyinstaller
#   pyinstaller --onefile --name claude-speaker scripts/speaker.py
# Include playsound/edge-tts in the bundle (kokoro is large + ML-heavy, avoid unless needed).
# The resulting .exe can be referenced from speak.cmd or hotkeys instead of `python`.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------- Config ----------------

def get_config_dir() -> Path:
    if platform.system() == "Windows":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path.home() / ".config"
    return base / "claude-code-voice"

def get_config_path() -> Path:
    return get_config_dir() / "config.json"

def get_last_path() -> Path:
    return get_config_dir() / "last-response.txt"

DEFAULT_CONFIG = {
    "engine": "edge-tts",    # DEFAULT: natural Microsoft neural (pip install edge-tts). Kokoro is experimental/optional.
    "voice": "en-US-AriaNeural",
    "rate": 1.0,
    "volume": 1.0,
    "language": "en",
    "strip_code": True,
    "max_chars": 6500,
    "prefer_natural": True,  # unused hint
}

def load_config() -> dict:
    path = get_config_path()
    cfg = DEFAULT_CONFIG.copy()
    if path.exists():
        try:
            user_cfg = json.loads(path.read_text(encoding="utf-8"))
            cfg.update(user_cfg)
        except Exception:
            pass
    else:
        get_config_dir().mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg

def save_config(cfg: dict):
    get_config_dir().mkdir(parents=True, exist_ok=True)
    get_config_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get_speaker_script_path() -> Path:
    """Return absolute path to this speaker.py script.
    Simple helper for bundling (PyInstaller, Nuitka, plugin wrappers, speak.cmd updates).
    Example bundling:
        pyinstaller --onefile --name speaker --add-data "..." $(python -c 'from scripts.speaker import get_speaker_script_path; print(get_speaker_script_path())')
    Kokoro is too heavy for typical bundles; prefer edge-tts + playsound for bundled builds.
    """
    return Path(__file__).resolve()


# ---------------- Text cleaning ----------------

def clean_text(text: str, strip_code: bool = True) -> str:
    if not text:
        return ""
    t = text.strip()

    if strip_code:
        # Replace code blocks with a short note
        t = re.sub(r"```[\s\S]*?```", "[code block]", t)
        # Remove inline code backticks
        t = re.sub(r"`([^`]+)`", r"\1", t)

    # Remove image markdown and most links
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)

    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()

    cfg = load_config()
    maxc = cfg.get("max_chars", 6500)
    if len(t) > maxc:
        t = t[:maxc] + " ... [truncated]"

    return t

# ---------------- Engines ----------------

def speak_native(text: str, cfg: dict):
    """Use the fastest native OS speech. No extra packages."""
    system = platform.system()

    if system == "Windows":
        # Reuse the proven PowerShell path for zero Python dependency on Windows
        ps1 = Path(__file__).parent / "speak.ps1"
        if ps1.exists():
            cmd = [
                "powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps1),
                "-Text", text,
                "-Rate", str(int((cfg.get("rate", 1.0) - 1.0) * 10)),
                "-Volume", str(int(cfg.get("volume", 1.0) * 100))
            ]
            subprocess.run(cmd, check=False)
            return
        # Fallback
        try:
            import win32com.client  # type: ignore
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = int((cfg.get("rate", 1.0) - 1) * 5)
            speaker.Volume = int(cfg.get("volume", 1) * 100)
            speaker.Speak(text)
            return
        except Exception:
            pass

    elif system == "Darwin":  # macOS
        rate = int(180 * cfg.get("rate", 1.0))
        voice = cfg.get("voice") or ""
        cmd = ["say", "-r", str(rate)]
        if voice:
            cmd += ["-v", voice]
        cmd += [text]
        subprocess.run(cmd, check=False)
        return

    else:  # Linux and others
        rate = int(150 * cfg.get("rate", 1.0))
        for exe in ["espeak-ng", "espeak", "spd-say"]:
            if shutil.which(exe):
                if exe == "spd-say":
                    subprocess.run([exe, "-r", str(rate), text], check=False)
                else:
                    v = cfg.get("voice") or ""
                    cmd = [exe, "-s", str(rate), "-v", v or "en"] if v or exe.startswith("espeak") else [exe, text]
                    subprocess.run([exe, "-s", str(rate), text] if exe.startswith("espeak") else [exe, text], check=False)
                return
        print("[speaker] No native TTS found on Linux. Install espeak-ng or use --engine edge-tts / kokoro", file=sys.stderr)

def shutil_which(cmd):
    import shutil
    return shutil.which(cmd)

def speak_pyttsx3(text: str, cfg: dict):
    try:
        import pyttsx3
    except ImportError:
        print("pyttsx3 not installed. Run: pip install pyttsx3", file=sys.stderr)
        speak_native(text, cfg)
        return

    engine = pyttsx3.init()
    rate = int(180 * cfg.get("rate", 1.0))
    engine.setProperty("rate", rate)
    engine.setProperty("volume", cfg.get("volume", 1.0))

    voice = cfg.get("voice")
    if voice:
        for v in engine.getProperty("voices"):
            if voice.lower() in (v.name or "").lower() or voice in (v.id or ""):
                engine.setProperty("voice", v.id)
                break

    engine.say(text)
    engine.runAndWait()

def speak_edge_tts(text: str, cfg: dict):
    """High quality Microsoft neural voices. Very natural. Needs internet once.
    Primary playback: playsound (clean, no/minimal window) + guaranteed cleanup of temp mp3.
    """
    try:
        import asyncio
        import edge_tts
    except ImportError:
        print("[speaker] edge-tts not installed. Falling back to native. pip install edge-tts", file=sys.stderr)
        speak_native(text, cfg)
        return

    voice = cfg.get("voice") or "en-US-AriaNeural"
    rate = int((cfg.get("rate", 1.0) - 1.0) * 100)
    rate_str = f"+{rate}%" if rate >= 0 else f"{rate}%"

    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)

        audio_dir = get_config_dir()
        audio_path = str(audio_dir / "last-spoken.mp3")
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Remove old file if present
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
        except Exception:
            pass

        async def _run():
            await communicate.save(audio_path)
            system = platform.system()
            print("[speaker] Natural voice audio generated. Launching playback...")

            try:
                # === PRIMARY PATH: playsound for clean playback (recommended) ===
                # playsound is primary because it blocks cleanly without spawning
                # extra console/player windows on most platforms. Install: pip install playsound
                # Cleanup is guaranteed via finally below.
                played = False
                try:
                    from playsound import playsound
                    playsound(audio_path, block=True)
                    played = True
                    print("[speaker] Played cleanly via playsound (primary path for edge-tts)")
                except ImportError:
                    print("[speaker] playsound not installed (optional but recommended for clean playback)")
                except Exception as e:
                    print(f"[speaker] playsound failed ({e}), falling back to OS player...")

                if not played:
                    # Fallback OS players (secondary)
                    if system == "Windows":
                        # Launch minimized to avoid stealing focus / full window
                        subprocess.run(['cmd', '/c', 'start', '/min', '', audio_path], shell=True, check=False)
                    elif system == "Darwin":
                        subprocess.run(["afplay", audio_path], check=False)
                    else:
                        for player in ["mpg123", "ffplay", "aplay", "play"]:
                            if shutil.which(player):
                                if player == "ffplay":
                                    subprocess.run([player, "-nodisp", "-autoexit", audio_path], check=False)
                                else:
                                    subprocess.run([player, audio_path], check=False)
                                break
                        else:
                            print(f"[speaker] Audio saved to {audio_path} (no player found to auto-play)", file=sys.stderr)
            finally:
                # === ALWAYS CLEAN UP (playsound primary path + all fallbacks) ===
                # Uses finally so we *always* delete the temp mp3, even if playback raises.
                # Prevents leftover files, repeated player popups, and disk accumulation.
                try:
                    if os.path.exists(audio_path):
                        os.unlink(audio_path)
                        print("[speaker] Cleaned up temporary audio file.")
                except Exception:
                    # File may be briefly locked on Windows after playsound; ignore.
                    # Next speak will overwrite or clean on next successful run.
                    pass

        asyncio.run(_run())
    except Exception as e:
        print(f"[speaker] edge-tts failed: {e}. Falling back to native.", file=sys.stderr)
        speak_native(text, cfg)

def speak_kokoro(text: str, cfg: dict):
    """EXPERIMENTAL / OPTIONAL: Fully local neural TTS (Kokoro-82M).
    Natural sounding, offline. First run downloads ~327MB model (one time only).

    IMPORTANT: Kokoro is experimental. It can (and often should) be skipped.
    No need to install its deps unless you specifically want fully-offline neural.
    The plugin works great with the default edge-tts (or native fallback).
    If missing or broken, we cleanly fall back without erroring the user flow.
    """
    try:
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="torch")
        warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
        from kokoro import KPipeline
        import sounddevice as sd
        import numpy as np
    except ImportError:
        print("[speaker] Kokoro not fully installed (optional/experimental - can be skipped). pip install kokoro sounddevice numpy", file=sys.stderr)
        speak_native(text, cfg)
        return

    try:
        print("[speaker] Initializing Kokoro (may download ~327MB model on first use - one time only)...")
        print("[speaker] Tip: For faster downloads set HF_TOKEN env var (free HF account). English quality can vary - edge-tts often better for natural reading.")
        # Kokoro pipeline - explicit repo to avoid warning
        lang = cfg.get("language", "en")
        pipeline = KPipeline(lang_code=lang[0] if lang else "a", repo_id='hexgrad/Kokoro-82M')
        voice = cfg.get("voice") or "af_heart"

        audio = []
        for _, _, audio_chunk in pipeline(text, voice=voice, speed=cfg.get("rate", 1.0)):
            audio.append(audio_chunk)
        if not audio:
            return
        final = np.concatenate(audio, axis=0)
        sd.play(final, 24000)
        sd.wait()
        print("[speaker] Kokoro playback finished (direct audio, no media player).")
    except Exception as e:
        print(f"[speaker] kokoro failed: {e}. Falling back to native.", file=sys.stderr)
        speak_native(text, cfg)


# ---------------- Voice Listing ----------------

def list_edge_voices():
    """List Microsoft edge-tts voices (requires internet). Rich set of languages and English accents."""
    try:
        import asyncio
        import edge_tts

        async def _list():
            voices = await edge_tts.list_voices()
            print("Available edge-tts voices (ShortName, Locale, Gender):")
            for v in voices:
                short = v.get('ShortName', '')
                locale = v.get('Locale', '')
                gender = v.get('Gender', '')
                print(f"  {short} | {locale} | {gender}")
            print("\nTip: Great for different English accents (en-US, en-GB, en-AU, en-IN, en-CA...) and many languages.")

        asyncio.run(_list())
    except Exception as e:
        print(f"Could not list edge-tts voices: {e}. Make sure edge-tts is installed and you have internet.")


def list_pyttsx3_voices():
    """List voices available through pyttsx3 (usually your system's installed voices)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("Available pyttsx3 / system voices:")
        for v in engine.getProperty("voices"):
            langs = v.languages if hasattr(v, 'languages') else []
            print(f"  ID: {v.id}")
            print(f"    Name: {v.name}")
            print(f"    Languages: {langs}")
        print("\nTip: These are the voices installed on your OS. Install more via Windows Settings > Time & Language > Speech.")
    except Exception as e:
        print(f"Could not list pyttsx3 voices: {e}. Try 'pip install pyttsx3'.")


def list_kokoro_voices():
    """Known good voices for Kokoro (local neural). EXPERIMENTAL/OPTIONAL - skip unless needed."""
    print("Popular Kokoro voices (good quality, fully local) [EXPERIMENTAL - can be skipped]:")
    voices = [
        ("af_heart", "American Female, warm & expressive (default)"),
        ("af_nova", "American Female, clear & professional"),
        ("af_alloy", "American Female, smooth & neutral"),
        ("am_adam", "American Male, natural"),
        ("am_fenrir", "American Male, deep & strong"),
        ("am_onyx", "American Male, smooth & confident"),
        ("bm_george", "British Male, polished"),
        ("bf_emma", "British Female, clear"),
    ]
    for vid, desc in voices:
        print(f"  {vid} - {desc}")
    print("\nMore available in the Kokoro model. Use --voice <name> with engine=kokoro.")
    print("Note: Kokoro support is optional/experimental. Most users should stick with edge-tts.")


def list_native_voices_hint():
    print("Native voices:")
    print("  - Windows: Depends on installed SAPI voices. Go to Settings > Time & Language > Speech to add more.")
    print("  - Use engine=pyttsx3 for easier listing of installed ones.")
    print("  - macOS: 'say -v ?' in terminal to list.")
    print("  - Linux: espeak-ng --voices or similar.")

# ---------------- Main ----------------

ENGINES = {
    "native": speak_native,
    "pyttsx3": speak_pyttsx3,
    "edge-tts": speak_edge_tts,   # primary recommended natural engine (default)
    "kokoro": speak_kokoro,       # EXPERIMENTAL/OPTIONAL - can safely be skipped, not installed by default
}

def main():
    parser = argparse.ArgumentParser(description="Configurable speaker for Claude Code / Grok output")
    parser.add_argument("text", nargs="?", help="Text to speak (or use --last / - for stdin)")
    parser.add_argument("--last", action="store_true", help="Speak the last captured response")
    parser.add_argument("--engine", choices=list(ENGINES.keys()), help="Override engine")
    parser.add_argument("--voice", help="Override voice")
    parser.add_argument("--rate", type=float, help="Speed multiplier (0.5-2.0)")
    parser.add_argument("--volume", type=float, help="Volume 0-1")
    parser.add_argument("--config", action="store_true", help="Print current config and exit")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), action="append",
                        help="Set a config value (e.g. --set engine edge-tts)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices for the engine (edge-tts and pyttsx3 have many)")

    args = parser.parse_args()
    cfg = load_config()

    # Handle --list-voices (do this early)
    if args.list_voices:
        eng = args.engine or cfg.get("engine", "edge-tts")
        print(f"Listing voices for engine: {eng}\n")
        if eng == "edge-tts":
            list_edge_voices()
        elif eng == "pyttsx3":
            list_pyttsx3_voices()
        elif eng == "kokoro":
            list_kokoro_voices()
        else:
            list_native_voices_hint()
        return

    # Handle --set
    if args.set:
        for k, v in args.set:
            if v.lower() in ("true", "false"):
                v = v.lower() == "true"
            elif v.replace(".", "", 1).isdigit():
                v = float(v) if "." in v else int(v)
            cfg[k] = v
        save_config(cfg)
        print("Config updated:", json.dumps(cfg, indent=2))
        return

    if args.config:
        print(json.dumps(cfg, indent=2))
        return

    # Simple interactive console mode (great for local testing)
    if not args.text and not args.last and not args.set and len(sys.argv) == 1:
        print("\n🔊 claude-code-voice interactive configurator")
        print("Current:", json.dumps({k: cfg[k] for k in ['engine','voice','rate','volume']}, indent=2))
        print("\nOptions:")
        print("  1) Change engine")
        print("  2) Set voice")
        print("  3) Speak a test phrase")
        print("  4) Show full config")
        print("  5) Exit")
        choice = input("\nChoice [1-5]: ").strip()
        
        if choice == "1":
            print("Available:", list(ENGINES.keys()))
            eng = input("New engine: ").strip()
            if eng in ENGINES:
                cfg["engine"] = eng
                save_config(cfg)
                print("Engine set to", eng)
        elif choice == "2":
            v = input("Voice name: ").strip()
            cfg["voice"] = v or None
            save_config(cfg)
            print("Voice updated")
        elif choice == "3":
            phrase = input("Phrase to speak: ").strip() or "This is a test of the speaker plugin."
            # re-enter main logic with this text
            args.text = phrase
            # continue below
        elif choice == "4":
            print(json.dumps(cfg, indent=2))
            return
        else:
            return

    # Determine text
    text = None
    if args.last:
        last_file = get_last_path()
        if last_file.exists():
            text = last_file.read_text(encoding="utf-8")
    elif args.text == "-" or (not args.text and not sys.stdin.isatty()):
        text = sys.stdin.read()
    elif args.text:
        text = args.text

    if not text:
        print("No text. Use: python speaker.py 'hello'  or  --last  or  echo 'hi' | python speaker.py -", file=sys.stderr)
        sys.exit(1)

    # Apply overrides
    if args.engine:
        cfg["engine"] = args.engine
    if args.voice:
        cfg["voice"] = args.voice
    if args.rate is not None:
        cfg["rate"] = args.rate
    if args.volume is not None:
        cfg["volume"] = args.volume

    cleaned = clean_text(text, cfg.get("strip_code", True))

    engine_name = cfg.get("engine", "edge-tts")
    engine_fn = ENGINES.get(engine_name, speak_native)

    print(f"[speaker] engine={engine_name} voice={cfg.get('voice') or 'default'} rate={cfg.get('rate')}")
    engine_fn(cleaned, cfg)

if __name__ == "__main__":
    main()
