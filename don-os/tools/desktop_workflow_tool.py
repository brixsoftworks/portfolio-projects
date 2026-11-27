"""
tools/desktop_workflow_tool.py

Everyday Desktop Workflow Tools.
Includes:
- System clipboard read/write (Wayland wl-copy/wl-paste with X11 fallback)
- Web page article reader & clean text extractor (BeautifulSoup)
- Media & Video downloader/inspector (yt-dlp)
"""

import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
def get_clipboard_text() -> str:
    """
    Read the current text content stored in the system clipboard.
    Supports Wayland (wl-paste) and X11 (xclip).
    
    Returns:
        The copied clipboard text or an error message if empty.
    """
    if shutil.which("wl-paste"):
        try:
            res = subprocess.run(["wl-paste", "--no-newline"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout:
                return res.stdout
        except Exception:
            pass

    if shutil.which("xclip"):
        try:
            res = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout:
                return res.stdout
        except Exception:
            pass

    return "Clipboard is currently empty or cannot be accessed."


@tool
def set_clipboard_text(text: str) -> str:
    """
    Copy a given text string into the system clipboard.
    Supports Wayland (wl-copy) and X11 (xclip).
    
    Args:
        text: The string content to copy to the clipboard.
        
    Returns:
        Confirmation status.
    """
    if not text:
        return "Error: Empty text provided."

    if shutil.which("wl-copy"):
        try:
            proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, text=True)
            proc.communicate(input=text, timeout=3)
            return f"Successfully copied {len(text)} characters to the system clipboard."
        except Exception as e:
            pass

    if shutil.which("xclip"):
        try:
            proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
            proc.communicate(input=text, timeout=3)
            return f"Successfully copied {len(text)} characters to the system clipboard (xclip)."
        except Exception as e:
            return f"Error copying to clipboard: {e}"

    return "Error: Neither wl-copy nor xclip is available on this system."


@tool
def read_web_page(url: str, max_chars: int = 5000) -> str:
    """
    Fetch and extract clean, readable text and article content from any web URL.
    Strips scripts, styles, navigations, and advertisements.
    
    Args:
        url: The web URL to read (e.g. documentation, blog post, news article).
        max_chars: Maximum characters of readable content to return (default: 5000).
        
    Returns:
        Page title and clean extracted body text.
    """
    target = url.strip()
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        req = urllib.request.Request(target, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")

        # Strip non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"

        # Find main article container or paragraphs
        article = soup.find("article") or soup.find("main") or soup.body
        if not article:
            return f"Title: {title}\nNo readable text could be extracted."

        # Extract text preserving paragraphs
        paragraphs = []
        for p in article.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            txt = p.get_text(separator=" ", strip=True)
            if txt and len(txt) > 20:
                paragraphs.append(txt)

        content = "\n\n".join(paragraphs)
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n[Truncated at {max_chars} characters...]"

        return f"=== {title} ===\nSource: {target}\n\n{content}"
    except Exception as e:
        return f"Error reading web page '{target}': {e}"


@tool
def get_media_info(url: str) -> str:
    """
    Inspect metadata for an online video or audio (YouTube, Vimeo, Twitter, etc.) without downloading.
    
    Args:
        url: Link to the media.
        
    Returns:
        Title, uploader, duration, view count, and available formats.
    """
    yt_bin = shutil.which("yt-dlp") or os.path.expanduser("~/.local/bin/yt-dlp")
    if not os.path.exists(yt_bin):
        return "Error: yt-dlp is not installed on this system."

    try:
        res = subprocess.run(
            [yt_bin, "--dump-single-json", "--no-warnings", "--no-playlist", url.strip()],
            capture_output=True,
            text=True,
            timeout=15
        )
        if res.returncode != 0:
            return f"Error inspecting media: {res.stderr.strip()}"

        data = json.loads(res.stdout)
        title = data.get("title", "Unknown")
        uploader = data.get("uploader", "Unknown")
        duration_sec = data.get("duration", 0)
        views = data.get("view_count", "N/A")
        mins, secs = divmod(duration_sec, 60)
        formatted_views = f"{views:,}" if isinstance(views, int) else str(views)

        return (
            f"Title: {title}\n"
            f"Channel / Creator: {uploader}\n"
            f"Duration: {mins}m {secs}s\n"
            f"Views: {formatted_views}\n"
            f"URL: {url.strip()}"
        )
    except Exception as e:
        return f"Error retrieving media metadata: {e}"


@tool
def download_media(url: str, audio_only: bool = False, output_dir: str = "") -> str:
    """
    Download video or audio from YouTube or other media sites using yt-dlp.
    
    Args:
        url: URL of the video or audio to download.
        audio_only: If True, extracts high quality MP3 audio. Defaults to False (MP4 video).
        output_dir: Custom download directory. Defaults to ~/Downloads or ~/Music.
        
    Returns:
        Status message with destination path.
    """
    yt_bin = shutil.which("yt-dlp") or os.path.expanduser("~/.local/bin/yt-dlp")
    if not os.path.exists(yt_bin):
        return "Error: yt-dlp is not installed."

    dest_folder = output_dir.strip() if output_dir.strip() else (
        os.path.expanduser("~/Music") if audio_only else os.path.expanduser("~/Downloads")
    )
    Path(dest_folder).mkdir(parents=True, exist_ok=True)

    cmd = [yt_bin, "--no-playlist", "--no-warnings"]
    if audio_only:
        cmd.extend(["-x", "--audio-format", "mp3", "-o", f"{dest_folder}/%(title)s.%(ext)s"])
    else:
        cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "-o", f"{dest_folder}/%(title)s.%(ext)s"])

    cmd.append(url.strip())

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0:
            return f"Successfully downloaded media to '{dest_folder}'."
        return f"Download failed: {res.stderr.strip() or res.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return f"Download started but taking longer than 2 minutes. Check '{dest_folder}'."
    except Exception as e:
        return f"Error during download: {e}"
