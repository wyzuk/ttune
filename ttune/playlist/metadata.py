"""Audio metadata extraction using mutagen and ffprobe with clean fallback handling."""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrackMetadata:
    path: str
    filename: str
    title: str
    artist: str
    album: str
    duration: float
    format_name: str = ""
    bitrate: Optional[int] = None
    sample_rate: int = 44100

    @property
    def duration_str(self) -> str:
        return format_duration(self.duration)


def format_duration(seconds: float) -> str:
    """Format duration in seconds into MM:SS or HH:MM:SS string."""
    if seconds is None or seconds < 0:
        return "00:00"
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def clean_filename(filename: str) -> str:
    """Clean common junk suffixes from media filenames."""
    base, _ = os.path.splitext(filename)
    patterns = [
        r"\(official\s*(?:music\s*)?video\)",
        r"\[official\s*(?:music\s*)?video\]",
        r"\(lyrics?\)",
        r"\[lyrics?\]",
        r"\(audio\)",
        r"\(getmp3\.pro\)",
        r"\[TubeRipper\.com\]",
        r"\(MP3_\d+K\)",
        r"\(M4A_\d+K\)",
        r"\(slowed\s*\+\s*reverb\)",
        r"\(bootleg\s*remix\)",
        r"\(remix\)",
    ]
    cleaned = base
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"^\d+[\s.-]+", "", cleaned)
    if "_" in cleaned and " " not in cleaned:
        cleaned = cleaned.replace("_", " ")

    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_")
    return cleaned if cleaned else base


def extract_metadata_mutagen(file_path: str) -> Optional[TrackMetadata]:
    """Attempt extraction using mutagen."""
    try:
        import mutagen

        f = mutagen.File(file_path, easy=True)
        if f is None:
            return None

        duration = getattr(f.info, "length", 0.0) if f.info else 0.0
        bitrate = getattr(f.info, "bitrate", None) if f.info else None
        sample_rate = getattr(f.info, "sample_rate", 44100) if f.info else 44100

        title = ""
        artist = ""
        album = ""

        if f.tags:
            title = f.tags.get("title", [""])[0] if "title" in f.tags else ""
            artist = f.tags.get("artist", [""])[0] if "artist" in f.tags else ""
            album = f.tags.get("album", [""])[0] if "album" in f.tags else ""

        _, ext = os.path.splitext(file_path)
        format_name = ext.lstrip(".").upper()

        filename = os.path.basename(file_path)
        cleaned = clean_filename(filename)

        if not title:
            if " - " in cleaned:
                parts = cleaned.split(" - ", 1)
                if not artist:
                    artist = parts[0].strip()
                title = parts[1].strip()
            else:
                title = cleaned

        if not artist:
            artist = "Unknown Artist"
        if not album:
            album = "Unknown Album"

        return TrackMetadata(
            path=file_path,
            filename=filename,
            title=title,
            artist=artist,
            album=album,
            duration=float(duration),
            format_name=format_name,
            bitrate=bitrate,
            sample_rate=sample_rate,
        )
    except Exception:
        return None


def extract_metadata_ffprobe(file_path: str) -> Optional[TrackMetadata]:
    """Attempt extraction using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode != 0:
            return None

        data = json.loads(res.stdout)
        fmt = data.get("format", {})
        tags = fmt.get("tags", {})
        lower_tags = {k.lower(): v for k, v in tags.items()}

        duration = float(fmt.get("duration", 0.0))
        bitrate = int(fmt.get("bit_rate", 0)) if fmt.get("bit_rate") else None

        sample_rate = 44100
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                sample_rate = int(stream.get("sample_rate", 44100))
                break

        title = lower_tags.get("title", "")
        artist = lower_tags.get("artist", "")
        album = lower_tags.get("album", "")

        filename = os.path.basename(file_path)
        cleaned = clean_filename(filename)

        if not title:
            if " - " in cleaned:
                parts = cleaned.split(" - ", 1)
                if not artist:
                    artist = parts[0].strip()
                title = parts[1].strip()
            else:
                title = cleaned

        if not artist:
            artist = "Unknown Artist"
        if not album:
            album = "Unknown Album"

        _, ext = os.path.splitext(file_path)
        format_name = ext.lstrip(".").upper()

        return TrackMetadata(
            path=file_path,
            filename=filename,
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            format_name=format_name,
            bitrate=bitrate,
            sample_rate=sample_rate,
        )
    except Exception:
        return None


def get_metadata(file_path: str) -> TrackMetadata:
    """Extract metadata for a file, with multi-tiered fallbacks so it never fails."""
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(file_path)

    meta = extract_metadata_mutagen(file_path)
    if meta and meta.duration > 0:
        return meta

    meta_ffprobe = extract_metadata_ffprobe(file_path)
    if meta_ffprobe:
        if meta and meta.title and meta.title != meta.filename:
            meta_ffprobe.title = meta.title
            meta_ffprobe.artist = meta.artist
            meta_ffprobe.album = meta.album
        return meta_ffprobe

    if meta:
        return meta

    cleaned = clean_filename(filename)
    artist = "Unknown Artist"
    title = cleaned
    if " - " in cleaned:
        parts = cleaned.split(" - ", 1)
        artist = parts[0].strip()
        title = parts[1].strip()

    return TrackMetadata(
        path=file_path,
        filename=filename,
        title=title,
        artist=artist,
        album="Unknown Album",
        duration=0.0,
        format_name=ext.lstrip(".").upper(),
        bitrate=None,
        sample_rate=44100,
    )
