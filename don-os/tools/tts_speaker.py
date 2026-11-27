"""
tools/tts_speaker.py

Ultra-low latency speech synthesis engine using edge-tts (natural neural voice).
Includes thorough Markdown cleaning (strips asterisks, bullets, hashtags, and formatting artifacts)
and direct streaming to audio players for instant sub-second playback.
"""

import asyncio
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Optional, List
import edge_tts

# Default voice: Mature ~25yo female voice (warm, natural, expressive, composed)
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-AvaNeural")
DEFAULT_RATE = os.getenv("TTS_RATE", "+5%")
DEFAULT_PITCH = os.getenv("TTS_PITCH", "+0Hz")

# Active audio playback process tracking for instant interruption
_active_proc_lock = threading.Lock()
_active_proc: Optional[subprocess.Popen] = None
_speech_active = False
_speech_generation = 0
_last_speech_end_time = 0.0
_recent_spoken_texts: List[str] = []


def is_speech_active() -> bool:
    with _active_proc_lock:
        return _speech_active


def get_speech_status() -> dict:
    with _active_proc_lock:
        now = time.time()
        cooldown = (now - _last_speech_end_time) < 1.0
        return {
            "speaking": _speech_active,
            "cooldown": cooldown,
            "active_or_cooldown": _speech_active or cooldown,
            "recent_texts": list(_recent_spoken_texts[-5:])
        }


def stop_current_speech():
    """Immediately terminates ongoing speech playback and invalidates its generation."""
    global _active_proc, _speech_active, _speech_generation, _last_speech_end_time
    with _active_proc_lock:
        _speech_generation += 1
        _speech_active = False
        _last_speech_end_time = time.time()
        if _active_proc and _active_proc.poll() is None:
            try:
                _active_proc.terminate()
                _active_proc.kill()
            except Exception:
                pass
            _active_proc = None


def clean_speech_text(text: str, max_chars: Optional[int] = None) -> str:
    """
    Cleans raw markdown and symbols so edge-tts speaks natural human language
    without pronouncing asterisks ('askus'), bullet dots, markdown headers, or URLs.
    Set max_chars only when intentionally limiting the spoken text.
    """
    if not text:
        return ""

    # 1. Keep code block content but remove its Markdown fence and language label
    t = re.sub(r'```[^\n`]*\n?([\s\S]*?)```', r'\1', text)
    # 2. Strip inline code backticks
    t = re.sub(r'`([^`]+)`', r'\1', t)
    # 3. Strip markdown links [title](url) -> title
    t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
    # 4. Strip raw URLs
    t = re.sub(r'https?://\S+', '', t)
    # 5. Strip markdown headers (e.g. ### Header)
    t = re.sub(r'#+\s*', '', t)
    # 6. Strip bold and italics asterisks and underscores
    t = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', t)
    t = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', t)
    # 7. Strip list bullets (*, -, +, •, ·)
    t = re.sub(r'(^|\n)\s*[-*+•·–—]\s+', r'\1', t)
    # 8. Strip formatting symbols (asterisks, hashtags, tildes, pipes, brackets, angle brackets)
    t = re.sub(r'[*~_#|><`]', ' ', t)
    # 9. Natural spoken conversions
    t = re.sub(r'°C\b', ' degrees Celsius', t)
    t = re.sub(r'°F\b', ' degrees Fahrenheit', t)
    t = re.sub(r'%', ' percent', t)
    t = re.sub(r'&', ' and ', t)
    t = re.sub(r'\be\.g\.,?', 'for example,', t)
    t = re.sub(r'\bi\.e\.,?', 'that is,', t)
    # 10. Collapse multiple dots / ellipses
    t = re.sub(r'\.{2,}', '.', t)
    # 11. Normalize spaces
    t = re.sub(r'\s+', ' ', t).strip()

    # 12. Smart sentence truncation: take first 1-2 natural sentences for crisp conversational response
    if max_chars is not None and max_chars > 0 and len(t) > max_chars:
        sentences = re.split(r'(?<=[.!?])\s+', t)
        spoken = ""
        for s in sentences:
            if not spoken:
                spoken = s
            elif len(spoken) + len(s) + 1 <= max_chars:
                spoken = f"{spoken} {s}"
            else:
                break
        t = spoken if spoken else t[:max_chars].rsplit(' ', 1)[0] + "."

    return t


async def _stream_audio_to_player(
    cleaned_text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH
):
    """Streams audio chunks directly into mpv via stdin for zero-delay playback."""
    global _active_proc

    # Prefer streaming with mpv if installed
    if shutil.which("mpv"):
        player_cmd = ["mpv", "--no-video", "--really-quiet", "-"]
        proc = subprocess.Popen(player_cmd, stdin=subprocess.PIPE)
        with _active_proc_lock:
            _active_proc = proc

        comm = edge_tts.Communicate(cleaned_text, voice, rate=rate, pitch=pitch)
        try:
            async for chunk in comm.stream():
                if chunk['type'] == 'audio':
                    try:
                        proc.stdin.write(chunk['data'])
                        proc.stdin.flush()
                    except (BrokenPipeError, OSError):
                        break
        except Exception as e:
            print(f"[TTS Stream Error]: {e}")
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass
            proc.wait()
            with _active_proc_lock:
                if _active_proc is proc:
                    _active_proc = None
        return

    # Fallback to file-based playback if mpv is not available
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        comm = edge_tts.Communicate(cleaned_text, voice, rate=rate, pitch=pitch)
        await comm.save(tmp_path)

        if shutil.which("pw-play"):
            cmd = ["pw-play", tmp_path]
        elif shutil.which("paplay"):
            cmd = ["paplay", tmp_path]
        elif shutil.which("ffplay"):
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path]
        else:
            cmd = ["aplay", tmp_path]

        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with _active_proc_lock:
            _active_proc = proc
        proc.wait()
        with _active_proc_lock:
            if _active_proc is proc:
                _active_proc = None
    except Exception as e:
        print(f"[TTS Fallback Error]: {e}")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def speak_text(
    text: str,
    voice: str = DEFAULT_VOICE,
    max_chars: Optional[int] = None,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH
):
    """
    Speaks out text directly through the laptop speakers using PipeWire/mpv streaming.
    Interrupts any ongoing speech and cleans all markdown symbols.
    """
    global _speech_active, _speech_generation

    # 1. Interrupt any active speech immediately to prevent delay / backlog
    stop_current_speech()

    # 2. Clean markdown symbols (asterisks, bullets, headers, links)
    clean = clean_speech_text(text, max_chars=max_chars)
    if not clean:
        return

    with _active_proc_lock:
        _speech_generation += 1
        generation = _speech_generation
        _speech_active = True
        _recent_spoken_texts.append(clean.strip().lower())
        if len(_recent_spoken_texts) > 10:
            _recent_spoken_texts.pop(0)

    print(f"\n[TTS Ava (~25yo)]: {clean}\n")

    try:
        asyncio.run(_stream_audio_to_player(clean, voice, rate, pitch))
    except Exception as e:
        print(f"[TTS Error]: {e}")
    finally:
        with _active_proc_lock:
            if generation == _speech_generation:
                _speech_active = False
                _last_speech_end_time = time.time()


# Synchronous convenience alias
speak_text_sync = speak_text


if __name__ == "__main__":
    speak_text("Right away, Boss Munna! Testing the ultra-low latency streaming voice engine.")
