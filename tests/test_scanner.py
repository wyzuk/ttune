"""Tests for media discovery and natural sorting."""

import os
import tempfile
from pathlib import Path

import pytest

from ttune.config import SUPPORTED_EXTENSIONS
from ttune.playlist.scanner import is_supported_file, natural_sort_key, scan_media


def test_natural_sort_key():
    items = ["track 10.mp3", "track 1.mp3", "track 2.mp3", "track 20.mp3"]
    sorted_items = sorted(items, key=natural_sort_key)
    assert sorted_items == ["track 1.mp3", "track 2.mp3", "track 10.mp3", "track 20.mp3"]


def test_is_supported_file():
    assert is_supported_file("song.mp3") is True
    assert is_supported_file("song.wav") is True
    assert is_supported_file("video.mp4") is True
    assert is_supported_file("track.flac") is True
    assert is_supported_file("clip.mkv") is True
    assert is_supported_file("song.opus") is True
    assert is_supported_file("text.txt") is False
    assert is_supported_file("image.png") is False


def test_scan_media_single_file():
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name

    try:
        results = scan_media(temp_path)
        assert len(results) == 1
        assert Path(results[0]).resolve() == Path(temp_path).resolve()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_scan_media_recursive_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        sub = dir_path / "subdir"
        sub.mkdir()

        # Create dummy media files
        (dir_path / "song1.mp3").touch()
        (dir_path / "song10.mp3").touch()
        (dir_path / "song2.wav").touch()
        (sub / "song3.flac").touch()
        (sub / "ignore.txt").touch()

        results = scan_media(str(dir_path))
        basenames = [os.path.basename(r) for r in results]

        assert "ignore.txt" not in basenames
        assert len(results) == 4
        # Check natural sorting
        assert basenames == ["song1.mp3", "song2.wav", "song3.flac", "song10.mp3"]
